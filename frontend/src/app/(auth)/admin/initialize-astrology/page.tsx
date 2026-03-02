'use client';

import React, { useState, useEffect } from 'react';
import { Container, Title, Box, Button, Code, Paper } from '@mantine/core';
import ManageDailyAstrology from '@/components/admin/ManageDailyAstrology';
import { IconArrowLeft } from '@tabler/icons-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth/AuthContext';

export default function InitializeDailyAstrologyPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [tokenInfo, setTokenInfo] = useState<string>('');

  useEffect(() => {
    // トークン情報を取得
    const storedToken = localStorage.getItem('token');
    setTokenInfo(`
      Context Token: ${token ? '存在します' : 'ありません'}
      LocalStorage Token: ${storedToken ? '存在します' : 'ありません'}
      認証状態: ${token ? '認証済み' : '未認証'}
    `);
  }, [token]);

  // API接続をテストする関数
  const testApiConnection = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`API接続成功: ${JSON.stringify(data)}`);
      } else {
        alert(`APIエラー: ステータス ${response.status}`);
      }
    } catch (error) {
      alert(`API接続テストエラー: ${error}`);
    }
  };

  return (
    <Container size="lg" py="xl">
      <Box mb="lg">
        <Button 
          variant="subtle" 
          leftSection={<IconArrowLeft size={16} />}
          onClick={() => router.push('/admin')}
        >
          管理画面に戻る
        </Button>
      </Box>
      
      <Title order={2} mb="xl">干支・九星データ初期化</Title>
      
      {/* デバッグ情報 */}
      <Paper withBorder p="md" mb="xl">
        <Title order={4} mb="sm">デバッグ情報</Title>
        <Code block>{tokenInfo}</Code>
        <Button onClick={testApiConnection} mt="sm">API接続テスト</Button>
      </Paper>
      
      <ManageDailyAstrology />
    </Container>
  );
} 