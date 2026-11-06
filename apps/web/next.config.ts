import type { NextConfig } from "next";

const API_ORIGIN = process.env.API_ORIGIN || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${API_ORIGIN}/api/v1/:path*`,
      },
      {
        source: "/healthz",
        destination: `${API_ORIGIN}/healthz`,
      },
    ];
  },
};

export default nextConfig;
