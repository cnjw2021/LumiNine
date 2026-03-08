"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from '@/contexts/auth/AuthContext';
import { Box, Container, Flex, Text, Title, UnstyledButton, Button } from '@mantine/core';
import { IconSparkles, IconDiamond, IconShieldCheck, IconWand } from '@tabler/icons-react';

export default function LandingPage() {
  const { token, isLoading } = useAuth();
  const router = useRouter();

  const handleStart = () => {
    if (token) {
      router.push('/appraisal');
    } else {
      router.push('/login');
    }
  };

  // Convert the Tailwind theme variables to standard JS
  const theme = {
    primary: "#d8a6a6",
    accentGold: "#d4af37",
    charcoal: "#1d1515",
    bgLight: "#f9f7f2",
  };

  return (
    <Box
      style={{
        backgroundColor: theme.bgLight,
        color: theme.charcoal,
        fontFamily: '"Noto Serif JP", serif',
        minHeight: '100vh',
        overflowX: 'hidden',
        position: 'relative'
      }}
    >
      {/* Decorative Background Elements (Floating Stones Aesthetic) */}
      <Box style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
        <Box style={{ position: 'absolute', top: '25%', left: '25%', width: 256, height: 256, borderRadius: '50%', backgroundColor: `${theme.primary}33`, filter: 'blur(40px)', opacity: 0.4 }} />
        <Box style={{ position: 'absolute', bottom: '25%', left: 40, width: 384, height: 384, borderRadius: '50%', backgroundColor: `${theme.accentGold}1a`, filter: 'blur(40px)', opacity: 0.4 }} />

        {/* Floating Stones Layer (Fills left half vertically, all visible above the fold) */}
        <Box style={{ position: 'absolute', top: 0, left: 0, bottom: 0, width: '50%', pointerEvents: 'none', zIndex: 1, minHeight: 800 }}>
          {/* Top Stone: Fluorite (Mystical purple/green) */}
          <Box style={{ position: 'absolute', top: '10%', left: '44%', width: 140, height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'rotate(20deg)', filter: 'drop-shadow(0 20px 30px rgba(0,0,0,0.1))', opacity: 0.9 }}>
            <Box style={{ width: '100%', height: '100%', backgroundImage: `url('/images/stones/fluorite.png')`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }} />
          </Box>

          {/* Upper Left Stone: Lapis Lazuli (Deep blue, very powerstone-like) */}
          <Box style={{ position: 'absolute', top: '22%', left: '10%', width: 160, height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'rotate(-10deg)', filter: 'drop-shadow(0 25px 35px rgba(0,0,0,0.12))', opacity: 0.95 }}>
            <Box style={{ width: '100%', height: '100%', backgroundImage: `url('/images/stones/lapis_lazuli.png')`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }} />
          </Box>

          {/* Center Main Stone: Rose Quartz (biggest, for soft contrast) */}
          <Box style={{ position: 'absolute', top: '42%', left: '35%', width: 260, height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'rotate(5deg)', filter: 'drop-shadow(0 40px 50px rgba(0,0,0,0.15))', opacity: 0.95 }}>
            <Box style={{ width: '100%', height: '100%', backgroundImage: `url('/images/stones/rose_quartz.png')`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }} />
          </Box>

          {/* Bottom Left Stone: Jade (Classic green Oriental powerstone) */}
          <Box style={{ position: 'absolute', top: '65%', left: '12%', width: 180, height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: 'rotate(-20deg)', filter: 'drop-shadow(0 25px 35px rgba(0,0,0,0.12))', opacity: 0.9 }}>
            <Box style={{ width: '100%', height: '100%', backgroundImage: `url('/images/stones/jade.png')`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' }} />
          </Box>
        </Box>
      </Box>

      {/* Top Navigation */}
      <Box component="header" style={{ position: 'fixed', top: 0, zIndex: 50, width: '100%', backgroundColor: 'rgba(249, 247, 242, 0.8)', backdropFilter: 'blur(12px)', borderBottom: `1px solid ${theme.primary}1a`, padding: '16px 24px' }}>
        <Box style={{ maxWidth: 1440, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Flex align="center" gap={12}>
            <IconSparkles size={32} color={theme.primary} />
            <Text style={{ fontSize: 20, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>LumiNine</Text>
          </Flex>
          <Flex align="center" gap={48} visibleFrom="md">
            <UnstyledButton style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>お問い合わせ</UnstyledButton>
            {!token && (
              <UnstyledButton onClick={() => router.push('/login')} style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>ログイン</UnstyledButton>
            )}
          </Flex>
          <Flex align="center" gap={24}>
            {token && (
              <Button onClick={() => router.push('/appraisal')} variant="outline" radius="xl" size="md" color={theme.primary} style={{ fontWeight: 700, padding: '0 32px' }}>鑑定へ戻る</Button>
            )}
            <Box style={{ width: 40, height: 40, borderRadius: '50%', border: `1px solid ${theme.primary}33`, backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuBb0WVjXt15W807V6ixd80YNHdVN-RJwV2-f8WRn2IbZFI9Ar1MSUa2C7om3OohF7tsQJY0J5cjr2XOKfAUErgxnUPqhISJc4Hl_6nNrqivyrAZlN96fojVN85a5gG6oUSTw8X0o-GLtFfPjPsj42FKuqyLtwk-0I4C9EIk7YXdusQrQOllha4dU0lKgygigWDGRMd70SETeVWItAV5tgXmIdiYi6PHL5PBJTCt7R8cXSETZhs_W-jzpwgS3WzGzm1xJ6p2v8d04pyz')`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
          </Flex>
        </Box>
      </Box>

      {/* Main Editorial Content */}
      <Box component="main" style={{ position: 'relative', display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 96, paddingBottom: 64, minHeight: 'calc(100vh - 200px)' }}>
        <Box style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: 1200, margin: '0 auto', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 64, padding: '0 24px', flexWrap: 'wrap' }}>

          {/* Visual Composition Area (Left) */}
          <Box visibleFrom="md" style={{ width: '45%', position: 'relative', height: 600, minWidth: 400 }} />

          {/* Editorial Text Area (Right) */}
          <Box style={{ flex: 1, display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', gap: 48, minWidth: 400 }}>

            <Box style={{ writingMode: 'vertical-rl', display: 'flex', flexDirection: 'column', gap: 32, height: 500 }}>
              <Title order={2} style={{ fontSize: 'clamp(36px, 4vw, 48px)', fontWeight: 700, lineHeight: 1.6, letterSpacing: '0.2em' }}>
                輝きが、私を語り出す。
              </Title>
              <Text style={{ fontSize: 18, fontWeight: 300, lineHeight: 2, letterSpacing: '0.1em', opacity: 0.8, paddingTop: 16 }}>
                洗練された大人の女性に贈る、<br />
                天然石とゴールドの調べ。<br />
                ルミネーインの鑑定で、<br />
                あなただけの運命の一石を<br />
                見つけてください。
              </Text>
            </Box>

            <Box style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
              <Box style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Text style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.3em', color: theme.primary, fontWeight: 700, fontFamily: '"Noto Sans JP", sans-serif' }}>LumiNine Editorial</Text>
                <Title order={3} style={{ fontSize: 24, fontWeight: 700, borderLeft: `2px solid ${theme.primary}`, paddingLeft: 16 }}>運命を彩る、唯一無二の輝き。</Title>
              </Box>

              <Button
                onClick={handleStart}
                radius="xl"
                size="xl"
                style={{ backgroundColor: theme.primary, color: '#fff', fontSize: 18, fontWeight: 700, letterSpacing: '0.1em', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', height: 56, minWidth: 280, fontFamily: '"Noto Sans JP", sans-serif' }}
              >
                {token ? '鑑定を開始する' : 'ログインして鑑定を始める'}
              </Button>

              <Box style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24, paddingTop: 40, borderTop: `1px solid ${theme.primary}1a` }}>
                <Flex direction="column" gap={8}>
                  <IconDiamond color={theme.primary} size={24} />
                  <Text style={{ fontSize: 10, fontWeight: 700, letterSpacing: '-0em', textTransform: 'uppercase', fontFamily: '"Noto Sans JP", sans-serif' }}>Authentic</Text>
                </Flex>
                <Flex direction="column" gap={8}>
                  <IconSparkles color={theme.primary} size={24} />
                  <Text style={{ fontSize: 10, fontWeight: 700, letterSpacing: '-0em', textTransform: 'uppercase', fontFamily: '"Noto Sans JP", sans-serif' }}>Personal</Text>
                </Flex>
                <Flex direction="column" gap={8}>
                  <IconShieldCheck color={theme.primary} size={24} />
                  <Text style={{ fontSize: 10, fontWeight: 700, letterSpacing: '-0em', textTransform: 'uppercase', fontFamily: '"Noto Sans JP", sans-serif' }}>Quality</Text>
                </Flex>
              </Box>
            </Box>

          </Box>
        </Box>
      </Box>

      {/* Newsletter / CTA */}
      <Box component="footer" style={{ padding: '80px 24px', backgroundColor: theme.bgLight, borderTop: `1px solid ${theme.primary}0d` }}>
        <Box style={{ maxWidth: 720, margin: '0 auto', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32 }}>
          <IconWand size={48} color={theme.primary} />
          <Title order={2} style={{ fontSize: 30, fontWeight: 700, letterSpacing: '0.2em' }}>美しさは、内側から。</Title>
          <Text style={{ color: 'rgba(29, 21, 21, 0.7)', lineHeight: 1.6, fontWeight: 300 }}>
            最新のコレクション情報や、限定イベントのご案内、<br />
            あなたにふさわしい宝石の物語をお届けします。
          </Text>
          <Text style={{ fontSize: 10, opacity: 0.4, marginTop: 40, letterSpacing: '0.1em' }}>© 2024 LumiNine Editorial. All Rights Reserved.</Text>
        </Box>
      </Box>
    </Box>
  );
}
