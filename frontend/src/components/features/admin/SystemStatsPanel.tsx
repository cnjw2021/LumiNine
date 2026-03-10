
import { Paper, Group, Title, Button, Text } from '@mantine/core';
import { COLORS, FONTS, CARD } from '@/utils/theme';

interface SystemStatsPanelProps {
    totalActiveUsers: number;
    deletedUsersCount: number;
    systemLimit: number;
    onEditLimit: () => void;
}

export function SystemStatsPanel({
    totalActiveUsers,
    deletedUsersCount,
    systemLimit,
    onEditLimit,
}: SystemStatsPanelProps) {
    const remaining = systemLimit - totalActiveUsers;

    return (
        <Paper p="md" mb="xl" radius={CARD.borderRadius} shadow="none" style={{ border: CARD.border, boxShadow: CARD.boxShadow }}>
            <Group justify="apart" mb="xs">
                <Title order={4} c={COLORS.text} style={{ fontFamily: FONTS.title, fontWeight: 'normal' }}>システム利用状況</Title>
                <Group>
                    <Button
                        variant="light"
                        size="sm"
                        onClick={onEditLimit}
                    >
                        アカウント制限数変更
                    </Button>
                </Group>
            </Group>
            <Group grow>
                <Paper p="md" radius="md" style={{ border: CARD.border }}>
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
                        c={remaining > 5 ? 'green' : remaining > 0 ? 'orange' : 'red'}
                    >
                        {remaining >= 0
                            ? remaining
                            : `0（超過: ${Math.abs(remaining)}）`}
                    </Text>
                </Paper>
            </Group>
        </Paper>
    );
}
