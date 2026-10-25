/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/profile',
        destination: '/career-profile',
        permanent: true,
      },
      {
        source: '/readiness',
        destination: '/career-readiness',
        permanent: true,
      },
    ];
  },
  async rewrites() {
    // When BACKEND_INTERNAL_URL is configured (e.g. in Vercel or local reverse proxy),
    // proxy /api/v1/:path* requests to the FastAPI backend.
    // This guarantees same-origin cookie delivery, avoids browser third-party cookie blocking,
    // and ensures Next.js Edge Middleware receives session cookies reliably.
    const backendUrl =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL;

    if (!backendUrl) {
      return [];
    }

    const cleanBackendUrl = backendUrl.replace(/\/+$/, '');
    return [
      {
        source: '/api/v1/:path*',
        destination: `${cleanBackendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
