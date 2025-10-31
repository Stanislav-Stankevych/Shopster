/** @type {import('next').NextConfig} */
const DEV_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://172.25.96.1:3000",
];

const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "172.25.96.1",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
  env: {
    NEXT_PUBLIC_APP_BUILD: process.env.NEXT_PUBLIC_APP_BUILD ?? "dev",
  },
  experimental: {
    serverActions: {
      allowedOrigins: DEV_ALLOWED_ORIGINS,
    },
  },
};

export default nextConfig;
