'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import { notifications } from '@mantine/notifications';
import { AxiosError } from 'axios';
import type { AdminUser, UpdateUserData, DateError } from '@/types/admin';
import {
    validateDates,
    validateEmail,
    formatDateSlash,
    formatDateForApi,
} from '@/utils/adminValidation';

interface UseUserManagementReturn {
    // ユーザーリスト
    users: AdminUser[];
    showDeleted: boolean;
    setShowDeleted: (v: boolean) => void;
    fetchUsers: () => Promise<void>;

    // 作成モーダル
    createModalOpened: boolean;
    setCreateModalOpened: (v: boolean) => void;
    newUserName: string;
    setNewUserName: (v: string) => void;
    newUserEmail: string;
    setNewUserEmail: (v: string) => void;
    newUserPassword: string;
    setNewUserPassword: (v: string) => void;

    // 編集モーダル
    editModalOpened: boolean;
    selectedUser: AdminUser | null;
    editName: string;
    setEditName: (v: string) => void;
    editEmail: string;
    setEditEmail: (v: string) => void;
    editPassword: string;
    setEditPassword: (v: string) => void;

    // 共通フォーム状態
    subscriptionStart: string;
    setSubscriptionStart: (v: string) => void;
    subscriptionEnd: string;
    setSubscriptionEnd: (v: string) => void;
    isAdmin: boolean;
    setIsAdmin: (v: boolean) => void;
    emailError: string;
    dateError: DateError;

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

export function useUserManagement(): UseUserManagementReturn {
    const router = useRouter();

    // ユーザーリスト
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [showDeleted, setShowDeleted] = useState(false);

    // 作成モーダル
    const [createModalOpened, setCreateModalOpened] = useState(false);
    const [newUserName, setNewUserName] = useState('');
    const [newUserEmail, setNewUserEmail] = useState('');
    const [newUserPassword, setNewUserPassword] = useState('');

    // 編集モーダル
    const [editModalOpened, setEditModalOpened] = useState(false);
    const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
    const [editName, setEditName] = useState('');
    const [editEmail, setEditEmail] = useState('');
    const [editPassword, setEditPassword] = useState('');

    // 共通フォーム状態
    const [subscriptionStart, setSubscriptionStart] = useState('');
    const [subscriptionEnd, setSubscriptionEnd] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [emailError, setEmailError] = useState('');
    const [dateError, setDateError] = useState<DateError>({});

    // ユーザーリスト取得
    const fetchUsers = useCallback(async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await api.get(`/auth/admin/users?show_deleted=${showDeleted}`);
            if (response.data && Array.isArray(response.data.users)) {
                setUsers(response.data.users);
            } else {
                console.error('Invalid response format:', response.data);
                setUsers([]);
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            if ((error as AxiosError).response?.status === 403) {
                router.push('/');
            }
            setUsers([]);
        }
    }, [router, showDeleted]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // ユーザー作成
    const handleCreateUser = useCallback(async (
        systemLimit: number,
        totalActiveUsers: number,
        onSuccess: () => Promise<void>,
    ) => {
        try {
            // バリデーション前にエラー状態をクリア
            setEmailError('');
            setDateError({});

            // システム上限チェック
            if (systemLimit <= totalActiveUsers) {
                notifications.show({
                    title: 'エラー',
                    message: 'アカウント制限数に達しているため、新規ユーザーを作成できません',
                    color: 'red',
                });
                return;
            }

            if (!newUserName.trim()) {
                notifications.show({
                    title: 'エラー',
                    message: '名前を入力してください',
                    color: 'red',
                });
                return;
            }

            const emailResult = validateEmail(newUserEmail);
            if (!emailResult.valid) {
                setEmailError(emailResult.error);
                return;
            }

            const dateResult = validateDates(subscriptionStart, subscriptionEnd);
            if (!dateResult.valid) {
                setDateError(dateResult.errors);
                return;
            }

            if (newUserPassword.length < 8) {
                notifications.show({
                    title: 'エラー',
                    message: 'パスワードは8文字以上である必要があります',
                    color: 'red',
                });
                return;
            }

            const token = localStorage.getItem('token');
            if (!token) {
                router.push('/login');
                return;
            }

            await api.post('/auth/admin/users', {
                name: newUserName,
                email: newUserEmail,
                password: newUserPassword,
                subscription_start: formatDateForApi(subscriptionStart),
                subscription_end: formatDateForApi(subscriptionEnd),
                is_admin: isAdmin,
            });

            setCreateModalOpened(false);
            setNewUserName('');
            setNewUserEmail('');
            setNewUserPassword('');
            setSubscriptionStart('');
            setSubscriptionEnd('');
            setIsAdmin(false);
            setEmailError('');
            setDateError({});

            await onSuccess();
            await fetchUsers();

            notifications.show({
                title: '成功',
                message: 'ユーザーを作成しました',
                color: 'green',
            });
        } catch (error) {
            console.error('Error creating user:', error);
            const axiosError = error as AxiosError<{ error: string }>;
            setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
        }
    }, [newUserName, newUserEmail, newUserPassword, subscriptionStart, subscriptionEnd, isAdmin, router, fetchUsers]);

    // ユーザー編集モーダルを開く
    const handleEditUser = useCallback((user: AdminUser) => {
        setSelectedUser(user);
        setEditName(user.name);
        setEditEmail(user.email);
        setSubscriptionStart(user.subscription_start ? formatDateSlash(user.subscription_start) : '');
        setSubscriptionEnd(user.subscription_end ? formatDateSlash(user.subscription_end) : '');
        setIsAdmin(user.is_admin || false);
        setEditPassword('');
        setEditModalOpened(true);
    }, []);

    // ユーザー更新
    const handleUpdateUser = useCallback(async (onSuccess: () => Promise<void>) => {
        if (!selectedUser) return;

        try {
            // バリデーション前にエラー状態をクリア
            setEmailError('');
            setDateError({});

            if (!editName.trim()) {
                notifications.show({
                    title: 'エラー',
                    message: '名前を入力してください',
                    color: 'red',
                });
                return;
            }

            const emailResult = validateEmail(editEmail);
            if (!emailResult.valid) {
                setEmailError(emailResult.error);
                return;
            }

            const dateResult = validateDates(subscriptionStart, subscriptionEnd);
            if (!dateResult.valid) {
                setDateError(dateResult.errors);
                return;
            }

            if (editPassword && editPassword.length < 8) {
                notifications.show({
                    title: 'エラー',
                    message: 'パスワードは8文字以上である必要があります',
                    color: 'red',
                });
                return;
            }

            const updateData: UpdateUserData = {
                name: editName,
                email: editEmail,
                subscription_start: formatDateForApi(subscriptionStart),
                subscription_end: formatDateForApi(subscriptionEnd),
            };

            // is_admin はスーパーユーザーのみ変更可能（バックエンドが非スーパーユーザーの is_admin キー存在を 403 で拒否）
            if (selectedUser && isAdmin !== selectedUser.is_admin) {
                updateData.is_admin = isAdmin;
            }

            if (editPassword) {
                updateData.password = editPassword;
            }

            await api.put(`/auth/admin/users/${selectedUser.id}`, updateData);

            setEditModalOpened(false);
            setSelectedUser(null);
            setEditEmail('');
            setEditPassword('');
            setSubscriptionStart('');
            setSubscriptionEnd('');
            setIsAdmin(false);
            setEmailError('');
            setDateError({});

            await onSuccess();
            await fetchUsers();

            notifications.show({
                title: '成功',
                message: 'ユーザー情報を更新しました',
                color: 'green',
            });
        } catch (error) {
            console.error('Error updating user:', error);
            const axiosError = error as AxiosError<{ error: string }>;
            setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
        }
    }, [selectedUser, editName, editEmail, editPassword, subscriptionStart, subscriptionEnd, isAdmin, router, fetchUsers]);

    // ユーザー削除
    const handleDeleteUser = useCallback(async (userId: number, onSuccess: () => Promise<void>) => {
        if (!confirm('このユーザーを削除してもよろしいですか？')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                router.push('/login');
                return;
            }

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
    }, [router, fetchUsers]);

    // モーダル閉じる
    const handleCloseCreateModal = useCallback(() => {
        setCreateModalOpened(false);
        setNewUserName('');
        setNewUserEmail('');
        setNewUserPassword('');
        setSubscriptionStart('');
        setSubscriptionEnd('');
        setIsAdmin(false);
        setEmailError('');
        setDateError({});
    }, []);

    const handleCloseEditModal = useCallback(() => {
        setEditModalOpened(false);
        setSelectedUser(null);
        setEditName('');
        setEditEmail('');
        setEditPassword('');
        setSubscriptionStart('');
        setSubscriptionEnd('');
        setIsAdmin(false);
        setEmailError('');
        setDateError({});
    }, []);

    return {
        users,
        showDeleted,
        setShowDeleted,
        fetchUsers,
        createModalOpened,
        setCreateModalOpened,
        newUserName,
        setNewUserName,
        newUserEmail,
        setNewUserEmail,
        newUserPassword,
        setNewUserPassword,
        editModalOpened,
        selectedUser,
        editName,
        setEditName,
        editEmail,
        setEditEmail,
        editPassword,
        setEditPassword,
        subscriptionStart,
        setSubscriptionStart,
        subscriptionEnd,
        setSubscriptionEnd,
        isAdmin,
        setIsAdmin,
        emailError,
        dateError,
        handleCreateUser,
        handleEditUser,
        handleUpdateUser,
        handleDeleteUser,
        handleCloseCreateModal,
        handleCloseEditModal,
        formatDate: formatDateSlash,
    };
}
