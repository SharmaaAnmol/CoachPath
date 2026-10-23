/**
 * CoachPath HTTP API Client.
 * Communicates with the FastAPI backend (/api/v1) adhering to RFC 7807 error conventions.
 */

export interface ApiErrorDetail {
  field?: string;
  issue: string;
}

export interface ApiErrorPayload {
  code: string;
  message: string;
  status: number;
  details?: ApiErrorDetail[];
  request_id?: string;
}

export class ApiClientError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly details?: ApiErrorDetail[];
  public readonly requestId?: string;

  constructor(payload: ApiErrorPayload) {
    super(payload.message);
    this.name = 'ApiClientError';
    this.code = payload.code;
    this.status = payload.status;
    this.details = payload.details;
    this.requestId = payload.request_id;
  }
}

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl =
      baseUrl ||
      process.env.NEXT_PUBLIC_API_URL ||
      'http://localhost:8000/api/v1';
  }

  private generateRequestId(): string {
    return `req_${Math.random().toString(36).substring(2, 10)}${Date.now().toString(36)}`;
  }

  public async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, headers, ...rest } = options;

    let url = `${this.baseUrl.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;

    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const isFormData = typeof FormData !== 'undefined' && rest.body instanceof FormData;

    const requestHeaders: Record<string, string> = {
      Accept: 'application/json',
      'X-Request-ID': this.generateRequestId(),
      ...((headers as Record<string, string>) || {}),
    };

    if (!isFormData && !requestHeaders['Content-Type']) {
      requestHeaders['Content-Type'] = 'application/json';
    }

    let response: Response;
    try {
      response = await fetch(url, {
        credentials: 'include',
        ...rest,
        headers: requestHeaders,
      });
    } catch (networkError: unknown) {
      throw new ApiClientError({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to CoachPath backend server. Please verify your connection.',
        status: 0,
      });
    }

    if (!response.ok) {
      let errorPayload: ApiErrorPayload;
      try {
        const body = await response.json();
        errorPayload = body.error || {
          code: 'HTTP_ERROR',
          message: response.statusText || 'An unexpected HTTP error occurred.',
          status: response.status,
          request_id: response.headers.get('X-Request-ID') || undefined,
        };
      } catch {
        errorPayload = {
          code: 'HTTP_ERROR',
          message: response.statusText || 'An unexpected HTTP error occurred.',
          status: response.status,
          request_id: response.headers.get('X-Request-ID') || undefined,
        };
      }
      throw new ApiClientError(errorPayload);
    }

    // Return empty object for 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json() as Promise<T>;
  }

  public get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public patch<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  public postMultipart<T>(endpoint: string, formData: FormData, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
    });
  }

  public async downloadBlob(endpoint: string, options?: RequestOptions): Promise<{ blob: Blob; filename?: string }> {
    const { params, headers, ...rest } = options || {};
    let url = `${this.baseUrl.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;

    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const response = await fetch(url, {
      credentials: 'include',
      ...rest,
      headers: {
        'X-Request-ID': this.generateRequestId(),
        ...((headers as Record<string, string>) || {}),
      },
    });

    if (!response.ok) {
      throw new ApiClientError({
        code: 'DOWNLOAD_FAILED',
        message: response.statusText || 'Download failed.',
        status: response.status,
      });
    }

    const disposition = response.headers.get('Content-Disposition');
    let filename: string | undefined;
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename="?([^";]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    const blob = await response.blob();
    return { blob, filename };
  }

  /**
   * Health and readiness checks
   */
  public async checkHealth(): Promise<{ status: string; service: string; version: string }> {
    return this.get<{ status: string; service: string; version: string }>('/health');
  }

  public async checkReadiness(): Promise<{ status: string; database: string }> {
    return this.get<{ status: string; database: string }>('/ready');
  }
}

export const apiClient = new ApiClient();
