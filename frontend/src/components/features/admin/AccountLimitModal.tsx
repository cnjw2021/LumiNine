
import { Modal, Stack, Text, TextInput, Button, Group } from '@mantine/core';
import type { AdminUser } from '@/types/admin';

interface AccountLimitModalProps {
    opened: boolean;
    onClose: () => void;
    selectedUser: AdminUser | null;
    accountLimit: number;
    onAccountLimitChange: (value: number) => void;
    onSubmit: () => void;
}

export function AccountLimitModal({
    opened,
    onClose,
    selectedUser,
    accountLimit,
    onAccountLimitChange,
    onSubmit,
}: AccountLimitModalProps) {
    return (
        <Modal
            opened={opened}
            onClose={onClose}
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
                    onChange={(e) => {
                        const value = e.currentTarget.valueAsNumber;
                        if (Number.isNaN(value)) return;
                        const intValue = Math.trunc(value);
                        onAccountLimitChange(intValue);
                    }}
                    type="number"
                    min={0}
                    step={1}
                    required
                />
                {selectedUser?.created_accounts_count !== undefined && (
                    <Text size="sm" c="dimmed">
                        現在の作成済みアカウント数: {selectedUser.created_accounts_count}
                    </Text>
                )}
                <Group justify="flex-end" mt="md">
                    <Button variant="outline" onClick={onClose}>キャンセル</Button>
                    <Button onClick={onSubmit}>更新</Button>
                </Group>
            </Stack>
        </Modal>
    );
}
