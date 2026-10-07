# CoachPath Frontend Authentication Architecture

**Document Version**: 1.0.0  
**Phase**: Phase 3B — Frontend Authentication Integration  
**Framework**: Next.js 14 (App Router) + React 18 + TypeScript  
**Backend Target**: FastAPI / SQLAlchemy 2.x (`/api/v1/auth`)  

---

## 1. Architecture Overview

CoachPath connects a modern Next.js 14 App Router frontend to a secure FastAPI backend. In strict alignment with `/docs/security-and-privacy.md` and `/docs/authentication-architecture.md`, the platform adheres to a zero-trust credential model:

1. **HttpOnly Cookie Storage**: JWT access tokens and opaque refresh tokens are managed exclusively through secure `HttpOnly`, `SameSite=Lax` cookies set by the FastAPI backend. Sensitive tokens are **never** stored in browser `localStorage` or `sessionStorage`, eliminating XSS token theft vectors.
2. **Centralized Client Layer**: UI components never initiate raw `fetch` calls to authentication endpoints. All authentication operations pass through `ApiClient` and `AuthClient` abstractions.
3. **Reactive State via React Context**: Authentication state (`loading`, `authenticated`, `unauthenticated`, `error`) is globally accessible via `useAuth()`.
4. **Two-Tier Route Protection**: Edge Middleware (`middleware.ts`) and Client Guard (`(app)/layout.tsx`) collaborate to eliminate flash-of-unauthenticated-content (FOUC).

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser / Client                      │
│                                                             │
│   ┌───────────────────────────┐   ┌─────────────────────┐   │
│   │    Public Pages / Auth    │   │  Protected App Area │   │
│   │   (/, /login, /signup)    │   │ (/dashboard, etc.)  │   │
│   └─────────────┬─────────────┘   └──────────┬──────────┘   │
│                 │                            │              │
│                 ▼                            ▼              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │       useAuth() Hook  ◄──►  AuthProvider            │   │
│   │ (status: loading | authenticated | unauthenticated) │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │                              │
│                              ▼                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           AuthClient (register, login, etc.)        │   │
│   │                          │                              │
│   │           ApiClient (credentials: 'include')        │   │
│   └──────────────────────────┬──────────────────────────┘   │
└──────────────────────────────┼──────────────────────────────┘
                               │ HTTP / JSON (HttpOnly Cookies)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                /api/v1/auth Master Router                   │
│   (/register, /login, /refresh, /logout, /me)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Abstractions

### 2.1 HTTP Client (`frontend/src/lib/api-client.ts`)
- **Credentials by Default**: Sends `credentials: 'include'` on every request so the browser automatically delivers and saves session cookies across ports/origins.
- **RFC 7807 Error Normalization**: Extracts structured error objects (`error.code`, `error.message`, `error.details`, `error.status`, `request_id`).
- **Network Resilience**: Traps low-level fetch `TypeError` network drops and converts them into normalized `ApiClientError` with `code: 'NETWORK_ERROR'`.

### 2.2 Authentication Client (`frontend/src/lib/auth-client.ts`)
Encapsulates all 5 core authentication operations:

| Method | HTTP Endpoint | Description |
| :--- | :--- | :--- |
| `register(payload)` | `POST /api/v1/auth/register` | Creates candidate account (`201 Created`). |
| `login(payload)` | `POST /api/v1/auth/login` | Authenticates credentials, establishes cookies (`200 OK`). |
| `logout()` | `POST /api/v1/auth/logout` | Revokes server session and clears cookies (`200 OK`). |
| `getCurrentUser()` | `GET /api/v1/auth/me` | Fetches authenticated user identity & profile (`200 OK`). |
| `refreshToken()` | `POST /api/v1/auth/refresh` | Rotates refresh token and issues new access token (`200 OK`). |

### 2.3 Global Auth State Provider (`frontend/src/providers/auth-provider.tsx`)
Exposes state and operations via React Context:
- **State Model**:
  - `status`: `'loading' | 'authenticated' | 'unauthenticated'`
  - `user`: `AuthUser | null` (`{ id, email, role, status, full_name, created_at }`)
  - `error`: `string | null`
  - `isLoading`: `boolean`
  - `isAuthenticated`: `boolean`
- **Actions**:
  - `login(credentials)`
  - `register(payload)`
  - `logout()`
  - `refreshUser()`
  - `clearError()`

---

## 3. Route Protection & Flash Prevention

Route protection is implemented across two synchronized defensive layers:

### 3.1 Edge Middleware (`frontend/src/middleware.ts`)
- Runs at the edge before request execution.
- Checks for presence of `access_token` or `refresh_token` session cookies.
- **Unauthenticated Traffic**: If a visitor attempts to access any route starting with a protected prefix, they are redirected to `/login?redirect=${encodeURIComponent(pathname)}`.
- **Authenticated Traffic**: If an authenticated user navigates to `/login` or `/signup`, they are redirected to `/dashboard`.
- **Public & Asset Bypass**: Public routes (`/`, `/about`, `/features`, `/how-it-works`, `/privacy`) and static assets (`_next`, images) pass through unaffected.

### 3.2 Client-Side AuthGuard (`frontend/src/app/(app)/layout.tsx`)
- Guards against expired or revoked tokens where a cookie might exist but session validation fails on the backend.
- During initial session verification (`isLoading || status === 'loading'`), renders a branded, elegant loading shell preventing content flashes.
- If `/api/v1/auth/me` returns 401, updates status to `'unauthenticated'` and redirects to `/login`.

### Protected Routes Directory
- `/dashboard`
- `/career-profile` (and `/profile`)
- `/skills`
- `/assessments`
- `/roadmap`
- `/jobs`
- `/resume`
- `/applications`
- `/recruiters`
- `/interviews`
- `/career-readiness` (and `/readiness`)
- `/settings`

---

## 4. User Experience & Flows

### 4.1 Login UX (`/login`)
- **Query Parameter Handling**:
  - `redirect`: Preserves destination path for post-login return.
  - `registered=true`: Renders a success alert banner confirming account readiness.
- **Graceful Error Handling**:
  - 401: *"Invalid email or password. Please verify your credentials."*
  - 429: *"Too many failed login attempts. Please wait 15 minutes before trying again."*
  - 403: *"This account has been suspended. Please contact support."*
  - Network Error: *"Unable to connect to CoachPath backend. Please verify the service is running."*
- **Form Controls**:
  - Loading spinner on submit button.
  - Disabled inputs while request is in flight.
  - Demo candidate auto-fill button for rapid evaluation.

### 4.2 Signup UX (`/signup`)
- **Live Password Complexity Checklist**:
  - Validates length ($\ge 8$), uppercase, lowercase, digit, and special characters before submission.
- **Seamless Session Transition**:
  - Upon successful registration, automatically establishes an authenticated session (`POST /login`) and navigates directly to `/dashboard`.
  - Fallback: If immediate login fails, redirects to `/login?registered=true&email=...`.
- **Error States**:
  - 409 Conflict: Inline alert indicating an account with that email already exists.
  - 422 Validation: Surfaces exact schema violation details.

### 4.3 Sign Out Flow
- Topbar user dropdown provides a functional **Sign Out** button.
- Invokes `authClient.logout()`, clearing the session on the FastAPI backend and resetting local state.
- Gracefully redirects to `/login`.

---

## 5. Quality Assurance & Verification

- **TypeScript Compilation**: `npx tsc --noEmit` passed with 0 errors.
- **ESLint**: `next lint` passed with 0 warnings and 0 errors.
- **Production Build**: `npm run build` compiled all 24 pages statically with Suspense boundaries and edge middleware.
- **Backend Test Suite**: `pytest backend/tests -v` passed all 52 automated tests.
