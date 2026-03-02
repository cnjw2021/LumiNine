'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';
import { useRouter } from 'next/navigation';
import { Stack, Drawer, Box, Text, Flex, Transition } from '@mantine/core';
import { 
  IconHome2, 
  IconLogout, 
  IconLogin, 
  IconQuestionMark,
  IconLock,
  IconChevronDown,
  IconDatabase,
  IconDownload
} from '@tabler/icons-react';
import { NavigationMenu, MenuItem } from './NavigationMenu';
import { DrawerHeader } from './DrawerHeader';

interface NavigationProps {
  opened: boolean;
  onClose: () => void;
}

export const Navigation = ({ opened, onClose }: NavigationProps) => {
  const router = useRouter();
  const { isLoggedIn, isAdmin, isSuperuser, checkPermissions, logout, isLoading: authLoading } = useAuth();
  const [permissionsLoaded, setPermissionsLoaded] = useState(false);
  const [userPermissions, setUserPermissions] = useState<Record<string, boolean>>({});
  const [navigating, setNavigating] = useState<string | null>(null);
  const [showScrollIndicator, setShowScrollIndicator] = useState(false);

  // メニュー項目の定義
  const defaultMenuItems: MenuItem[] = useMemo(() => {
    if (!isLoggedIn && !authLoading) return [];
    return [
      { icon: IconHome2, label: '九星気学鑑定', href: '/' },
      { icon: IconQuestionMark, label: 'サンプル一覧', href: '/examples' }
    ];
  }, [isLoggedIn, authLoading]);

  // 管理者メニュー項目
  const adminMenuItems: MenuItem[] = useMemo(() => {
    if (!isLoggedIn || (!isAdmin && !isSuperuser)) return [];
    
    const items = [
      { icon: IconDatabase, label: '管理画面', href: '/admin', permission: 'data_management' }
    ];

    if (isSuperuser) {
      items.push(
        { icon: IconDownload, label: 'SVG九星盤ダウンロード', href: '/admin/svg-kyusei', permission: 'svg_download' },
        { icon: IconDownload, label: 'SVG五行図ダウンロード', href: '/admin/svg-gogyo', permission: 'svg_download' }
      );
    }

    return items;
  }, [isLoggedIn, isAdmin, isSuperuser]);

  // アカウントメニュー項目
  const accountItems: MenuItem[] = useMemo(() => {
    if (isLoggedIn || authLoading) {
      return [
        { icon: IconLock, label: 'パスワード変更', href: '/password-change' },
        { 
          icon: IconLogout, 
          label: 'ログアウト', 
          href: '#', 
          onClick: async () => {
            try {
              onClose();
              await logout();
              window.location.href = '/login';
            } catch (error) {
              console.error('Logout error:', error);
              window.location.href = '/login';
            }
          }
        }
      ];
    } else {
      return [{ icon: IconLogin, label: 'ログイン', href: '/login' }];
    }
  }, [isLoggedIn, authLoading, logout, onClose]);

  // 権限チェック
  useEffect(() => {
    if (!isLoggedIn || authLoading) return;
    
    const checkMenuPermissions = async () => {
      try {
        const permissionCodes = adminMenuItems
          .filter(item => item.permission)
          .map(item => item.permission as string);

        if (permissionCodes.length > 0) {
          const permissions = await checkPermissions(permissionCodes);
          setUserPermissions(permissions);
          setPermissionsLoaded(true);
        }
      } catch (error) {
        console.error('Error checking permissions:', error);
        setUserPermissions({});
        setPermissionsLoaded(true);
      }
    };

    checkMenuPermissions();
  }, [isLoggedIn, authLoading, adminMenuItems, checkPermissions]);

  const handleNavigation = async (href: string) => {
    try {
      if (!isLoggedIn && href !== '/login') {
        onClose();
        router.push('/login');
        return;
      }

      setNavigating(href);
      onClose();
      router.push(href);
      
      const timeoutId = setTimeout(() => {
        setNavigating(null);
      }, 5000);
      
      return () => clearTimeout(timeoutId);
    } catch (error) {
      console.error('Navigation error:', error);
      setNavigating(null);
    }
  };

  // メニューセクションの表示可否を判定
  const hasAnyAdminPermission = useMemo(() => {
    if (!isLoggedIn) return false;
    if (isSuperuser) return true;
    if (!permissionsLoaded) return false;
    
    return adminMenuItems.some(item => {
      if (!item.permission) return true;
      if (isAdmin && ['user_view', 'user_create', 'user_edit', 'user_delete'].includes(item.permission)) return true;
      return userPermissions[item.permission] === true;
    });
  }, [isLoggedIn, permissionsLoaded, isSuperuser, isAdmin, adminMenuItems, userPermissions]);

  // スクロールインジケーターの表示制御
  useEffect(() => {
    const checkScroll = () => {
      const container = document.querySelector('.mantine-Drawer-body');
      if (container) {
        const hasOverflow = container.scrollHeight > container.clientHeight;
        setShowScrollIndicator(hasOverflow);
      }
    };

    checkScroll();
    window.addEventListener('resize', checkScroll);
    return () => window.removeEventListener('resize', checkScroll);
  }, [isLoggedIn, permissionsLoaded, adminMenuItems.length]);

  return (
    <>
      <Drawer
        opened={opened}
        onClose={onClose}
        size="320px"
        padding="0"
        hiddenFrom="sm"
        withCloseButton={false}
        title={<DrawerHeader title="九星気学" onClose={onClose} />}
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
        <Box style={{ position: 'relative' }}>
          <Stack gap="lg">
            {defaultMenuItems.length > 0 && (
              <Stack gap="xs">
                <NavigationMenu 
                  items={defaultMenuItems}
                  onNavigate={handleNavigation}
                  navigating={navigating}
                />
              </Stack>
            )}
            
            {(isLoggedIn || authLoading) && (
              <Stack gap="xs">
                <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                  九星気学について
                </Text>
              </Stack>
            )}

            <Stack gap="xs">
              <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                アカウント
              </Text>
              <NavigationMenu 
                items={accountItems}
                onNavigate={handleNavigation}
                navigating={navigating}
              />
            </Stack>
            
            {isLoggedIn && (isAdmin || isSuperuser) && hasAnyAdminPermission && (
              <Stack gap="xs">
                <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                  管理者メニュー
                  {!permissionsLoaded && (
                    <Text component="span" size="xs" c="dimmed" style={{ marginLeft: '5px' }}>
                      (読み込み中...)
                    </Text>
                  )}
                </Text>
                {permissionsLoaded && (
                  <NavigationMenu 
                    items={adminMenuItems}
                    onNavigate={handleNavigation}
                    navigating={navigating}
                  />
                )}
              </Stack>
            )}
          </Stack>

          {/* スクロールインジケーター */}
          <Transition mounted={showScrollIndicator} transition="fade" duration={200}>
            {(styles) => (
              <Flex
                justify="center"
                align="center"
                style={{
                  ...styles,
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '10px',
                  background: 'linear-gradient(to top, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0) 100%)',
                  pointerEvents: 'none',
                }}
              >
                <IconChevronDown size={20} color="#4BA3E3" style={{ opacity: 0.7 }} />
              </Flex>
            )}
          </Transition>
        </Box>
      </Drawer>

      <Stack
        visibleFrom="sm"
        p="md"
        style={{
          height: '100%',
          width: '320px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(10px)',
          borderRight: '1px solid rgba(75, 163, 227, 0.1)',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Text size="xl" fw={600} c="#4BA3E3" mb="md">九星気学</Text>
        <Box style={{ position: 'relative', flexGrow: 1, overflow: 'auto' }}>
          <Stack gap="lg">
            {defaultMenuItems.length > 0 && (
              <Stack gap="xs">
                <NavigationMenu 
                  items={defaultMenuItems}
                  onNavigate={handleNavigation}
                  navigating={navigating}
                />
              </Stack>
            )}
            
            {(isLoggedIn || authLoading) && (
              <Stack gap="xs">
                <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                  九星気学について
                </Text>
              </Stack>
            )}

            <Stack gap="xs">
              <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                アカウント
              </Text>
              <NavigationMenu 
                items={accountItems}
                onNavigate={handleNavigation}
                navigating={navigating}
              />
            </Stack>
            
            {isLoggedIn && (isAdmin || isSuperuser) && hasAnyAdminPermission && (
              <Stack gap="xs">
                <Text size="sm" fw={700} c="#4BA3E3" style={{ letterSpacing: '0.5px' }}>
                  管理者メニュー
                  {!permissionsLoaded && (
                    <Text component="span" size="xs" c="dimmed" style={{ marginLeft: '5px' }}>
                      (読み込み中...)
                    </Text>
                  )}
                </Text>
                {permissionsLoaded && (
                  <NavigationMenu 
                    items={adminMenuItems}
                    onNavigate={handleNavigation}
                    navigating={navigating}
                  />
                )}
              </Stack>
            )}
          </Stack>
        </Box>
      </Stack>
    </>
  );
}; 