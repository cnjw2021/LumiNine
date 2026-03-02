'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Container,
  Title,
  Text,
  Card,
  Group,
  Button,
  Select,
  Checkbox,
  Loader,
  Badge,
  Tabs,
  Table,
  Accordion,
  Modal,
  TextInput,
  Alert
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { IconInfoCircle, IconSearch, IconCheck, IconX, IconUserPlus } from '@tabler/icons-react';
import api from '@/utils/api';
import { AxiosError } from 'axios';
import { PermissionGuard } from '@/components/common/auth/PermissionGuard';

interface Permission {
  id: number;
  code: string;
  name: string;
  description: string | null;
  category: string;
}

interface User {
  id: number;
  email: string;
  is_superuser?: boolean;
  is_admin?: boolean;
}

interface UserPermissions {
  user_id: number;
  email: string;
  is_admin: boolean;
  is_superuser: boolean;
  permissions: {
    [category: string]: Permission[];
  };
}

export default function PermissionManagement() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const [allPermissions, setAllPermissions] = useState<{[category: string]: Permission[]}>({});
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<string | null>('users');
  const [error, setError] = useState<string | null>(null);
  const [opened, { open, close }] = useDisclosure(false);
  const [newPermission, setNewPermission] = useState({
    code: '',
    name: '',
    description: '',
    category: ''
  });

  // ユーザー一覧を取得
  const fetchUsers = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/auth/admin/users');
      if (response.data && Array.isArray(response.data.users)) {
        setUsers(response.data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      if ((error as AxiosError).response?.status === 403) {
        router.push('/');
      }
      setError('ユーザー情報の取得に失敗しました');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // 全ての権限を取得
  const fetchAllPermissions = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/permissions');
      if (response.data) {
        // スーパーユーザー以外はシステムカテゴリーを除外
        if (!userPermissions?.is_superuser) {
          const filteredPermissions = { ...response.data };
          delete filteredPermissions['system'];
          setAllPermissions(filteredPermissions);
        } else {
          setAllPermissions(response.data);
        }
      }
    } catch (error) {
      console.error('Error fetching permissions:', error);
      setError('権限情報の取得に失敗しました');
    } finally {
      setIsLoading(false);
    }
  }, [userPermissions?.is_superuser]);

  // ユーザーの権限を取得
  const fetchUserPermissions = useCallback(async (userId: number) => {
    try {
      setIsLoading(true);
      const response = await api.get(`/permissions/${userId}`);
      if (response.data) {
        // スーパーユーザー以外はシステムカテゴリーを除外
        const permissions = { ...response.data };
        if (!permissions.is_superuser) {
          delete permissions.permissions['system'];
        }
        setUserPermissions(permissions);
        
        // 選択された権限を設定
        const selectedCodes: string[] = [];
        Object.values(permissions.permissions as Record<string, Permission[]>).forEach((perms: Permission[]) => {
          perms.forEach((permission: Permission) => {
            selectedCodes.push(permission.code);
          });
        });
        setSelectedPermissions(selectedCodes);
      }
    } catch (error) {
      console.error('Error fetching user permissions:', error);
      setError('ユーザー権限の取得に失敗しました');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 権限の保存
  const savePermissions = async () => {
    if (!selectedUser) return;
    
    try {
      setIsSaving(true);
      await api.post(`/permissions/${selectedUser.id}`, {
        permissions: selectedPermissions
      });
      
      notifications.show({
        title: '保存完了',
        message: '権限設定を保存しました',
        color: 'green',
        icon: <IconCheck />
      });
      
      // 権限を再取得
      await fetchUserPermissions(selectedUser.id);
    } catch (error) {
      console.error('Error saving permissions:', error);
      notifications.show({
        title: 'エラー',
        message: '権限の保存に失敗しました',
        color: 'red',
        icon: <IconX />
      });
    } finally {
      setIsSaving(false);
    }
  };

  // 新しい権限の作成
  const createPermission = async () => {
    try {
      setIsSaving(true);
      await api.post('/permissions', newPermission);
      
      notifications.show({
        title: '作成完了',
        message: '新しい権限を作成しました',
        color: 'green',
        icon: <IconCheck />
      });
      
      // フォームをリセット
      setNewPermission({
        code: '',
        name: '',
        description: '',
        category: ''
      });
      
      // 権限を再取得
      await fetchAllPermissions();
      close();
    } catch (error) {
      console.error('Error creating permission:', error);
      notifications.show({
        title: 'エラー',
        message: '権限の作成に失敗しました',
        color: 'red',
        icon: <IconX />
      });
    } finally {
      setIsSaving(false);
    }
  };

  // 権限の選択状態を切り替え
  const togglePermission = (code: string) => {
    setSelectedPermissions(prev => {
      if (prev.includes(code)) {
        return prev.filter(p => p !== code);
      } else {
        return [...prev, code];
      }
    });
  };

  // 初期データ取得
  useEffect(() => {
    fetchUsers();
    fetchAllPermissions();
  }, [fetchUsers, fetchAllPermissions]);

  // ユーザー選択時に権限を取得
  useEffect(() => {
    if (selectedUser) {
      fetchUserPermissions(selectedUser.id);
    } else {
      setUserPermissions(null);
      setSelectedPermissions([]);
    }
  }, [selectedUser, fetchUserPermissions]);

  // 検索フィルター
  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <PermissionGuard
      permissionCode="permission_manage"
      requireSuperuser={true}
      fallback={
        <Container size="lg" py="xl">
          <Alert icon={<IconInfoCircle />} color="red" title="アクセス権限がありません">
            この機能はスーパーユーザーのみがアクセスできます。
          </Alert>
        </Container>
      }
    >
      <Container size="lg" py="xl">
        {error && (
          <Alert icon={<IconX />} color="red" title="エラー" mb="md">
            {error}
          </Alert>
        )}
        
        <Title order={2} mb="lg">権限管理</Title>
        
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tabs.List mb="md">
            <Tabs.Tab value="users">ユーザー権限</Tabs.Tab>
            <Tabs.Tab value="permissions">権限一覧</Tabs.Tab>
          </Tabs.List>
          
          <Tabs.Panel value="users" pt="md">
            <Group align="flex-start" grow>
              {/* ユーザー一覧 */}
              <Card withBorder shadow="sm" p="md">
                <Card.Section withBorder inheritPadding py="xs">
                  <Group justify="space-between">
                    <Title order={4}>ユーザー一覧</Title>
                    <TextInput
                      placeholder="ユーザーを検索"
                      leftSection={<IconSearch size={16} />}
                      value={searchQuery}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.currentTarget.value)}
                      size="xs"
                      w={200}
                    />
                  </Group>
                </Card.Section>
                
                {isLoading && !selectedUser ? (
                  <Group justify="center" py="xl">
                    <Loader />
                  </Group>
                ) : (
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>メールアドレス</Table.Th>
                        <Table.Th>権限</Table.Th>
                        <Table.Th>操作</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {filteredUsers.map((user) => (
                        <Table.Tr key={user.id} style={{ 
                          backgroundColor: selectedUser?.id === user.id ? 'rgba(75, 163, 227, 0.1)' : undefined 
                        }}>
                          <Table.Td>{user.email}</Table.Td>
                          <Table.Td>
                            {user.is_superuser ? (
                              <Badge color="grape">スーパーユーザー</Badge>
                            ) : user.is_admin ? (
                              <Badge color="pink">管理者</Badge>
                            ) : (
                              <Badge color="blue">一般ユーザー</Badge>
                            )}
                          </Table.Td>
                          <Table.Td>
                            <Button
                              variant="light"
                              size="xs"
                              onClick={() => setSelectedUser(user)}
                              disabled={user.is_superuser}
                            >
                              権限設定
                            </Button>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                )}
              </Card>
              
              {/* 権限設定 */}
              <Card withBorder shadow="sm" p="md">
                <Card.Section withBorder inheritPadding py="xs">
                  <Title order={4}>
                    {selectedUser ? `${selectedUser.email} の権限設定` : '権限設定'}
                  </Title>
                </Card.Section>
                
                {!selectedUser ? (
                  <Text c="dimmed" py="xl" ta="center">
                    左側のリストからユーザーを選択してください
                  </Text>
                ) : isLoading ? (
                  <Group justify="center" py="xl">
                    <Loader />
                  </Group>
                ) : (
                  <>
                    {userPermissions?.is_superuser ? (
                      <Alert icon={<IconInfoCircle />} color="grape" my="md">
                        スーパーユーザーは全ての権限を持っているため、個別の権限設定は不要です。
                      </Alert>
                    ) : (
                      <>
                        <Alert icon={<IconInfoCircle />} color="blue" my="md">
                          管理者は基本的なユーザー管理権限を常に持っています。その他の機能へのアクセス権限を設定できます。
                        </Alert>
                        
                        <Accordion>
                          {Object.entries(allPermissions).map(([category, permissions]) => (
                            <Accordion.Item key={category} value={category}>
                              <Accordion.Control>
                                <Group>
                                  <Text fw={500}>{getCategoryName(category)}</Text>
                                  <Badge>
                                    {permissions.filter(p => selectedPermissions.includes(p.code)).length} / {permissions.length}
                                  </Badge>
                                </Group>
                              </Accordion.Control>
                              <Accordion.Panel>
                                <Table>
                                  <Table.Thead>
                                    <Table.Tr>
                                      <Table.Th>権限名</Table.Th>
                                      <Table.Th>説明</Table.Th>
                                      <Table.Th>有効</Table.Th>
                                    </Table.Tr>
                                  </Table.Thead>
                                  <Table.Tbody>
                                    {permissions.map((permission) => (
                                      <Table.Tr key={permission.id}>
                                        <Table.Td>{permission.name}</Table.Td>
                                        <Table.Td>{permission.description || '-'}</Table.Td>
                                        <Table.Td>
                                          <Checkbox
                                            checked={selectedPermissions.includes(permission.code)}
                                            onChange={() => togglePermission(permission.code)}
                                            disabled={
                                              // 管理者の基本権限は変更不可
                                              userPermissions?.is_admin && 
                                              ['user_view', 'user_create', 'user_edit', 'user_delete'].includes(permission.code)
                                            }
                                          />
                                        </Table.Td>
                                      </Table.Tr>
                                    ))}
                                  </Table.Tbody>
                                </Table>
                              </Accordion.Panel>
                            </Accordion.Item>
                          ))}
                        </Accordion>
                        
                        <Group justify="right" mt="md">
                          <Button
                            onClick={() => setSelectedUser(null)}
                            variant="outline"
                          >
                            キャンセル
                          </Button>
                          <Button
                            onClick={savePermissions}
                            loading={isSaving}
                          >
                            保存
                          </Button>
                        </Group>
                      </>
                    )}
                  </>
                )}
              </Card>
            </Group>
          </Tabs.Panel>
          
          <Tabs.Panel value="permissions" pt="md">
            <Group justify="space-between" mb="md">
              <Title order={4}>権限一覧</Title>
              <Button leftSection={<IconUserPlus size={16} />} onClick={open}>
                新しい権限を作成
              </Button>
            </Group>
            
            {isLoading ? (
              <Group justify="center" py="xl">
                <Loader />
              </Group>
            ) : (
              <Accordion>
                {Object.entries(allPermissions).map(([category, permissions]) => (
                  <Accordion.Item key={category} value={category}>
                    <Accordion.Control>
                      <Group>
                        <Text fw={500}>{getCategoryName(category)}</Text>
                        <Badge>{permissions.length}</Badge>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Table>
                        <Table.Thead>
                          <Table.Tr>
                            <Table.Th>コード</Table.Th>
                            <Table.Th>権限名</Table.Th>
                            <Table.Th>説明</Table.Th>
                          </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                          {permissions.map((permission) => (
                            <Table.Tr key={permission.id}>
                              <Table.Td>
                                <code>{permission.code}</code>
                              </Table.Td>
                              <Table.Td>{permission.name}</Table.Td>
                              <Table.Td>{permission.description || '-'}</Table.Td>
                            </Table.Tr>
                          ))}
                        </Table.Tbody>
                      </Table>
                    </Accordion.Panel>
                  </Accordion.Item>
                ))}
              </Accordion>
            )}
          </Tabs.Panel>
        </Tabs>
        
        {/* 新しい権限作成モーダル */}
        <Modal
          opened={opened}
          onClose={close}
          title="新しい権限を作成"
          size="md"
        >
          <TextInput
            label="権限コード"
            placeholder="例: year_fortune_edit"
            required
            mb="sm"
            value={newPermission.code}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPermission({...newPermission, code: e.currentTarget.value})}
          />
          
          <TextInput
            label="権限名"
            placeholder="例: 年間運勢データ編集"
            required
            mb="sm"
            value={newPermission.name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPermission({...newPermission, name: e.currentTarget.value})}
          />
          
          <TextInput
            label="説明"
            placeholder="この権限の説明"
            mb="sm"
            value={newPermission.description}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPermission({...newPermission, description: e.currentTarget.value})}
          />
          
          <Select
            label="カテゴリ"
            placeholder="権限のカテゴリを選択"
            required
            mb="md"
            data={[
              { value: 'user_management', label: 'ユーザー管理' },
              { value: 'system', label: 'システム' }
            ]}
            value={newPermission.category}
            onChange={(value) => setNewPermission({...newPermission, category: value || ''})}
          />
          
          <Group justify="right">
            <Button variant="outline" onClick={close}>キャンセル</Button>
            <Button 
              onClick={createPermission}
              loading={isSaving}
              disabled={!newPermission.code || !newPermission.name || !newPermission.category}
            >
              作成
            </Button>
          </Group>
        </Modal>
      </Container>
    </PermissionGuard>
  );
}

// カテゴリ名を日本語に変換
function getCategoryName(category: string): string {
  const categoryMap: {[key: string]: string} = {
    'user_management': 'ユーザー管理',
    'system': 'システム'
  };
  
  return categoryMap[category] || category;
} 