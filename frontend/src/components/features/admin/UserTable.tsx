
import { Table, Text, Button, Group } from '@mantine/core';
import { IconTrash } from '@tabler/icons-react';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import type { AdminUser } from '@/types/admin';
import { COLORS } from '@/utils/theme';

dayjs.extend(utc);
dayjs.extend(timezone);

interface UserTableProps {
    users: AdminUser[];
    showDeleted: boolean;
    onEdit: (user: AdminUser) => void;
    onDelete: (userId: number) => void;
    onEditAccountLimit?: (user: AdminUser) => void;
    formatDate: (dateStr: string | undefined | null) => string;
}

export function UserTable({ users, showDeleted, onEdit, onDelete, onEditAccountLimit, formatDate }: UserTableProps) {
    return (
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
                                <Text fw={500} c={COLORS.rose}>スーパーユーザー</Text>
                            ) : user.is_admin ? (
                                <Text fw={500} c={COLORS.rose}>管理者</Text>
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
                                    {user.subscription_start
                                        ? (dayjs().tz('Asia/Tokyo').isBefore(dayjs.tz(user.subscription_start, 'Asia/Tokyo'))
                                            ? '利用開始前'
                                            : '利用期間終了')
                                        : '未設定'}
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
                                            onClick={() => onEdit(user)}
                                        >
                                            編集
                                        </Button>
                                        <Button
                                            variant="light"
                                            color="red"
                                            size="xs"
                                            leftSection={<IconTrash size={14} />}
                                            onClick={() => onDelete(user.id)}
                                        >
                                            削除
                                        </Button>
                                        {user.is_admin && onEditAccountLimit && (
                                            <Button
                                                variant="light"
                                                color="grape"
                                                size="xs"
                                                onClick={() => onEditAccountLimit(user)}
                                            >
                                                制限
                                            </Button>
                                        )}
                                    </>
                                )}
                            </Group>
                        </Table.Td>
                    </Table.Tr>
                ))}
            </Table.Tbody>
        </Table>
    );
}
