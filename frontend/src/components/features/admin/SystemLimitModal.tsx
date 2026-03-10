
import { Modal, Stack, Text, TextInput, Button, Group } from '@mantine/core';

interface SystemLimitModalProps {
    opened: boolean;
    onClose: () => void;
    systemLimit: number;
    totalActiveUsers: number;
    onSystemLimitChange: (value: number) => void;
    onSubmit: () => void;
}

export function SystemLimitModal({
    opened,
    onClose,
    systemLimit,
    totalActiveUsers,
    onSystemLimitChange,
    onSubmit,
}: SystemLimitModalProps) {
    return (
        <Modal
            opened={opened}
            onClose={onClose}
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
                        const value = e.currentTarget.valueAsNumber;
                        if (Number.isNaN(value)) return;
                        const intValue = Math.trunc(value);
                        onSystemLimitChange(intValue);
                    }}
                    type="number"
                    step={1}
                    min={totalActiveUsers}
                    required
                />
                {totalActiveUsers > 0 && (
                    <Text size="sm" c="dimmed">
                        現在の利用アカウント数: {totalActiveUsers}
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
