'use client';

import { useState } from 'react';
import {
    Container, Title, Text, Card, Group, Stack, SimpleGrid,
    Loader, Center, Pagination, Tabs, Badge, Box,
} from '@mantine/core';
import {
    IconChartBar, IconFileDownload, IconCalendar, IconHistory,
} from '@tabler/icons-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { useMyDashboardSummary, useMyDashboardHistory, useMyDashboardChart } from '@/hooks/useDashboard';
import { COLORS, CARD, FONTS, SECTION_HEADER } from '@/utils/theme';

// ── 스타일 상수 ──────────────────────────────────────────
const CARD_STYLE = {
    ...CARD,
    padding: '24px',
    backgroundColor: COLORS.cardBg,
} as const;

const STAT_VALUE_STYLE = {
    fontSize: '32px',
    fontWeight: 700,
    fontFamily: FONTS.title,
    color: COLORS.text,
    lineHeight: 1.2,
} as const;

const STAT_LABEL_STYLE = {
    fontSize: '13px',
    color: COLORS.textDimmed,
    fontFamily: FONTS.caption,
    letterSpacing: '0.05em',
} as const;

const CHART_COLORS = {
    bar: COLORS.rose,
    barHover: '#c9a6a6',
    grid: 'rgba(0,0,0,0.05)',
} as const;

// ── 요약 카드 ────────────────────────────────────────────

function SummaryCards() {
    const { summary, loading, error } = useMyDashboardSummary();

    if (loading) return <Center py="xl"><Loader color={COLORS.rose} /></Center>;
    if (error || !summary) return <Text c="dimmed" ta="center">{error || 'データがありません'}</Text>;

    const cards = [
        {
            icon: IconChartBar,
            label: '鑑定実行回数',
            value: summary.reading_count,
            color: COLORS.sage,
        },
        {
            icon: IconFileDownload,
            label: 'PDFダウンロード数',
            value: summary.pdf_count,
            color: COLORS.rose,
        },
        {
            icon: IconCalendar,
            label: '最終鑑定日',
            value: summary.last_reading_date
                ? new Date(summary.last_reading_date).toLocaleDateString('ja-JP')
                : '—',
            color: COLORS.accent,
        },
    ];

    return (
        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
            {cards.map((c) => (
                <Card key={c.label} style={CARD_STYLE}>
                    <Group gap="sm" mb="xs">
                        <c.icon size={20} style={{ color: c.color }} stroke={1.5} />
                        <Text style={STAT_LABEL_STYLE}>{c.label}</Text>
                    </Group>
                    <Text style={STAT_VALUE_STYLE}>
                        {typeof c.value === 'number' ? c.value.toLocaleString() : c.value}
                    </Text>
                </Card>
            ))}
        </SimpleGrid>
    );
}

// ── 미니 차트 ────────────────────────────────────────────

function MiniChart() {
    const { chartData, loading, error } = useMyDashboardChart();

    if (loading) return <Center py="lg"><Loader size="sm" color={COLORS.rose} /></Center>;
    if (error) return <Text c="dimmed" size="sm" ta="center">{error}</Text>;

    const data = chartData?.readings ?? [];
    if (data.length === 0) {
        return (
            <Text c="dimmed" size="sm" ta="center" py="lg">
                まだ鑑定の記録がありません
            </Text>
        );
    }

    return (
        <Box style={{ width: '100%', height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                    <XAxis
                        dataKey="month"
                        tick={{ fontSize: 11, fill: COLORS.textDimmed }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fontSize: 11, fill: COLORS.textDimmed }}
                        axisLine={false}
                        tickLine={false}
                        allowDecimals={false}
                    />
                    <Tooltip
                        contentStyle={{
                            borderRadius: '8px',
                            border: `1px solid ${COLORS.accent}`,
                            fontSize: '12px',
                        }}
                        formatter={(value: number) => [`${value}回`, '鑑定数']}
                    />
                    <Bar
                        dataKey="count"
                        fill={CHART_COLORS.bar}
                        radius={[4, 4, 0, 0]}
                        maxBarSize={40}
                    />
                </BarChart>
            </ResponsiveContainer>
        </Box>
    );
}

// ── 利用履歴 ─────────────────────────────────────────────

function HistoryTabs() {
    const [page, setPage] = useState(1);
    const perPage = 20;
    const { history, loading, error } = useMyDashboardHistory(page, perPage);

    if (loading) return <Center py="lg"><Loader size="sm" color={COLORS.rose} /></Center>;
    if (error) return <Text c="dimmed" size="sm" ta="center">{error}</Text>;
    if (!history) return null;

    return (
        <Tabs defaultValue="readings" styles={{
            tab: { fontFamily: FONTS.caption, fontSize: '13px', letterSpacing: '0.05em' },
        }}>
            <Tabs.List>
                <Tabs.Tab value="readings" leftSection={<IconChartBar size={14} />}>
                    鑑定履歴
                    <Badge size="sm" ml={6} color="gray" variant="light">
                        {history.readings.total}
                    </Badge>
                </Tabs.Tab>
                <Tabs.Tab value="pdfs" leftSection={<IconFileDownload size={14} />}>
                    PDFダウンロード
                    <Badge size="sm" ml={6} color="gray" variant="light">
                        {history.pdfs.total}
                    </Badge>
                </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="readings" pt="md">
                {history.readings.items.length === 0 ? (
                    <Text c="dimmed" size="sm" ta="center" py="lg">まだ鑑定の記録がありません</Text>
                ) : (
                    <Stack gap="xs">
                        {history.readings.items.map((item) => (
                            <Card key={item.id} padding="sm" style={{
                                ...CARD,
                                padding: '12px 16px',
                                backgroundColor: COLORS.cardBg,
                            }}>
                                <Group justify="space-between" wrap="nowrap">
                                    <Group gap="xs">
                                        <IconHistory size={14} style={{ color: COLORS.sage }} />
                                        <Text size="sm" fw={500} style={{ fontFamily: FONTS.body }}>
                                            {item.target_year}年{item.target_month}月 鑑定
                                        </Text>
                                    </Group>
                                    <Text size="xs" c="dimmed">
                                        {item.created_at
                                            ? new Date(item.created_at).toLocaleDateString('ja-JP')
                                            : '—'}
                                    </Text>
                                </Group>
                            </Card>
                        ))}
                        {history.readings.total > perPage && (
                            <Center mt="sm">
                                <Pagination
                                    total={Math.ceil(history.readings.total / perPage)}
                                    value={page}
                                    onChange={setPage}
                                    size="sm"
                                    color={COLORS.rose}
                                />
                            </Center>
                        )}
                    </Stack>
                )}
            </Tabs.Panel>

            <Tabs.Panel value="pdfs" pt="md">
                {history.pdfs.items.length === 0 ? (
                    <Text c="dimmed" size="sm" ta="center" py="lg">まだPDFダウンロードの記録がありません</Text>
                ) : (
                    <Stack gap="xs">
                        {history.pdfs.items.map((item) => (
                            <Card key={item.id} padding="sm" style={{
                                ...CARD,
                                padding: '12px 16px',
                                backgroundColor: COLORS.cardBg,
                            }}>
                                <Group justify="space-between" wrap="nowrap">
                                    <Group gap="xs">
                                        <IconFileDownload size={14} style={{ color: COLORS.rose }} />
                                        <Text size="sm" fw={500} style={{ fontFamily: FONTS.body }}>
                                            {item.target_name || 'レポート'}
                                        </Text>
                                    </Group>
                                    <Text size="xs" c="dimmed">
                                        {item.created_at
                                            ? new Date(item.created_at).toLocaleDateString('ja-JP')
                                            : '—'}
                                    </Text>
                                </Group>
                            </Card>
                        ))}
                        {history.pdfs.total > perPage && (
                            <Center mt="sm">
                                <Pagination
                                    total={Math.ceil(history.pdfs.total / perPage)}
                                    value={page}
                                    onChange={setPage}
                                    size="sm"
                                    color={COLORS.rose}
                                />
                            </Center>
                        )}
                    </Stack>
                )}
            </Tabs.Panel>
        </Tabs>
    );
}

// ── メインページ ─────────────────────────────────────────

export default function DashboardPage() {
    return (
        <Container size="md" py="xl">
            <Stack gap="xl">
                {/* ヘッダー */}
                <Box>
                    <Text style={SECTION_HEADER} mb={4}>MY DASHBOARD</Text>
                    <Title
                        order={2}
                        style={{
                            fontFamily: FONTS.title,
                            color: COLORS.text,
                            fontWeight: 600,
                        }}
                    >
                        マイダッシュボード
                    </Title>
                    <Text size="sm" c="dimmed" mt={4}>
                        あなたの鑑定・PDF利用状況をご確認いただけます
                    </Text>
                </Box>

                {/* 要約カード */}
                <SummaryCards />

                {/* ミニチャート */}
                <Card style={CARD_STYLE}>
                    <Text style={SECTION_HEADER} mb="sm">MONTHLY TREND</Text>
                    <Title order={4} mb="md" style={{ fontFamily: FONTS.title, color: COLORS.text }}>
                        鑑定実行数 推移（直近6ヶ月）
                    </Title>
                    <MiniChart />
                </Card>

                {/* 利用履歴 */}
                <Card style={CARD_STYLE}>
                    <Text style={SECTION_HEADER} mb="sm">HISTORY</Text>
                    <Title order={4} mb="md" style={{ fontFamily: FONTS.title, color: COLORS.text }}>
                        利用履歴
                    </Title>
                    <HistoryTabs />
                </Card>
            </Stack>
        </Container>
    );
}
