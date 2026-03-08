"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { PasswordInput, Button, Paper, Title, Container, Stack, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import api from '@/utils/api';
import { AxiosError } from 'axios';
import { COLORS, FONTS, GRADIENTS, CARD, BUTTON } from '@/utils/theme';

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
        shadow="none"
        p="xl"
        radius={CARD.borderRadius}
        style={{
          backgroundColor: COLORS.cardBg,
          border: CARD.border,
          boxShadow: CARD.boxShadow,
        }}
      >
        <Title
          order={1}
          ta="center"
          mb="lg"
          c={COLORS.text}
          style={{ fontFamily: FONTS.title, fontWeight: 'normal', letterSpacing: '0.05em' }}
        >
          パスワード変更
        </Title>

        <form onSubmit={handlePasswordChange} noValidate>
          <Stack>
            {error && (
              <Text c={COLORS.error} mb="md" ta="center" size="sm">
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
                label: { color: COLORS.text },
                input: {
                  '&:focus': {
                    borderColor: COLORS.accent
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
                label: { color: COLORS.text },
                input: {
                  '&:focus': {
                    borderColor: COLORS.accent
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
                label: { color: COLORS.text },
                input: {
                  '&:focus': {
                    borderColor: COLORS.accent
                  }
                }
              }}
            />

            <Button
              type="submit"
              fullWidth
              mt="md"
              loading={loading}
              style={{
                ...BUTTON.primary,
                padding: '14px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
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