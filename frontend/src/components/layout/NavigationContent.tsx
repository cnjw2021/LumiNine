'use client';

import React from 'react';
import { Stack, Text } from '@mantine/core';
import { NavigationMenu, MenuItem } from './NavigationMenu';
import { FONTS, NAV } from '@/utils/theme';

/**
 * ナビゲーション共通コンテンツ
 *
 * DRY: モバイル(Drawer) / デスクトップ(Sidebar) で共有される
 *      メニューセクション群を単一コンポーネントに統合
 */

/** セクションタイトルの共通スタイル (SSoT) */
const SECTION_TITLE_STYLE = { letterSpacing: '0.5px', fontFamily: FONTS.caption } as const;

interface NavigationContentProps {
    defaultMenuItems: MenuItem[];
    aboutItems: MenuItem[];
    accountItems: MenuItem[];
    adminMenuItems: MenuItem[];
    isLoggedIn: boolean;
    isAdmin: boolean;
    isSuperuser: boolean;
    hasAnyAdminPermission: boolean;
    permissionsLoaded: boolean;
    onNavigate: (href: string) => void;
    navigating: string | null;
}

export const NavigationContent = ({
    defaultMenuItems,
    aboutItems,
    accountItems,
    adminMenuItems,
    isLoggedIn,
    isAdmin,
    isSuperuser,
    hasAnyAdminPermission,
    permissionsLoaded,
    onNavigate,
    navigating,
}: NavigationContentProps) => {
    return (
        <Stack gap="lg">
            {defaultMenuItems.length > 0 && (
                <Stack gap="xs">
                    <NavigationMenu
                        items={defaultMenuItems}
                        onNavigate={onNavigate}
                        navigating={navigating}
                    />
                </Stack>
            )}

            {aboutItems.length > 0 && (
                <Stack gap="xs">
                    <Text size="sm" fw={700} c={NAV.sectionTitle} style={SECTION_TITLE_STYLE}>
                        鑑定のインサイト
                    </Text>
                    <NavigationMenu
                        items={aboutItems}
                        onNavigate={onNavigate}
                        navigating={navigating}
                    />
                </Stack>
            )}

            <Stack gap="xs">
                <Text size="sm" fw={700} c={NAV.sectionTitle} style={SECTION_TITLE_STYLE}>
                    アカウント
                </Text>
                <NavigationMenu
                    items={accountItems}
                    onNavigate={onNavigate}
                    navigating={navigating}
                />
            </Stack>

            {isLoggedIn && (isAdmin || isSuperuser) && hasAnyAdminPermission && (
                <Stack gap="xs">
                    <Text size="sm" fw={700} c={NAV.sectionTitle} style={SECTION_TITLE_STYLE}>
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
                            onNavigate={onNavigate}
                            navigating={navigating}
                        />
                    )}
                </Stack>
            )}
        </Stack>
    );
};
