import type { NextConfig } from "next";

const host: string = process.env.API_HOST || 'localhost';
const nextConfig: NextConfig = {
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  output: 'standalone',
  async rewrites() {
    return [
      { source: '/api/:path*', destination: `http://${host}:8000/api/:path*` },
    ];
  },
};

export default nextConfig;
