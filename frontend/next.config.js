/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  // Cloudflare Pages (next-on-pages) ではstandalone不可 → CF_PAGES未設定時のみstandalone
  ...(process.env.CF_PAGES ? {} : { output: 'standalone' }),
  poweredByHeader: false,
  compress: true,
  reactStrictMode: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    // [핵심] Next.js 16 Turbopack 에러 해결을 위해 빈 객체라도 명시해야 합니다.
    turbopack: {},
    optimizeCss: true,
    scrollRestoration: true,
    optimizePackageImports: ['@mantine/core', '@mantine/hooks']
  },
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5001',
        pathname: '/api/nine-star/static/**',
      },
      {
        // Cloud Run 백엔드 이미지 URL 허용 (프로덕션)
        protocol: 'https',
        hostname: '*.run.app',
        pathname: '/api/nine-star/static/**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    // 경로 별칭(Alias) 설정
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };

    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        child_process: false,
      };
    }

    return config;
  },
  // [중요] Cloudflare Pages / Cloud Run 배포 시
  // API 경로는 NEXT_PUBLIC_API_URL 환경변수로 직접 지정합니다.
  // 로컬 개발 시에는 NEXT_PUBLIC_API_URL 미설정 → localhost:5001 폴백을 사용하세요.
  // (docker-compose 환경에서는 아래 rewrites가 자동으로 적용됩니다)
  ...(process.env.NODE_ENV !== 'production' && {
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: 'http://backend:5001/api/:path*'
        }
      ]
    }
  })
}

module.exports = nextConfig;