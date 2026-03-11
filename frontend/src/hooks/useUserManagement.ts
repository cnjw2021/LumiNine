'use client';

import { useState, useEffect, useCallback } from 'react';
import api from '@/utils/api';
import { notifications } from '@mantine/notifications';
import { AxiosError } from 'axios';
import type { AdminUser, UpdateUserData } from '@/types/admin';
import { formatDateSlash, formatDateForApi } from '@/utils/adminValidation';
import { useUserFormState, UseUserFormStateReturn } from '@/hooks/useUserFormState';

// ── 型定義 ──────────────────────────────────────────

interface UseUserManagementReturn {
    // ユーザーリスト
    users: AdminUser[];
    showDeleted: boolean;
    setShowDeleted: (v: boolean) => void;
    fetchUsers: () => Promise<void>;

    // 作成フォーム
    createModalOpened: boolean;
    setCreateModalOpened: (v: boolean) => void;
    createForm: UseUserFormStateReturn;

    // 編集フォーム
    editModalOpened: boolean;
    selectedUser: AdminUser | null;
    editForm: UseUserFormStateReturn;

    // ハンドラー
    handleCreateUser: (systemLimit: number, totalActiveUsers: number, onSuccess: () => Promise<void>) => Promise<void>;
    handleEditUser: (user: AdminUser) => void;
    handleUpdateUser: (onSuccess: () => Promise<void>) => Promise<void>;
    handleDeleteUser: (userId: number, onSuccess: () => Promise<void>) => Promise<void>;
    handleCloseCreateModal: () => void;
    handleCloseEditModal: () => void;

    // ユーティリティ
    formatDate: (dateStr: string | undefined | null) => string;
}

// ── フック ──────────────────────────────────────────

export function useUserManagement(): UseUserManagementReturn {

    // ユーザーリスト
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [showDeleted, setShowDeleted] = useState(false);

    // モーダル状態
    const [createModalOpened, setCreateModalOpened] = useState(false);
    const [editModalOpened, setEditModalOpened] = useState(false);
    const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);

    // 独立したフォーム状態（create/edit が互いに干渉しない）
    const createForm = useUserFormState();
    const editForm = useUserFormState();

    // ── ユーザーリスト取得 ────────────────────────────

    const fetchUsers = useCallback(async () => {
        try {
            const response = await api.get(`/auth/admin/users?show_deleted=${showDeleted}`);
            if (response.data && Array.isArray(response.data.users)) {
                setUsers(response.data.users);
            } else {
                console.error('Invalid response format:', response.data);
                setUsers([]);
            }
        } catch (error) {
            const axiosError = error as AxiosError;
            // 401 は API インターセプターによるリダイレクトで静かに処理する
            if (axiosError.response?.status === 401) {
                return;
            }
            console.error('Error fetching users:', error);
            setUsers([]);
        }
    }, [showDeleted]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // ── ユーザー作成 ────────────────────────────────

    const handleCreateUser = useCallback(async (
        systemLimit: number,
        totalActiveUsers: number,
        onSuccess: () => Promise<void>,
    ) => {
        try {
            // システム上限チェック
            if (systemLimit <= totalActiveUsers) {
                notifications.show({
                    title: 'エラー',
                    message: 'アカウント制限数に達しているため、新規ユーザーを作成できません',
                    color: 'red',
                });
                return;
            }

            if (!createForm.validate({ requirePassword: true })) {
                return;
            }

            const { name, email, password, subscriptionStart, subscriptionEnd, isAdmin } = createForm.fields;

            await api.post('/auth/admin/users', {
                name,
                email,
                password,
                subscription_start: formatDateForApi(subscriptionStart),
                subscription_end: formatDateForApi(subscriptionEnd),
                is_admin: isAdmin,
            });

            setCreateModalOpened(false);
            createForm.reset();

            await onSuccess();
            await fetchUsers();

            notifications.show({
                title: '成功',
                message: 'ユーザーを作成しました',
                color: 'green',
            });
        } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            if (axiosError.response?.status === 401) {
                // 認証エラー時はグローバルな interceptor に処理を任せる
                return;
            }
            console.error('Error creating user:', error);
            createForm.setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
        }
    }, [createForm.validate, createForm.fields, createForm.reset, createForm.setEmailError, fetchUsers]);

    // ── ユーザー編集モーダルを開く ──────────────────

    const handleEditUser = useCallback((user: AdminUser) => {
        setSelectedUser(user);
        editForm.setName(user.name);
        editForm.setEmail(user.email);
        editForm.setSubscriptionStart(user.subscription_start ? formatDateSlash(user.subscription_start) : '');
        editForm.setSubscriptionEnd(user.subscription_end ? formatDateSlash(user.subscription_end) : '');
        editForm.setIsAdmin(user.is_admin || false);
        editForm.setPassword('');
        setEditModalOpened(true);
    }, [editForm.setName, editForm.setEmail, editForm.setSubscriptionStart, editForm.setSubscriptionEnd, editForm.setIsAdmin, editForm.setPassword]);

    // ── ユーザー更新 ────────────────────────────────

    const handleUpdateUser = useCallback(async (onSuccess: () => Promise<void>) => {
        if (!selectedUser) return;

        try {
            if (!editForm.validate()) {
                return;
            }

            const { name, email, password, subscriptionStart, subscriptionEnd, isAdmin } = editForm.fields;

            const updateData: UpdateUserData = {
                name,
                email,
                subscription_start: formatDateForApi(subscriptionStart),
                subscription_end: formatDateForApi(subscriptionEnd),
            };

            // is_admin はスーパーユーザーのみ変更可能（バックエンドが非スーパーユーザーの is_admin キー存在を 403 で拒否）
            if (selectedUser && isAdmin !== selectedUser.is_admin) {
                updateData.is_admin = isAdmin;
            }

            if (password) {
                updateData.password = password;
            }

            await api.put(`/auth/admin/users/${selectedUser.id}`, updateData);

            setEditModalOpened(false);
            setSelectedUser(null);
            editForm.reset();

            await onSuccess();
            await fetchUsers();

            notifications.show({
                title: '成功',
                message: 'ユーザー情報を更新しました',
                color: 'green',
            });
        } catch (error) {
            const axiosError = error as AxiosError<{ error: string }>;
            if (axiosError.response?.status === 401) {
                return;
            }
            console.error('Error updating user:', error);
            editForm.setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
        }
    }, [selectedUser, editForm.validate, editForm.fields, editForm.reset, editForm.setEmailError, fetchUsers]);

    // ── ユーザー削除 ────────────────────────────────

    const handleDeleteUser = useCallback(async (userId: number, onSuccess: () => Promise<void>) => {
        if (!confirm('このユーザーを削除してもよろしいですか？')) {
            return;
        }

        try {
            await api.delete(`/auth/admin/users/${userId}`);

            await onSuccess();
            await fetchUsers();

            notifications.show({
                title: '成功',
                message: 'ユーザーを削除しました',
                color: 'green',
            });
        } catch (error) {
            console.error('Error deleting user:', error);
            const axiosError = error as AxiosError<{ error: string }>;
            notifications.show({
                title: 'エラー',
                message: axiosError.response?.data.error || '予期せぬエラーが発生しました',
                color: 'red',
            });
        }
    }, [fetchUsers]);

    // ── モーダル閉じる ──────────────────────────────

    const handleCloseCreateModal = useCallback(() => {
        setCreateModalOpened(false);
        createForm.reset();
    }, [createForm.reset]);

    const handleCloseEditModal = useCallback(() => {
        setEditModalOpened(false);
        setSelectedUser(null);
        editForm.reset();
    }, [editForm.reset]);

    // ── return ──────────────────────────────────────

    return {
        users,
        showDeleted,
        setShowDeleted,
        fetchUsers,
        createModalOpened,
        setCreateModalOpened,
        createForm,
        editModalOpened,
        selectedUser,
        editForm,
        handleCreateUser,
        handleEditUser,
        handleUpdateUser,
        handleDeleteUser,
        handleCloseCreateModal,
        handleCloseEditModal,
        formatDate: formatDateSlash,
    };
}
