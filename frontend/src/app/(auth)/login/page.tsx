"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from '@/contexts/auth/AuthContext';
import { TextInput, PasswordInput, Button, Paper, Title, Container, Stack, Text } from '@mantine/core';
import axios from '@/utils/api'; // Flaskとの通信に使うaxiosインスタンスを想定
import { AxiosError } from 'axios';
import { COLORS, FONTS, GRADIENTS, CARD, INPUT_STYLES } from '@/utils/theme';

export default function LoginPage() {
  const router = useRouter();
  const { token, setLoginStatus } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ログイン済みユーザーのリダイレクト
  useEffect(() => {
    if (token) {
      router.replace('/');
    }
  }, [token, router]);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // フォームのデフォルト送信を確実に防ぐ

    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/auth/login', { email, password });

      // バックエンドから返されたレスポンスをチェック
      if (response.data?.access_token) {
        // access_tokenフィールドを使用（バックエンドのレスポンス形式に合わせる）
        const refreshToken = response.data.refresh_token || null;

        // ログイン成功時の処理
        setLoginStatus(true, response.data.access_token, refreshToken);

        // 画面をリロード
        window.location.href = '/';
      } else {
        // エラーをコンソールに出力せず、UIにのみ表示
        setError('ログイン情報の取得に失敗しました。しばらく経ってからもう一度お試しください。');
      }
    } catch (error: unknown) {
      // エラー時はログイン状態をリセット
      setLoginStatus(false);

      if (error instanceof AxiosError) {
        // 401エラー（認証失敗）の場合の特別処理
        if (error.response?.status === 401) {
          setError(error.response.data?.message || 'メールアドレスまたはパスワードが正しくありません');
        } else if (error.response?.data?.message) {
          setError(error.response.data.message);
        } else if (error.response?.data?.error) {
          setError(error.response.data.error);
        } else {
          setError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
        }
      } else {
        setError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    handleLogin(e);
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
          c={COLORS.accent}
          style={{ fontFamily: FONTS.title }}
        >
          ログイン
        </Title>

        <form onSubmit={handleSubmit} noValidate>
          <Stack>
            {error && (
              <Text c={COLORS.error} mb="md" ta="center" size="sm">
                {error}
              </Text>
            )}

            <TextInput
              label="メールアドレス"
              placeholder="your@email.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              label="パスワード"
              placeholder="パスワードを入力"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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
              variant="gradient"
              gradient={GRADIENTS.button}
              mt="md"
              loading={loading}
              style={{ fontFamily: FONTS.body }}
            >
              ログイン
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
}
