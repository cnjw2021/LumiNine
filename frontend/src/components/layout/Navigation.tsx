'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';
import { useRouter } from 'next/navigation';
import { Stack, Drawer, Box, Text } from '@mantine/core';
import { DrawerHeader } from './DrawerHeader';
import { NavigationContent } from './NavigationContent';
import { ScrollIndicator } from './ScrollIndicator';
import { useNavigationMenuItems } from '@/hooks/useNavigationMenuItems';
import { useMenuPermissions } from '@/hooks/useMenuPermissions';
import { COLORS, NAV } from '@/utils/theme';

/**
 * ナビゲーションコンテナ
 *
 * SRP: Drawer / Sidebar レイアウトの切り替えと
 *      ルーティング処理のみを担当
 */

/** Drawer / Sidebar の幅 */
const NAV_WIDTH = '320px';

/** ナビゲーション後の状態クリア遅延 (ms) */
const NAVIGATION_RESET_DELAY_MS = 500;

/** 共通背景スタイル */
const NAV_BG_STYLE = {
  backgroundColor: 'rgba(245, 247, 243, 0.95)',
  backdropFilter: 'blur(10px)',
} as const;

interface NavigationProps {
  opened: boolean;
  onClose: () => void;
}

export const Navigation = ({ opened, onClose }: NavigationProps) => {
  const router = useRouter();
  const { isLoggedIn, isAdmin, isSuperuser, checkPermissions, logout, isLoading: authLoading } = useAuth();
  const [navigating, setNavigating] = useState<string | null>(null);

  const { defaultMenuItems, adminMenuItems, aboutItems, accountItems } = useNavigationMenuItems({
    isLoggedIn, isAdmin, isSuperuser, authLoading, onClose, logout,
  });

  const { permissionsLoaded, hasAnyAdminPermission } = useMenuPermissions({
    isLoggedIn, isAdmin, isSuperuser, authLoading, adminMenuItems, checkPermissions,
  });

  const handleNavigation = async (href: string) => {
    try {
      if (!isLoggedIn && href !== '/login') {
        onClose();
        router.push('/login');
        return;
      }
      setNavigating(href);
      router.push(href);
      onClose();
      setTimeout(() => setNavigating(null), NAVIGATION_RESET_DELAY_MS);
    } catch (error) {
      console.error('Navigation error:', error);
      setNavigating(null);
    }
  };

  /** NavigationContent に渡す共通 props */
  const contentProps = {
    defaultMenuItems,
    aboutItems,
    accountItems,
    adminMenuItems,
    isLoggedIn,
    isAdmin,
    isSuperuser,
    hasAnyAdminPermission,
    permissionsLoaded,
    onNavigate: handleNavigation,
    navigating,
  };

  return (
    <>
      <Drawer
        opened={opened}
        onClose={onClose}
        size={NAV_WIDTH}
        padding="0"
        hiddenFrom="sm"
        withCloseButton={false}
        lockScroll={false}
        title={<DrawerHeader title="LumiNine" onClose={onClose} />}
        styles={{
          header: {
            padding: 0,
            margin: 0,
            borderBottom: `2px solid ${NAV.borderColor}`,
            ...NAV_BG_STYLE,
          },
          body: {
            padding: '20px',
            ...NAV_BG_STYLE,
          },
        }}
      >
        <Box style={{ position: 'relative' }}>
          <NavigationContent {...contentProps} />
          <ScrollIndicator deps={[isLoggedIn, permissionsLoaded, adminMenuItems.length]} />
        </Box>
      </Drawer>

      <Stack
        visibleFrom="sm"
        p="md"
        style={{
          height: '100%',
          width: NAV_WIDTH,
          ...NAV_BG_STYLE,
          borderRight: `1px solid ${NAV.borderColor}`,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Text size="xl" mb="md" style={{ fontSize: 20, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: COLORS.text }}>LumiNine</Text>
        <Box style={{ position: 'relative', flexGrow: 1, overflow: 'auto' }}>
          <NavigationContent {...contentProps} />
        </Box>
      </Stack>
    </>
  );
};