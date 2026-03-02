"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { PasswordInput, Button, Paper, Title, Container, Stack, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import api from '@/utils/api';
import { AxiosError } from 'axios';

export default function PasswordChangePage() {
  const router = useRouter();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (loading) {
      return;
    }

    // 入力検証
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("すべての項目を入力してください");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("新しいパスワードと確認用パスワードが一致しません");
      return;
    }

    // パスワードの強度チェック
    if (newPassword.length < 8) {
      setError("パスワードは8文字以上である必要があります");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      
      // 成功時の処理
      notifications.show({
        title: '成功',
        message: 'パスワードが正常に変更されました',
        color: 'green',
      });
      
      // フォームをリセット
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      
      // 少し待ってからホームページに戻る
      setTimeout(() => {
        router.push('/');
      }, 2000);
      
    } catch (error: unknown) {
      console.error('Password change error:', error);
      
      if (error instanceof AxiosError && error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('パスワード変更に失敗しました。入力内容を確認してください。');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size="xs" py="xl">
      <Paper 
        shadow="md" 
        p="xl" 
        radius="md"
        style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(75, 163, 227, 0.1)'
        }}
      >
        <Title order={1} ta="center" mb="lg" c="#4BA3E3">
          パスワード変更
        </Title>

        <form onSubmit={handlePasswordChange} noValidate>
          <Stack>
            {error && (
              <Text color="red" mb="md" ta="center">
                {error}
              </Text>
            )}

            <PasswordInput
              label="現在のパスワード"
              placeholder="現在のパスワードを入力"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              disabled={loading}
              styles={{
                label: {
                  color: '#4a5568'
                },
                input: {
                  '&:focus': {
                    borderColor: '#4BA3E3'
                  }
                }
              }}
            />

            <PasswordInput
              label="新しいパスワード"
              placeholder="新しいパスワードを入力"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={loading}
              styles={{
                label: {
                  color: '#4a5568'
                },
                input: {
                  '&:focus': {
                    borderColor: '#4BA3E3'
                  }
                }
              }}
            />

            <PasswordInput
              label="新しいパスワード（確認）"
              placeholder="新しいパスワードを再入力"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              styles={{
                label: {
                  color: '#4a5568'
                },
                input: {
                  '&:focus': {
                    borderColor: '#4BA3E3'
                  }
                }
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="gradient"
              gradient={{ from: '#4BA3E3', to: '#FFE45C' }}
              mt="md"
              loading={loading}
            >
              パスワードを変更
            </Button>

            <Button
              variant="subtle"
              color="gray"
              fullWidth
              onClick={() => router.back()}
              disabled={loading}
            >
              キャンセル
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
} 