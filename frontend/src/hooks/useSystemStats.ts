'use client';

import { useState, useEffect, useCallback } from 'react';
import api from '@/utils/api';
import { notifications } from '@mantine/notifications';
import { AxiosError } from 'axios';
import type { AdminUser, UpdateAccountLimitData } from '@/types/admin';

interface UseSystemStatsReturn {
    // 統計情報
    systemLimit: number;
    setSystemLimit: (v: number) => void;
    totalActiveUsers: number;
    deletedUsersCount: number;
    isSuperuser: boolean;

    // アカウント制限モーダル
    accountLimitModalOpened: boolean;
    setAccountLimitModalOpened: (v: boolean) => void;
    accountLimit: number;
    setAccountLimit: (v: number) => void;
    selectedLimitUser: AdminUser | null;
    setSelectedLimitUser: (v: AdminUser | null) => void;

    // システム制限モーダル
    systemLimitModalOpened: boolean;
    setSystemLimitModalOpened: (v: boolean) => void;

    // ハンドラー
    fetchSystemStats: () => Promise<void>;
    handleUpdateAccountLimit: (onSuccess: () => Promise<void>) => Promise<void>;
    handleUpdateSystemLimit: () => Promise<void>;
    handleCloseAccountLimitModal: () => void;
    handleSystemLimitChange: (value: number) => void;
}

export function useSystemStats(): UseSystemStatsReturn {
    // 統計情報
    const [systemLimit, setSystemLimit] = useState<number>(0);
    const [totalActiveUsers, setTotalActiveUsers] = useState<number>(0);
    const [deletedUsersCount, setDeletedUsersCount] = useState<number>(0);
    const [isSuperuser, setIsSuperuser] = useState(false);

    // アカウント制限モーダル
    const [accountLimitModalOpened, setAccountLimitModalOpened] = useState(false);
    const [accountLimit, setAccountLimit] = useState<number>(0);
    const [selectedLimitUser, setSelectedLimitUser] = useState<AdminUser | null>(null);

    // システム制限モーダル
    const [systemLimitModalOpened, setSystemLimitModalOpened] = useState(false);

    // スーパーユーザー確認
    const checkSuperuserStatus = useCallback(async () => {
        try {
            const response = await api.get('/auth/admin-status');
            setIsSuperuser(response.data.is_superuser || false);
        } catch (error) {
            console.error('Error checking superuser status:', error);
            setIsSuperuser(false);
        }
    }, []);

    useEffect(() => {
        checkSuperuserStatus();
    }, [checkSuperuserStatus]);

    // システム統計取得
    const fetchSystemStats = useCallback(async () => {
        try {
            const statsResponse = await api.get('/auth/admin/system-stats');
            setSystemLimit(statsResponse.data.account_limit || 0);
            setTotalActiveUsers(statsResponse.data.total_active_users || 0);
            setDeletedUsersCount(statsResponse.data.deleted_users_count || 0);
        } catch (error) {
            console.error('Error fetching system stats:', error);
        }
    }, []);

    useEffect(() => {
        fetchSystemStats();
    }, [fetchSystemStats]);

    // アカウント制限更新
    const handleUpdateAccountLimit = useCallback(async (onSuccess: () => Promise<void>) => {
        if (!selectedLimitUser) return;

        try {
            const updateData: UpdateAccountLimitData = {
                account_limit: accountLimit,
            };

            await api.put(`/auth/admin/users/${selectedLimitUser.id}/account-limit`, updateData);

            setAccountLimitModalOpened(false);
            setSelectedLimitUser(null);
            setAccountLimit(0);

            await onSuccess();
            await fetchSystemStats();

            notifications.show({
                title: '成功',
                message: 'アカウント制限数を更新しました',
                color: 'green',
            });
        } catch (error) {
            console.error('Error updating account limit:', error);
            const axiosError = error as AxiosError<{ error: string }>;
            notifications.show({
                title: 'エラー',
                message: axiosError.response?.data.error || 'アカウント制限数の更新中にエラーが発生しました',
                color: 'red',
            });
        }
    }, [selectedLimitUser, accountLimit, fetchSystemStats]);

    // システム制限更新
    const handleUpdateSystemLimit = useCallback(async () => {
        try {
            if (systemLimit < totalActiveUsers) {
                notifications.show({
                    title: 'エラー',
                    message: `制限数は現在のアクティブユーザー数（${totalActiveUsers}）以上である必要があります`,
                    color: 'red',
                });
                setSystemLimit(totalActiveUsers);
                return;
            }

            await api.put('/auth/admin/account-limit', {
                account_limit: systemLimit,
            });

            setSystemLimitModalOpened(false);
            notifications.show({
                title: '成功',
                message: 'アカウント制限数を更新しました',
                color: 'green',
            });
            fetchSystemStats();
        } catch (error) {
            console.error('Error updating system limit:', error);
            const axiosError = error as AxiosError<{ error: string }>;
            notifications.show({
                title: 'エラー',
                message: axiosError.response?.data.error || 'アカウント制限数の更新中にエラーが発生しました',
                color: 'red',
            });
        }
    }, [systemLimit, totalActiveUsers, fetchSystemStats]);

    // アカウント制限モーダル閉じる
    const handleCloseAccountLimitModal = useCallback(() => {
        setAccountLimitModalOpened(false);
        setSelectedLimitUser(null);
        setAccountLimit(0);
    }, []);

    // システム制限値変更ハンドラー
    const handleSystemLimitChange = useCallback((newValue: number) => {
        if (newValue < totalActiveUsers) {
            notifications.show({
                title: '警告',
                message: `制限数は現在のアクティブユーザー数（${totalActiveUsers}）以上である必要があります`,
                color: 'yellow',
            });
            setSystemLimit(totalActiveUsers);
        } else {
            setSystemLimit(newValue);
        }
    }, [totalActiveUsers]);

    return {
        systemLimit,
        setSystemLimit,
        totalActiveUsers,
        deletedUsersCount,
        isSuperuser,
        accountLimitModalOpened,
        setAccountLimitModalOpened,
        accountLimit,
        setAccountLimit,
        selectedLimitUser,
        setSelectedLimitUser,
        systemLimitModalOpened,
        setSystemLimitModalOpened,
        fetchSystemStats,
        handleUpdateAccountLimit,
        handleUpdateSystemLimit,
        handleCloseAccountLimitModal,
        handleSystemLimitChange,
    };
}
