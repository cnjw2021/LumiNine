'use client';

import { useState, useMemo } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';
import {
    Container, Title, Text, Card, Group, Stack, SimpleGrid,
    Loader, Center, Pagination, Box, SegmentedControl,
    Table, TextInput, Select,
} from '@mantine/core';
import {
    IconChartBar, IconFileDownload, IconUsers,
    IconSearch, IconSortAscending, IconSortDescending,
} from '@tabler/icons-react';
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import {
    useAdminDashboardSummary,
    useAdminDashboardChart,
    useAdminDashboardUsers,
} from '@/hooks/useDashboard';
import {
    ChartType, AggregationInterval, DateRangePreset,
} from '@/types/dashboard';
import { COLORS, CARD, FONTS, SECTION_HEADER } from '@/utils/theme';

// ── 스타일 상수 ──────────────────────────────────────────
const CARD_STYLE = {
    ...CARD,
    padding: '24px',
    backgroundColor: COLORS.cardBg,
} as const;

const STAT_VALUE_STYLE = {
    fontSize: '36px',
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
    reading: COLORS.sage,
    pdf: COLORS.rose,
    grid: 'rgba(0,0,0,0.05)',
} as const;

// ── 기간 프리셋 ──────────────────────────────────────────
const PRESETS: { value: DateRangePreset; label: string; days: number }[] = [
    { value: '7d', label: '7日', days: 7 },
    { value: '30d', label: '30日', days: 30 },
    { value: '90d', label: '90日', days: 90 },
    { value: '1y', label: '1年', days: 365 },
];

function getDateRange(preset: DateRangePreset): { start: string; end: string } {
    const now = new Date();
    const end = now.toISOString();
    const presetDays = PRESETS.find(p => p.value === preset)?.days || 30;
    const start = new Date(now.getTime() - presetDays * 86400000).toISOString();
    return { start, end };
}

// ── 요약 카드 ────────────────────────────────────────────

function AdminSummaryCards() {
    const { summary, loading, error } = useAdminDashboardSummary();

    if (loading) return <Center py="xl"><Loader color={COLORS.rose} /></Center>;
    if (error || !summary) return <Text c="dimmed" ta="center">{error || 'データがありません'}</Text>;

    const cards = [
        { icon: IconChartBar, label: '全体鑑定実行数', value: summary.total_readings, color: COLORS.sage },
        { icon: IconFileDownload, label: '全体PDFダウンロード数', value: summary.total_pdfs, color: COLORS.rose },
        { icon: IconUsers, label: 'アクティブユーザー数', value: summary.active_users, color: COLORS.accent },
    ];

    return (
        <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
            {cards.map((c) => (
                <Card key={c.label} style={CARD_STYLE}>
                    <Group gap="sm" mb="xs">
                        <c.icon size={20} style={{ color: c.color }} stroke={1.5} />
                        <Text style={STAT_LABEL_STYLE}>{c.label}</Text>
                    </Group>
                    <Text style={STAT_VALUE_STYLE}>{c.value.toLocaleString()}</Text>
                </Card>
            ))}
        </SimpleGrid>
    );
}

// ── 추이 그래프 ──────────────────────────────────────────

function TrendChart() {
    const [preset, setPreset] = useState<DateRangePreset>('30d');
    const [chartType, setChartType] = useState<ChartType>('line');
    const [interval, setInterval] = useState<AggregationInterval>('daily');

    const { start, end } = useMemo(() => getDateRange(preset), [preset]);
    const { chartData, loading, error } = useAdminDashboardChart(start, end, interval);

    // 두 데이터 세트를 날짜 기준으로 병합
    const mergedData = useMemo(() => {
        if (!chartData) return [];
        const map = new Map<string, { date: string; readings: number; pdfs: number }>();
        for (const p of chartData.readings) {
            map.set(p.date, { date: p.date, readings: p.count, pdfs: 0 });
        }
        for (const p of chartData.pdfs) {
            const existing = map.get(p.date);
            if (existing) {
                existing.pdfs = p.count;
            } else {
                map.set(p.date, { date: p.date, readings: 0, pdfs: p.count });
            }
        }
        return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date));
    }, [chartData]);

    const ChartComponent = chartType === 'line' ? LineChart : BarChart;

    return (
        <Stack gap="md">
            <Group justify="space-between" wrap="wrap" gap="sm">
                <SegmentedControl
                    value={preset}
                    onChange={(v) => setPreset(v as DateRangePreset)}
                    data={PRESETS.map(p => ({ value: p.value, label: p.label }))}
                    size="xs"
                    styles={{ root: { fontFamily: FONTS.caption } }}
                />
                <Group gap="xs">
                    <Select
                        value={interval}
                        onChange={(v) => setInterval((v as AggregationInterval) || 'daily')}
                        data={[
                            { value: 'daily', label: '日別' },
                            { value: 'weekly', label: '週別' },
                            { value: 'monthly', label: '月別' },
                        ]}
                        size="xs"
                        w={90}
                        styles={{ input: { fontFamily: FONTS.caption, fontSize: '12px' } }}
                    />
                    <SegmentedControl
                        value={chartType}
                        onChange={(v) => setChartType(v as ChartType)}
                        data={[
                            { value: 'line', label: 'ライン' },
                            { value: 'bar', label: 'バー' },
                        ]}
                        size="xs"
                        styles={{ root: { fontFamily: FONTS.caption } }}
                    />
                </Group>
            </Group>

            {loading ? (
                <Center py="xl"><Loader size="sm" color={COLORS.rose} /></Center>
            ) : error ? (
                <Text c="dimmed" size="sm" ta="center">{error}</Text>
            ) : mergedData.length === 0 ? (
                <Text c="dimmed" size="sm" ta="center" py="xl">指定期間にデータがありません</Text>
            ) : (
                <Box style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <ChartComponent data={mergedData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                            <XAxis
                                dataKey="date"
                                tick={{ fontSize: 10, fill: COLORS.textDimmed }}
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
                            />
                            <Legend
                                wrapperStyle={{ fontSize: '12px', fontFamily: FONTS.caption }}
                            />
                            {chartType === 'line' ? (
                                <>
                                    <Line type="monotone" dataKey="readings" name="鑑定数" stroke={CHART_COLORS.reading} strokeWidth={2} dot={{ r: 3 }} />
                                    <Line type="monotone" dataKey="pdfs" name="PDF数" stroke={CHART_COLORS.pdf} strokeWidth={2} dot={{ r: 3 }} />
                                </>
                            ) : (
                                <>
                                    <Bar dataKey="readings" name="鑑定数" fill={CHART_COLORS.reading} radius={[4, 4, 0, 0]} maxBarSize={30} />
                                    <Bar dataKey="pdfs" name="PDF数" fill={CHART_COLORS.pdf} radius={[4, 4, 0, 0]} maxBarSize={30} />
                                </>
                            )}
                        </ChartComponent>
                    </ResponsiveContainer>
                </Box>
            )}
        </Stack>
    );
}

// ── 사용자 테이블 ────────────────────────────────────────

function UsersTable() {
    const [page, setPage] = useState(1);
    const [sort, setSort] = useState('name');
    const [order, setOrder] = useState('asc');
    const [search, setSearch] = useState('');
    const perPage = 20;

    const { data, loading, error } = useAdminDashboardUsers(page, perPage, sort, order, search);

    const toggleSort = (field: string) => {
        if (sort === field) {
            setOrder(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSort(field);
            setOrder('asc');
        }
        setPage(1);
    };

    const SortIcon = order === 'asc' ? IconSortAscending : IconSortDescending;

    const sortableHeader = (field: string, label: string) => (
        <Table.Th
            style={{ cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }}
            onClick={() => toggleSort(field)}
            onKeyDown={(e: React.KeyboardEvent) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSort(field);
                }
            }}
            role="button"
            tabIndex={0}
        >
            <Group gap={4} wrap="nowrap">
                <Text size="xs" fw={600}>{label}</Text>
                {sort === field && <SortIcon size={14} style={{ color: COLORS.rose }} />}
            </Group>
        </Table.Th>
    );

    return (
        <Stack gap="md">
            <TextInput
                placeholder="ユーザー名またはメールで検索..."
                leftSection={<IconSearch size={16} />}
                value={search}
                onChange={(e) => { setSearch(e.currentTarget.value); setPage(1); }}
                size="sm"
                styles={{ input: { fontFamily: FONTS.body, fontSize: '13px' } }}
            />

            {loading ? (
                <Center py="lg"><Loader size="sm" color={COLORS.rose} /></Center>
            ) : error ? (
                <Text c="dimmed" size="sm" ta="center">{error}</Text>
            ) : !data || data.users.length === 0 ? (
                <Text c="dimmed" size="sm" ta="center" py="lg">該当するユーザーがいません</Text>
            ) : (
                <>
                    <Table.ScrollContainer minWidth={600}>
                        <Table striped highlightOnHover styles={{
                            th: { fontFamily: FONTS.caption, fontSize: '12px', letterSpacing: '0.03em' },
                            td: { fontFamily: FONTS.body, fontSize: '13px' },
                        }}>
                            <Table.Thead>
                                <Table.Tr>
                                    {sortableHeader('name', 'ユーザー名')}
                                    {sortableHeader('email', 'メール')}
                                    {sortableHeader('reading_count', '鑑定数')}
                                    {sortableHeader('pdf_count', 'PDF数')}
                                    {sortableHeader('last_reading_date', '最終鑑定日')}
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {data.users.map((user) => (
                                    <Table.Tr key={user.id}>
                                        <Table.Td>{user.name}</Table.Td>
                                        <Table.Td>{user.email}</Table.Td>
                                        <Table.Td ta="right">{user.reading_count}</Table.Td>
                                        <Table.Td ta="right">{user.pdf_count}</Table.Td>
                                        <Table.Td>
                                            {user.last_reading_date
                                                ? new Date(user.last_reading_date).toLocaleDateString('ja-JP')
                                                : '—'}
                                        </Table.Td>
                                    </Table.Tr>
                                ))}
                            </Table.Tbody>
                        </Table>
                    </Table.ScrollContainer>

                    {data.pagination.total_pages > 1 && (
                        <Center>
                            <Pagination
                                total={data.pagination.total_pages}
                                value={page}
                                onChange={setPage}
                                size="sm"
                                color={COLORS.rose}
                            />
                        </Center>
                    )}

                    <Text size="xs" c="dimmed" ta="right" style={{ fontFamily: FONTS.caption }}>
                        全{data.pagination.total}件中 {((page - 1) * perPage) + 1}〜{Math.min(page * perPage, data.pagination.total)}件表示
                    </Text>
                </>
            )}
        </Stack>
    );
}

// ── メインページ ─────────────────────────────────────────

export default function AdminDashboardPage() {
    const { isSuperuser } = useAuth();

    if (!isSuperuser) {
        return (
            <Container size="lg" py="xl">
                <Center py="xl">
                    <Text c="dimmed" size="lg">このページはスーパーユーザー専用です。</Text>
                </Center>
            </Container>
        );
    }

    return (
        <Container size="lg" py="xl">
            <Stack gap="xl">
                {/* ヘッダー */}
                <Box>
                    <Text style={SECTION_HEADER} mb={4}>ADMIN DASHBOARD</Text>
                    <Title
                        order={2}
                        style={{
                            fontFamily: FONTS.title,
                            color: COLORS.text,
                            fontWeight: 600,
                        }}
                    >
                        管理者ダッシュボード
                    </Title>
                    <Text size="sm" c="dimmed" mt={4}>
                        サービス全体の利用状況をリアルタイムで確認できます
                    </Text>
                </Box>

                {/* 要約カード */}
                <AdminSummaryCards />

                {/* 推移グラフ */}
                <Card style={CARD_STYLE}>
                    <Text style={SECTION_HEADER} mb="sm">TREND ANALYSIS</Text>
                    <Title order={4} mb="md" style={{ fontFamily: FONTS.title, color: COLORS.text }}>
                        利用推移グラフ
                    </Title>
                    <TrendChart />
                </Card>

                {/* ユーザー別集計 */}
                <Card style={CARD_STYLE}>
                    <Text style={SECTION_HEADER} mb="sm">USER ANALYTICS</Text>
                    <Title order={4} mb="md" style={{ fontFamily: FONTS.title, color: COLORS.text }}>
                        ユーザー別集計
                    </Title>
                    <UsersTable />
                </Card>
            </Stack>
        </Container>
    );
}
