'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';
import { useRouter } from 'next/navigation';
import { LoadingOverlay } from '@mantine/core';

export default function PasswordChangeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoggedIn, isLoading } = useAuth();
  const router = useRouter();

  // 未ログインユーザーをリダイレクト
  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
      router.replace('/login');
    }
  }, [isLoggedIn, isLoading, router]);

  if (isLoading) {
    return (
      <div style={{ position: 'relative', height: '100vh' }}>
        <LoadingOverlay 
          visible={true} 
          zIndex={1000}
          overlayProps={{ blur: 2 }}
          loaderProps={{ color: '#4BA3E3', size: 'xl' }}
        />
      </div>
    );
  }

  return (
    <div className="password-change-layout">
      {children}
    </div>
  );
} 