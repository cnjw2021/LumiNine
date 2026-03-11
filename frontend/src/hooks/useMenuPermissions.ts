'use client';

import { useState, useEffect, useMemo } from 'react';
import { MenuItem } from '@/components/layout/NavigationMenu';

/**
 * メニュー項目の権限チェック
 *
 * SRP: 権限チェック・判定のみを担当
 * DIP: checkPermissions 関数を外部から注入
 */

/** 管理者ロールに暗黙的に付与される権限 */
const ADMIN_IMPLICIT_PERMISSIONS = ['user_view', 'user_create', 'user_edit', 'user_delete'] as const;

interface UseMenuPermissionsParams {
    isLoggedIn: boolean;
    isAdmin: boolean;
    isSuperuser: boolean;
    authLoading: boolean;
    adminMenuItems: MenuItem[];
    checkPermissions: (codes: string[]) => Promise<Record<string, boolean>>;
}

export function useMenuPermissions({
    isLoggedIn,
    isAdmin,
    isSuperuser,
    authLoading,
    adminMenuItems,
    checkPermissions,
}: UseMenuPermissionsParams) {
    const [permissionsLoaded, setPermissionsLoaded] = useState(false);
    const [userPermissions, setUserPermissions] = useState<Record<string, boolean>>({});

    useEffect(() => {
        // ログアウト時やロード中は状態をリセット
        if (!isLoggedIn || authLoading) {
            setPermissionsLoaded(false);
            setUserPermissions({});
            return;
        }

        let cancelled = false;

        // 再チェック前に一旦リセット
        setPermissionsLoaded(false);
        setUserPermissions({});

        const checkMenuPermissions = async () => {
            try {
                const permissionCodes = adminMenuItems
                    .filter(item => item.permission)
                    .map(item => item.permission as string);

                if (permissionCodes.length > 0) {
                    const permissions = await checkPermissions(permissionCodes);
                    if (!cancelled) {
                        setUserPermissions(permissions);
                        setPermissionsLoaded(true);
                    }
                } else {
                    if (!cancelled) {
                        setUserPermissions({});
                        setPermissionsLoaded(true);
                    }
                }
            } catch (error) {
                console.error('Error checking permissions:', error);
                if (!cancelled) {
                    setUserPermissions({});
                    setPermissionsLoaded(true);
                }
            }
        };

        checkMenuPermissions();

        return () => { cancelled = true; };
    }, [isLoggedIn, authLoading, adminMenuItems, checkPermissions]);

    // メニューセクションの表示可否を判定
    const hasAnyAdminPermission = useMemo(() => {
        if (!isLoggedIn) return false;
        if (isSuperuser) return true;
        if (!permissionsLoaded) return false;

        return adminMenuItems.some(item => {
            if (!item.permission) return true;
            if (isAdmin && (ADMIN_IMPLICIT_PERMISSIONS as readonly string[]).includes(item.permission)) return true;
            return userPermissions[item.permission] === true;
        });
    }, [isLoggedIn, permissionsLoaded, isSuperuser, isAdmin, adminMenuItems, userPermissions]);

    return { permissionsLoaded, hasAnyAdminPermission };
}
