"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Container, Loader } from '@mantine/core';
import { NineStarKiForm } from '@/components/features/form';
import { useAuth } from '@/contexts/auth/AuthContext';
import { useNineStarKiStore } from '@/stores/nineStarKiStore';

export default function Home() {
  const { token, isLoading } = useAuth();
  const router = useRouter();
  const nineStarKiResult = useNineStarKiStore((state) => state.result);

  useEffect(() => {
    if (!isLoading && !token) {
      router.replace('/login');
    }
  }, [isLoading, token, router]);

  // ページロード時に九星気学ストアの状態をリセット
  useEffect(() => {
    // ストアに結果がある場合、ホームページに来たらリセット
    if (nineStarKiResult) {
      console.log('ホームページで九星気学ストアをリセットします');
      useNineStarKiStore.getState().reset();
      // セッションストレージも削除
      sessionStorage.removeItem('ninestarki_data');
    }
  }, [nineStarKiResult]);

  if (isLoading) {
    return (
      <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Loader />
      </Container>
    );
  }

  if (!token) {
    return null;
  }

  return (
    <main>
      <Container 
        size="lg" 
        py="xl"
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-start',
          paddingTop: 'calc(20vh)',
          minHeight: '100vh',
        }}
      >
        <NineStarKiForm token={token} />
      </Container>
    </main>
  );
}
