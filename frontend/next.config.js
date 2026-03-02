/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  output: 'standalone', // [성능] 960MB RAM 환경에서 필수 설정
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
    // [보안/경고 해결] 'domains'는 폐지 예정이므로 'remotePatterns'로 통합합니다.
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5001',
        pathname: '/api/nine-star/static/**',
      },
      // 필요하다면 여기에 다른 허용 도메인을 추가하세요.
    ],
  },
  webpack: (config, { isServer }) => {
    // 경로 별칭(Alias) 설정
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };

    // RCE 취약점 및 보안 강화를 위한 브라우저 측 모듈 차단
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
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:5001/api/:path*' // 백엔드 경로 포함
      }
    ]
  }
}

module.exports = nextConfig;