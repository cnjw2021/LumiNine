'use client';

import React, { ReactNode } from 'react';
import { AppShell, Drawer, Group, Stack, Burger, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconDashboard, IconUsers, IconStars, IconCodeDots, IconSettings, IconDatabase, IconCalendarEvent, IconDownload } from '@tabler/icons-react';
import { useAdminCheck } from '../../../hooks/useAdminCheck';
import { NavigationMenu, MenuItem } from '@/components/layout/NavigationMenu';
import { DrawerHeader } from '@/components/layout/DrawerHeader';

// 管理メニューの項目を定義
const MENU_ITEMS: MenuItem[] = [
  { label: 'ダッシュボード', href: '/admin', icon: IconDashboard },
  { label: 'ユーザー管理', href: '/admin/users', icon: IconUsers },
  { label: '九星データ管理', href: '/admin/stars', icon: IconStars },
  { label: 'SVG九星盤ダウンロード', href: '/admin/svg-kyusei', icon: IconDownload },
  { label: '引っ越し吉日管理', href: '/admin/moving-dates', icon: IconCalendarEvent },
  { label: '権限管理', href: '/admin/permissions', icon: IconSettings },
  { label: 'データ管理', href: '/admin/data-management', icon: IconDatabase },
  { label: 'SQL実行', href: '/admin/sql-execution', icon: IconCodeDots },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const [opened, { toggle, close }] = useDisclosure();
  const { isLoading } = useAdminCheck();

  if (isLoading) {
    return null;
  }

  return (
    <>
      <AppShell
        header={{ height: 60 }}
        navbar={{
          width: 300,
          breakpoint: 'sm',
          collapsed: { desktop: false, mobile: true }
        }}
        padding={0}
        styles={{
          main: {
            width: '100%',
            maxWidth: '100%',
            overflowX: 'hidden',
            padding: '20px'
          }
        }}
      >
        <AppShell.Header style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          borderBottom: '2px solid rgba(75, 163, 227, 0.1)'
        }}>
          <Group h={60} px="20px" justify="space-between" w="100%">
            <Group gap="sm">
              <Burger
                opened={opened}
                onClick={toggle}
                hiddenFrom="sm"
                size="sm"
                color="#4BA3E3"
              />
              <Text 
                size="xl" 
                fw={600} 
                c="#4BA3E3" 
                style={{ 
                  letterSpacing: '0.5px',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}
              >
                管理画面
              </Text>
            </Group>
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="md" style={{
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          borderRight: '2px solid rgba(75, 163, 227, 0.1)'
        }}>
          <Stack gap="xs">
            <NavigationMenu 
              items={MENU_ITEMS}
              onNavigate={(href) => {
                close();
                window.location.href = href;
              }}
              navigating={null}
            />
          </Stack>
        </AppShell.Navbar>

        <AppShell.Main>
          {children}
        </AppShell.Main>
      </AppShell>

      <Drawer
        opened={opened}
        onClose={close}
        size="320px"
        padding="0"
        hiddenFrom="sm"
        withCloseButton={false}
        title={<DrawerHeader title="管理画面" onClose={close} />}
        styles={{
          header: {
            padding: 0,
            margin: 0,
            borderBottom: '2px solid rgba(75, 163, 227, 0.1)',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)'
          },
          body: {
            padding: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)'
          }
        }}
      >
        <Stack gap="xs">
          <NavigationMenu 
            items={MENU_ITEMS}
            onNavigate={(href) => {
              close();
              window.location.href = href;
            }}
            navigating={null}
          />
        </Stack>
      </Drawer>
    </>
  );
} 