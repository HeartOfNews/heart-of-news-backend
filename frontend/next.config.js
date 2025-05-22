/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['api.heartofnews.com', 'api-staging.heartofnews.com', 'localhost'],
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig