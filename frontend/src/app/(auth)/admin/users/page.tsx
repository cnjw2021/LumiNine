'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/utils/api';
import {
  Container,
  Title,
  Button,
  Table,
  TextInput,
  Modal,
  Group,
  Text,
  Stack,
  Switch,
  PasswordInput,
  Paper,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconTrash } from '@tabler/icons-react';
import { AxiosError } from 'axios';
import dayjs from 'dayjs';
import 'dayjs/locale/ja';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import CustomDatePicker from '@/components/common/ui/Datepicker';

// プラグインを設定
dayjs.extend(utc);
dayjs.extend(timezone);
// タイムゾーンをJSTに設定
dayjs.tz.setDefault('Asia/Tokyo');
// ロケールを日本語に設定
dayjs.locale('ja');

interface User {
  id: number;
  name: string;
  email: string;
  is_superuser?: boolean;
  is_admin?: boolean;
  subscription_start?: string;
  subscription_end?: string;
  is_subscription_active?: boolean;
  account_limit?: number;
  remaining_accounts?: number;
  created_accounts_count?: number;
  is_deleted?: boolean;
  deleted_at?: string;
  deleted_by_email?: string;
}

interface UpdateUserData {
  name: string;
  email: string;
  is_admin: boolean;
  subscription_start: string;
  subscription_end: string;
  password?: string;
}

// アカウント制限更新用インターフェース
interface UpdateAccountLimitData {
  account_limit: number;
}

interface DateError {
  startDate?: string;
  endDate?: string;
}

export default function UserManagement() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [showDeleted, setShowDeleted] = useState(false);
  const [createModalOpened, setCreateModalOpened] = useState(false);
  const [editModalOpened, setEditModalOpened] = useState(false);
  const [accountLimitModalOpened, setAccountLimitModalOpened] = useState(false);
  const [systemLimitModalOpened, setSystemLimitModalOpened] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editPassword, setEditPassword] = useState('');
  const [subscriptionStart, setSubscriptionStart] = useState('');
  const [subscriptionEnd, setSubscriptionEnd] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [dateError, setDateError] = useState<DateError>({});
  const [accountLimit, setAccountLimit] = useState<number>(0);
  const [systemLimit, setSystemLimit] = useState<number>(0);
  const [totalActiveUsers, setTotalActiveUsers] = useState<number>(0);
  const [deletedUsersCount, setDeletedUsersCount] = useState<number>(0);
  const [isSuperuser, setIsSuperuser] = useState(false);

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
  }, [fetchUsers, showDeleted]);

  // 現在のユーザーがスーパーユーザーかどうかを確認
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

  // システム全体のアカウント数と制限を取得
  const fetchSystemStats = useCallback(async () => {
    try {
      // システム全体の統計情報を取得
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

  const validateDates = (start: string, end: string): boolean => {
    setDateError({});
    
    if (!start || !end) {
      setDateError({
        startDate: '日付を入力してください',
        endDate: '日付を入力してください'
      });
      return false;
    }

    // YYYY/MM/DD形式のバリデーション
    const datePattern = /^\d{4}\/\d{2}\/\d{2}$/;
    if (!datePattern.test(start) || !datePattern.test(end)) {
      setDateError({
        startDate: '日付は YYYY/MM/DD 形式で入力してください',
        endDate: '日付は YYYY/MM/DD 形式で入力してください'
      });
      return false;
    }

    const startDate = dayjs(start);
    const endDate = dayjs(end);
    
    if (!startDate.isValid() || !endDate.isValid()) {
      setDateError({
        startDate: '有効な日付を入力してください',
        endDate: '有効な日付を入力してください'
      });
      return false;
    }

    if (endDate.isBefore(startDate)) {
      setDateError({
        endDate: '終了日は開始日より後の日付を選択してください'
      });
      return false;
    }

    return true;
  };

  const validateEmail = (email: string): boolean => {
    setEmailError('');
    
    if (!email) {
      setEmailError('メールアドレスを入力してください');
      return false;
    }

    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
      setEmailError('有効なメールアドレスを入力してください');
      return false;
    }

    return true;
  };

  const handleCreateUser = async () => {
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

      if (!newUserName.trim()) {
        notifications.show({
          title: 'エラー',
          message: '名前を入力してください',
          color: 'red',
        });
        return;
      }
      if (!validateEmail(newUserEmail)) {
        return;
      }
      if (!validateDates(subscriptionStart, subscriptionEnd)) {
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

      // 日付のフォーマットを変換（YYYY/MM/DD → YYYY-MM-DD）
      const formattedStart = subscriptionStart.replace(/\//g, '-');
      const formattedEnd = subscriptionEnd.replace(/\//g, '-');

      await api.post('/auth/admin/users', {
        name: newUserName,
        email: newUserEmail,
        password: newUserPassword,
        subscription_start: formattedStart,
        subscription_end: formattedEnd,
        is_admin: isAdmin
      });

      setCreateModalOpened(false);
      setNewUserName('');
      setNewUserEmail('');
      setNewUserPassword('');
      setSubscriptionStart('');
      setSubscriptionEnd('');
      setIsAdmin(false);
      
      // ユーザー作成後に統計情報を再取得
      await fetchSystemStats();
      // ユーザーリストを再取得
      await fetchUsers();
      
      notifications.show({
        title: '成功',
        message: 'ユーザーを作成しました',
        color: 'green',
      });
    } catch (error) {
      console.error('Error creating user:', error);
      const axiosError = error as AxiosError<{error: string}>;
      setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
    }
  };

  const handleDeleteUser = async (userId: number) => {
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

      // ユーザー削除後に統計情報を再取得
      const statsResponse = await api.get('/auth/admin/system-stats');
      setSystemLimit(statsResponse.data.account_limit || 0);
      setTotalActiveUsers(statsResponse.data.total_active_users || 0);
      setDeletedUsersCount(statsResponse.data.deleted_users_count || 0);
      
      // ユーザーリストを再取得
      await fetchUsers();
      
      notifications.show({
        title: '成功',
        message: 'ユーザーを削除しました',
        color: 'green',
      });
    } catch (error) {
      console.error('Error deleting user:', error);
      const axiosError = error as AxiosError<{error: string}>;
      notifications.show({
        title: 'エラー',
        message: axiosError.response?.data.error || '予期せぬエラーが発生しました',
        color: 'red',
      });
    }
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setEditName(user.name);
    setEditEmail(user.email);
    // 日付をスラッシュ形式に変換
    setSubscriptionStart(user.subscription_start ? formatDate(user.subscription_start) : '');
    setSubscriptionEnd(user.subscription_end ? formatDate(user.subscription_end) : '');
    setIsAdmin(user.is_admin || false);
    setEditPassword('');
    setEditModalOpened(true);
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    try {
      if (!editName.trim()) {
        notifications.show({
          title: 'エラー',
          message: '名前を入力してください',
          color: 'red',
        });
        return;
      }
      if (!validateEmail(editEmail)) {
        return;
      }
      if (!validateDates(subscriptionStart, subscriptionEnd)) {
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

      // 日付のフォーマットを変換（YYYY/MM/DD → YYYY-MM-DD）
      const formattedStart = subscriptionStart.replace(/\//g, '-');
      const formattedEnd = subscriptionEnd.replace(/\//g, '-');

      const updateData: UpdateUserData = {
        name: editName,
        email: editEmail,
        is_admin: isAdmin,
        subscription_start: formattedStart,
        subscription_end: formattedEnd,
      };

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
      
      // ユーザー更新後に統計情報を再取得
      await fetchSystemStats();
      // ユーザーリストを再取得
      await fetchUsers();
      
      notifications.show({
        title: '成功',
        message: 'ユーザー情報を更新しました',
        color: 'green',
      });
    } catch (error) {
      console.error('Error updating user:', error);
      const axiosError = error as AxiosError<{error: string}>;
      setEmailError(axiosError.response?.data.error || '予期せぬエラーが発生しました');
    }
  };

  const formatDate = (dateStr: string | undefined | null) => {
    if (!dateStr) return '-';
    // 日付文字列から日付オブジェクトを作成し、指定したフォーマットで表示
    return dayjs(dateStr).format('YYYY/MM/DD');
  };

  const handleCloseCreateModal = () => {
    setCreateModalOpened(false);
    setNewUserName('');
    setNewUserEmail('');
    setNewUserPassword('');
    setSubscriptionStart('');
    setSubscriptionEnd('');
    setIsAdmin(false);
    setEmailError('');
    setDateError({});
  };

  const handleCloseEditModal = () => {
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
  };

  // アカウント制限数を更新する
  const handleUpdateAccountLimit = async () => {
    if (!selectedUser) return;

    try {
      const updateData: UpdateAccountLimitData = {
        account_limit: accountLimit
      };

      await api.put(`/auth/admin/users/${selectedUser.id}/account-limit`, updateData);

      setAccountLimitModalOpened(false);
      setSelectedUser(null);
      setAccountLimit(0);
      // ユーザーリストを再取得
      await fetchUsers();
      // システム統計情報も再取得
      await fetchSystemStats();
      notifications.show({
        title: '成功',
        message: 'アカウント制限数を更新しました',
        color: 'green',
      });
    } catch (error) {
      console.error('Error updating account limit:', error);
      const axiosError = error as AxiosError<{error: string}>;
      notifications.show({
        title: 'エラー',
        message: axiosError.response?.data.error || 'アカウント制限数の更新中にエラーが発生しました',
        color: 'red',
      });
    }
  };

  const handleCloseAccountLimitModal = () => {
    setAccountLimitModalOpened(false);
    setSelectedUser(null);
    setAccountLimit(0);
  };

  // システム全体の制限数を更新
  const handleUpdateSystemLimit = async () => {
    try {
      // 現在のアクティブユーザー数より少ない値は設定できないようにする
      if (systemLimit < totalActiveUsers) {
        notifications.show({
          title: 'エラー',
          message: `制限数は現在のアクティブユーザー数（${totalActiveUsers}）以上である必要があります`,
          color: 'red',
        });
        setSystemLimit(totalActiveUsers);
        return;
      }

      // 正しいAPIエンドポイントを使用
      await api.put('/auth/admin/account-limit', {
        account_limit: systemLimit
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
      const axiosError = error as AxiosError<{error: string}>;
      notifications.show({
        title: 'エラー',
        message: axiosError.response?.data.error || 'アカウント制限数の更新中にエラーが発生しました',
        color: 'red',
      });
    }
  };

  return (
    <Container size="lg" mt="xl">
      <Group justify="space-between" mb="xl">
        <Title order={2}>ユーザー管理</Title>
        <Group>
          <Switch
            label="削除済みユーザーを表示"
            checked={showDeleted}
            onChange={(event) => setShowDeleted(event.currentTarget.checked)}
          />
          <Button 
            onClick={() => setCreateModalOpened(true)}
            variant="gradient"
            gradient={{ from: 'pink', to: 'grape' }}
            disabled={systemLimit <= totalActiveUsers}
            title={systemLimit <= totalActiveUsers ? "アカウント制限数に達しているため、新規ユーザーを作成できません" : ""}
          >
            新規ユーザー作成
          </Button>
        </Group>
      </Group>

      {isSuperuser && (
        <Paper withBorder p="md" mb="xl" radius="md" shadow="sm">
          <Group justify="apart" mb="xs">
            <Title order={4}>システム利用状況</Title>
            <Group>
              <Button 
                variant="light" 
                size="sm"
                onClick={() => setSystemLimitModalOpened(true)}
              >
                アカウント制限数変更
              </Button>
            </Group>
          </Group>
          <Group grow>
            <Paper withBorder p="md" radius="md">
              <Text size="sm" c="dimmed">現在の利用アカウント数</Text>
              <Text size="xl" fw={700}>{totalActiveUsers}</Text>
            </Paper>
            <Paper withBorder p="md" radius="md">
              <Text size="sm" c="dimmed">削除済みアカウント数</Text>
              <Text size="xl" fw={700}>{deletedUsersCount}</Text>
            </Paper>
            <Paper withBorder p="md" radius="md">
              <Text size="sm" c="dimmed">アカウント制限数</Text>
              <Text size="xl" fw={700}>{systemLimit}</Text>
            </Paper>
            <Paper withBorder p="md" radius="md">
              <Text size="sm" c="dimmed">残り利用可能数</Text>
              <Text 
                size="xl" 
                fw={700} 
                c={systemLimit - totalActiveUsers > 5 ? 'green' : systemLimit - totalActiveUsers > 0 ? 'orange' : 'red'}
              >
                {systemLimit - totalActiveUsers >= 0 ? 
                  (systemLimit - totalActiveUsers) : 
                  `0（超過: ${Math.abs(systemLimit - totalActiveUsers)}）`}
              </Text>
            </Paper>
          </Group>
        </Paper>
      )}

      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: '5%' }}>ID</Table.Th>
            <Table.Th style={{ width: '15%' }}>名前</Table.Th>
            <Table.Th style={{ width: '20%' }}>メールアドレス</Table.Th>
            <Table.Th style={{ width: '10%' }}>権限</Table.Th>
            <Table.Th style={{ width: '12%' }}>利用開始日</Table.Th>
            <Table.Th style={{ width: '12%' }}>利用終了日</Table.Th>
            <Table.Th style={{ width: '8%' }}>ステータス</Table.Th>
            {showDeleted && (
              <>
                <Table.Th style={{ width: '10%' }}>削除日時</Table.Th>
                <Table.Th style={{ width: '10%' }}>削除者</Table.Th>
              </>
            )}
            <Table.Th style={{ width: showDeleted ? '8%' : '13%' }}>操作</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {users.map((user) => (
            <Table.Tr key={user.id} style={{
              backgroundColor: user.is_deleted ? 'rgba(234, 234, 234, 0.5)' : undefined
            }}>
              <Table.Td>{user.id}</Table.Td>
              <Table.Td>{user.name || '-'}</Table.Td>
              <Table.Td>{user.email}</Table.Td>
              <Table.Td>
                {user.is_superuser ? (
                  <Text fw={500} c="grape">スーパーユーザー</Text>
                ) : user.is_admin ? (
                  <Text fw={500} c="pink">管理者</Text>
                ) : (
                  <Text>一般ユーザー</Text>
                )}
              </Table.Td>
              <Table.Td>{formatDate(user.subscription_start)}</Table.Td>
              <Table.Td>{formatDate(user.subscription_end)}</Table.Td>
              <Table.Td>
                {user.is_deleted ? (
                  <Text fw={500} c="gray">削除済み</Text>
                ) : user.is_subscription_active ? (
                  <Text fw={500} c="green">有効</Text>
                ) : (
                  <Text fw={500} c="red">
                    {dayjs().tz('Asia/Tokyo').isBefore(dayjs.tz(user.subscription_start, 'Asia/Tokyo'))
                      ? '利用開始前'
                      : '利用期間終了'}
                  </Text>
                )}
              </Table.Td>
              {showDeleted && (
                <>
                  <Table.Td>{formatDate(user.deleted_at)}</Table.Td>
                  <Table.Td>{user.deleted_by_email || '-'}</Table.Td>
                </>
              )}
              <Table.Td>
                <Group gap="xs">
                  {!user.is_superuser && !user.is_deleted && (
                    <>
                      <Button
                        variant="light"
                        color="blue"
                        size="xs"
                        onClick={() => handleEditUser(user)}
                      >
                        編集
                      </Button>
                      <Button
                        variant="light"
                        color="red"
                        size="xs"
                        leftSection={<IconTrash size={14} />}
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        削除
                      </Button>
                    </>
                  )}
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>

      <Modal
        opened={createModalOpened}
        onClose={handleCloseCreateModal}
        title="新規ユーザー作成"
        size="md"
      >
        <Stack>
          {systemLimit <= totalActiveUsers && (
            <Text c="red" size="sm" fw={500} mb="md">
              アカウント制限数に達しているため、新規ユーザーを作成できません。
              制限数を増やすか、不要なアカウントを削除してください。
            </Text>
          )}
          <TextInput
            label="名前"
            placeholder="ユーザー名を入力"
            value={newUserName}
            onChange={(event) => setNewUserName(event.currentTarget.value)}
            required
          />
          <TextInput
            label="メールアドレス"
            placeholder="example@example.com"
            value={newUserEmail}
            onChange={(event) => setNewUserEmail(event.currentTarget.value)}
            error={emailError}
            required
          />
          <PasswordInput
            label="パスワード"
            value={newUserPassword}
            onChange={(event) => setNewUserPassword(event.currentTarget.value)}
            error={newUserPassword.length > 0 && newUserPassword.length < 8 ? "パスワードは8文字以上である必要があります" : ""}
            required
          />
          <CustomDatePicker
            label="利用開始日"
            value={subscriptionStart}
            onChange={setSubscriptionStart}
            error={dateError.startDate}
          />
          <CustomDatePicker
            label="利用終了日"
            value={subscriptionEnd}
            onChange={setSubscriptionEnd}
            error={dateError.endDate}
          />
          <Switch
            label="管理者権限"
            checked={isAdmin}
            onChange={(event) => setIsAdmin(event.currentTarget.checked)}
          />
          {emailError && (
            <Text c="red" size="sm">
              {emailError}
            </Text>
          )}
          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={handleCloseCreateModal}>
              キャンセル
            </Button>
            <Button 
              onClick={handleCreateUser}
              variant="gradient"
              gradient={{ from: 'pink', to: 'grape' }}
              disabled={systemLimit <= totalActiveUsers}
            >
              作成
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal
        opened={editModalOpened}
        onClose={handleCloseEditModal}
        title="ユーザー情報の編集"
        size="md"
      >
        <Stack>
          <TextInput
            label="名前"
            placeholder="ユーザー名を入力"
            value={editName}
            onChange={(event) => setEditName(event.currentTarget.value)}
            required
          />
          <TextInput
            label="メールアドレス"
            placeholder="example@example.com"
            value={editEmail}
            onChange={(event) => setEditEmail(event.currentTarget.value)}
            error={emailError}
            required
          />
          <PasswordInput
            label="パスワード（変更する場合のみ）"
            value={editPassword}
            onChange={(event) => setEditPassword(event.currentTarget.value)}
            error={editPassword.length > 0 && editPassword.length < 8 ? "パスワードは8文字以上である必要があります" : ""}
          />
          <CustomDatePicker
            label="利用開始日"
            value={subscriptionStart}
            onChange={setSubscriptionStart}
            error={dateError.startDate}
          />
          <CustomDatePicker
            label="利用終了日"
            value={subscriptionEnd}
            onChange={setSubscriptionEnd}
            error={dateError.endDate}
          />
          <Switch
            label="管理者権限"
            checked={isAdmin}
            onChange={(event) => setIsAdmin(event.currentTarget.checked)}
          />
          {emailError && (
            <Text c="red" size="sm">
              {emailError}
            </Text>
          )}
          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={handleCloseEditModal}>
              キャンセル
            </Button>
            <Button 
              onClick={handleUpdateUser}
              variant="gradient"
              gradient={{ from: 'pink', to: 'grape' }}
            >
              更新
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* アカウント制限数編集モーダル */}
      <Modal
        opened={accountLimitModalOpened}
        onClose={handleCloseAccountLimitModal}
        title="アカウント制限数の編集"
        centered
      >
        <Stack>
          <Text>
            管理者: {selectedUser?.email}
          </Text>
          <TextInput
            label="アカウント作成制限数"
            placeholder="制限数を入力"
            value={accountLimit}
            onChange={(e) => setAccountLimit(Number(e.target.value))}
            type="number"
            min={0}
            required
          />
          {selectedUser?.created_accounts_count !== undefined && (
            <Text size="sm" c="dimmed">
              現在の作成済みアカウント数: {selectedUser.created_accounts_count}
            </Text>
          )}
          <Group justify="flex-end" mt="md">
            <Button variant="outline" onClick={handleCloseAccountLimitModal}>キャンセル</Button>
            <Button onClick={handleUpdateAccountLimit}>更新</Button>
          </Group>
        </Stack>
      </Modal>

      {/* システム全体の制限数編集モーダル */}
      <Modal
        opened={systemLimitModalOpened}
        onClose={() => setSystemLimitModalOpened(false)}
        title="アカウント制限数編集"
        centered
      >
        <Stack>
          <Text>
            システム全体で利用可能なアカウント数の上限を設定します。
            この数値は、管理者を含む全てのユーザーアカウントに適用されます。
          </Text>
          <TextInput
            label="アカウント制限数"
            placeholder="制限数を入力"
            value={systemLimit}
            onChange={(e) => {
              const newValue = Number(e.target.value);
              // 現在のアクティブユーザー数より少ない値は設定できないようにする
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
            }}
            type="number"
            min={totalActiveUsers}
            required
          />
          {totalActiveUsers > 0 && (
            <Text size="sm" c="dimmed">
              現在の利用アカウント数: {totalActiveUsers}
            </Text>
          )}
          <Group justify="flex-end" mt="md">
            <Button variant="outline" onClick={() => setSystemLimitModalOpened(false)}>キャンセル</Button>
            <Button onClick={handleUpdateSystemLimit}>更新</Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
} 