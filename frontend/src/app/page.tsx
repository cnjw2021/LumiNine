"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useAuth } from '@/contexts/auth/AuthContext';
import { Box, Container, Flex, Text, Title, UnstyledButton, TextInput, Button } from '@mantine/core';
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

        <Box style={{ position: 'absolute', top: '50%', left: '15%', transform: 'translateY(-50%)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, opacity: 0.6 }}>
          <Box style={{ width: 128, height: 192, borderRadius: 9999, backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuBFK3cfccaekVQLO_BUjuS0YhXOLOrQgkWywLPqcBdjJEvxV4MSLAH-RHTMmjLYDfcAZbndIkBJWhocVuXZ4izUyMyNTPNN9zNRCrhhN1H26rWNgd_UcPQVKqHAk1Y6O_PacrKCjaCgDmRwC8zlOch0VrYOHbAUjpROsZM0_aji2EYNOfpToU5pxZtnI8wV5h-uQBXlWBz3aW5wwB6OkymkWTR53GWTMRS2ewxeXdDsOE93fxgxJBgpKXy18Bgsu0A_9UPqY8ws-kQv')`, backgroundSize: 'cover', backgroundPosition: 'center', transform: 'rotate(12deg)', border: '1px solid rgba(255,255,255,0.5)', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }} />
          <Box style={{ width: 96, height: 96, borderRadius: '50%', backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuD23mxzUA5ZDO906MRNGvxB63gJHOcn1kxkm-5X94gpzY8ePaA-XR7RAa6a0dqrdNBM1lN5s9ezqN_e4h5p33ReCSznYbyvYQQbLgTh_6uBRXZCt3mLBC56JffbEZ955ImFZnLGcmxFSnjAQxHhtezlfxB78E-HNPSBjurwHaiohecAMZiszqoEWKfyRkugokMS3ov4PT4Knmd8Lg9cA5Ihl9JJ94dUTqO9PuDBbuSzRZ6uxvNcl9U2ipkM_oH2lOQ1hhoE4-5s7hcc')`, backgroundSize: 'cover', backgroundPosition: 'center', transform: 'rotate(-12deg)', marginTop: 80, border: '1px solid rgba(255,255,255,0.5)', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }} />
          <Box style={{ width: 160, height: 160, borderRadius: '50%', backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuDaTZso3IaBgVFH3pSHzmZ10rb2T43_PxemF7PgCi3VeOpzYI8gPManVtwVa3M4zKHCOV4u7Nn1zyskiQ8lVPyH1xAewMkCnhT5bnmVYw_1glHSamSv9aMVty6W2iBQ7itn2YjpYynnYFQOiOY7y6EaYjQM0V6_nDu3vMLfMYNm4A5B8uObeBgLtrFuVxWPbTsS62yGkHnj4W7lqfdZnThBEjNVod8NW6miX0chOAkT3kTKGQEyBw-0hTk8YpP2O1nhVdAZicK5MWOa')`, backgroundSize: 'cover', backgroundPosition: 'center', transform: 'rotate(6deg)', marginLeft: -40, border: '1px solid rgba(255,255,255,0.5)', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }} />
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
            <UnstyledButton style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>Collections</UnstyledButton>
            <UnstyledButton style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>Philosophy</UnstyledButton>
            <UnstyledButton style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>Materials</UnstyledButton>
            <UnstyledButton style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.05em', transition: 'color 0.2s', '&:hover': { color: theme.primary } }}>Stores</UnstyledButton>
          </Flex>
          <Flex align="center" gap={24}>
            {!token ? (
              <Button onClick={() => router.push('/login')} radius="xl" size="md" color={theme.primary} style={{ backgroundColor: theme.primary, fontWeight: 700, padding: '0 32px' }}>ログイン</Button>
            ) : (
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
          <Box visibleFrom="md" style={{ width: '45%', position: 'relative', height: 600, minWidth: 400 }}>
            <Box style={{ position: 'absolute', top: 0, right: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box style={{ position: 'relative' }}>
                <Box style={{ width: 256, height: 320, backgroundColor: 'rgba(255,255,255,0.3)', backdropFilter: 'blur(4px)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.4)', boxShadow: 'inset 0 2px 4px 0 rgba(0,0,0,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuDnsl-OYpYL1rKHE0maqfHkz8ZDoxkIEGREwenSibE-Xh-5wI5hcev7_ZR7YH7AQExxJvFOfy4d6KHjWyAgubHwcnxI4SjVGSU0l-wHxDhE4F6nlX2vEL0BlB3BLnrqwAAklImyqx-lng30KxV-AsN9GnobEw0SScQfrEoB2RgOklbGyRzGZuIHJTitrO4QXDRsS9_SAEcg_g0TBtUTrjfLaZ0epIw6oy_tN_IA8t6qKm0lz4Ki3U9cDwSe1-qLFjAHRZQgvJnxHNYP" alt="Fine gold necklace with gemstone" style={{ objectFit: 'cover', width: '100%', height: '100%', opacity: 0.9 }} />
                </Box>
              </Box>
            </Box>
          </Box>

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
          <Flex direction={{ base: 'column', md: 'row' }} gap={16} mt={16} style={{ width: '100%' }}>
            <TextInput
              placeholder="メールアドレスを入力"
              radius="xl"
              size="md"
              style={{ flex: 1, fontFamily: '"Noto Sans JP", sans-serif' }}
              styles={{ input: { height: 56, backgroundColor: '#fff', border: `1px solid ${theme.primary}33` } }}
            />
            <Button radius="xl" size="md" style={{ backgroundColor: theme.charcoal, color: '#fff', fontWeight: 700, letterSpacing: '0.1em', height: 56, padding: '0 40px' }}>
              購読する
            </Button>
          </Flex>
          <Text style={{ fontSize: 10, opacity: 0.4, marginTop: 40, letterSpacing: '0.1em' }}>© 2024 LumiNine Editorial. All Rights Reserved.</Text>
        </Box>
      </Box>
    </Box>
  );
}
