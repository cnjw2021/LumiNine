'use client';

import { useMemo } from 'react';
import {
    IconHome2,
    IconLogout,
    IconLogin,
    IconQuestionMark,
    IconLock,
    IconDatabase
} from '@tabler/icons-react';
import { MenuItem } from '@/components/layout/NavigationMenu';

/**
 * ナビゲーションメニュー項目の定義
 *
 * SRP: メニュー項目の定義・構成のみを担当
 * SSoT: 全メニュー項目がこのフック1箇所で管理される
 */

/** 管理者メニューの権限コード */
export const ADMIN_PERMISSION_DATA_MANAGEMENT = 'data_management';

interface UseNavigationMenuItemsParams {
    isLoggedIn: boolean;
    isAdmin: boolean;
    isSuperuser: boolean;
    authLoading: boolean;
    onClose: () => void;
    logout: () => Promise<void>;
}

export function useNavigationMenuItems({
    isLoggedIn,
    isAdmin,
    isSuperuser,
    authLoading,
    onClose,
    logout,
}: UseNavigationMenuItemsParams) {
    // メニュー項目の定義
    const defaultMenuItems: MenuItem[] = useMemo(() => {
        if (!isLoggedIn && !authLoading) return [];
        return [
            { icon: IconHome2, label: 'パーソナルストーン鑑定', href: '/appraisal' }
        ];
    }, [isLoggedIn, authLoading]);

    // 管理者メニュー項目
    const adminMenuItems: MenuItem[] = useMemo(() => {
        if (!isLoggedIn || (!isAdmin && !isSuperuser)) return [];
        return [
            { icon: IconDatabase, label: '管理画面', href: '/admin', permission: ADMIN_PERMISSION_DATA_MANAGEMENT }
        ];
    }, [isLoggedIn, isAdmin, isSuperuser]);

    // 鑑定のインサイト
    const aboutItems: MenuItem[] = useMemo(() => {
        if (!isLoggedIn && !authLoading) return [];
        return [
            { icon: IconQuestionMark, label: '数秘術について', href: '/about/numerology' },
            { icon: IconQuestionMark, label: '九星気学について', href: '/about/ninestarki' },
            { icon: IconQuestionMark, label: 'パワーストーンについて', href: '/about/powerstone' }
        ];
    }, [isLoggedIn, authLoading]);

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

    return { defaultMenuItems, adminMenuItems, aboutItems, accountItems };
}
