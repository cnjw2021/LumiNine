'use client';

import { MantineProvider, createTheme, AppShell, Group, Text, Burger } from '@mantine/core';
import { Navigation } from '@/components/layout/Navigation';
import { AuthProvider } from '@/contexts/auth/AuthContext';
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [opened, { toggle }] = useDisclosure();

  return (
    <html lang="ja">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Serif+JP:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, backgroundColor: COLORS.primaryBg }}>
        <MantineProvider theme={theme} defaultColorScheme="light">
          <AuthProvider>
            <Notifications />
            <AppShell
              header={{ height: { base: 60, sm: 0 } }}
              navbar={{
                width: { base: 320, sm: 320, lg: 320 },
                breakpoint: 'sm',
                collapsed: { desktop: false, mobile: !opened }
              }}
              padding={{ base: 6, sm: 12, md: 16, lg: 24 }}
              styles={{
                main: {
                  backgroundColor: COLORS.primaryBg,
                  backgroundImage: GRADIENTS.pageBg,
                  width: '100%',
                  maxWidth: '100%',
                  overflowX: 'hidden'
                },
                navbar: {
                  backgroundColor: 'rgba(245, 247, 243, 0.95)',
                  backdropFilter: 'blur(10px)',
                  border: 'none'
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
                    color={COLORS.accent}
                  />
                  <Text
                    size="xl"
                    fw={400}
                    c={COLORS.text}
                    style={{ fontFamily: FONTS.title, letterSpacing: '0.05em' }}
                  >
                    九星気学
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
          </AuthProvider>
        </MantineProvider>
      </body>
    </html>
  );
}