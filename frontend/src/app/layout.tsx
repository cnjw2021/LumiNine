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

const theme = createTheme({
  primaryColor: 'pink',
  colors: {
    pink: [
      '#fff5f7',
      '#fdf2f8',
      '#fce7f3',
      '#fbcfe8',
      '#f9a8d4',
      '#f472b6',
      '#ec4899',
      '#db2777',
      '#be185d',
      '#9d174d',
    ],
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
      <body style={{ margin: 0, backgroundColor: '#fff' }}>
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
              padding="20px"
              styles={{
                main: {
                  background: 'linear-gradient(45deg, rgba(75, 163, 227, 0.2) 0%, rgba(255, 228, 92, 0.2) 50%, rgba(75, 163, 227, 0.2) 100%)',
                  width: '100%',
                  maxWidth: '100%',
                  overflowX: 'hidden'
                },
                navbar: {
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(10px)',
                  border: 'none'
                }
              }}
            >
              <AppShell.Header hiddenFrom="sm">
                <Group h="100%" px="20px" style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(10px)' }}>
                  <Burger
                    opened={opened}
                    onClick={toggle}
                    hiddenFrom="sm"
                    size="sm"
                    color="#4BA3E3"
                  />
                  <Text size="xl" fw={600} c="#4BA3E3">
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