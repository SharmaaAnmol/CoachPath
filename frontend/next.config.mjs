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
};

export default nextConfig;
