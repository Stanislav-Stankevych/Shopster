/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**"
      }
    ]
  },
  env: {
    NEXT_PUBLIC_APP_BUILD: process.env.NEXT_PUBLIC_APP_BUILD ?? "dev"
  }
};

export default nextConfig;
