'use client';

import { MantineProvider, createTheme, AppShell, Group, Text, Burger } from '@mantine/core';
import { Navigation } from '@/components/layout/Navigation';
import { AuthProvider, useAuth } from '@/contexts/auth/AuthContext';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@/components/styles/paragraph.css';
import '@/components/styles/result.css';
import { Notifications } from '@mantine/notifications';
import { useDisclosure } from '@mantine/hooks';
import { COLORS, GRADIENTS, FONTS, NAV } from '@/utils/theme';

const theme = createTheme({
  primaryColor: 'gold',
  colors: {
    gold: [
      '#fdfaf0',
      '#f9f3d5',
      '#f0e4a8',
      '#e6d27a',
      '#d4af37',
      '#c5975a',
      '#b07d2e',
      '#9a6a24',
      '#7d551d',
      '#604016',
    ],
  },
  fontFamily: FONTS.body,
  headings: {
    fontFamily: FONTS.title,
  },
});

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

function AppShellLayout({ children }: { children: React.ReactNode }) {
  const [opened, { toggle, close }] = useDisclosure();
  const pathname = usePathname();
  const { isLoggedIn } = useAuth();
  // ランディングページかつ未ログインの場合のみサイドバーを非表示にする
  const hideSidebar = pathname === '/' && !isLoggedIn;

  useEffect(() => {
    // 1. 라우트 이동 시 강제로 최상단 스크롤 (원활한 화면 전환용)
    window.scrollTo({ top: 0, left: 0 });

    // 모바일 환경에서 라우팅이 일어났을 때 Drawer를 강제로 닫음
    close();
  }, [pathname, close]);

  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      <Notifications />
      <AppShell
        header={{ height: { base: 60, sm: 0 } }}
        navbar={{
          width: { base: 320, sm: 320, lg: 320 },
          breakpoint: 'sm',
          collapsed: { desktop: hideSidebar, mobile: !opened }
        }}
        padding={hideSidebar ? 0 : { base: 6, sm: 12, md: 16, lg: 24 }}
        styles={{
          main: {
            backgroundColor: COLORS.primaryBg,
            backgroundImage: GRADIENTS.pageBg,
            width: '100%',
            maxWidth: '100%',
            padding: hideSidebar ? 0 : undefined
          },
          navbar: {
            backgroundColor: 'rgba(245, 247, 243, 0.95)',
            backdropFilter: 'blur(10px)',
            border: 'none',
          }
        }}
      >
        <AppShell.Header hiddenFrom="sm">
          <Group h="100%" px="20px" style={{ backgroundColor: 'rgba(245, 247, 243, 0.95)', backdropFilter: 'blur(10px)' }}>
            <Burger
              opened={opened}
              onClick={toggle}
              hiddenFrom="sm"
              size="sm"
              color={COLORS.rose}
            />
            <Text
              style={{ fontSize: 20, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: COLORS.text }}
            >
              LumiNine
            </Text>
          </Group>
        </AppShell.Header>
        <AppShell.Navbar>
          <Navigation opened={opened} onClose={toggle} />
        </AppShell.Navbar>
        <AppShell.Main>
          {children}
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Serif+JP:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, backgroundColor: COLORS.primaryBg }}>
        <AuthProvider>
          <AppShellLayout>{children}</AppShellLayout>
        </AuthProvider>
      </body>
    </html>
  );
}