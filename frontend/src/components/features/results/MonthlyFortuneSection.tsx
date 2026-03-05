'use client';

import React from 'react';
import { Paper, Title, Box, Text, Badge, Group, Stack, Card, SimpleGrid } from '@mantine/core';
import { GogyoStone, PeriodFortuneData, MonthDirectionInfo } from '@/types/directionFortune';

interface MonthlyFortuneSectionProps {
    mainStar: { star_number: number; name_jp: string };
    monthStar: { star_number: number; name_jp: string };
    currentMonthData: PeriodFortuneData | null;
    monthlyStone: GogyoStone | null;
    protectionStone: GogyoStone | null;
}

/** 九星の星番号に基づく色 */
const getStarColor = (starNumber: number): string => {
    const colors = [
        '#3490dc', '#2d3748', '#38a169', '#319795', '#ecc94b',
        '#a0aec0', '#e53e3e', '#805ad5', '#ed64a6',
    ];
    return colors[starNumber - 1] || '#3490dc';
};

/** 方位の日本語表記 */
const DIRECTION_LABELS: Record<string, string> = {
    north: '北', northeast: '北東', east: '東', southeast: '南東',
    south: '南', southwest: '南西', west: '西', northwest: '北西',
};

/** 吉方位バッジ */
const DirectionBadge: React.FC<{ direction: string; info: MonthDirectionInfo }> = ({
    direction,
    info,
}) => {
    const isAuspicious = info.is_auspicious;
    const bgColor = isAuspicious ? '#ecfdf5' : '#fef2f2';
    const borderColor = isAuspicious ? '#a7f3d0' : '#fecaca';
    const textColor = isAuspicious ? '#065f46' : '#991b1b';
    const icon = isAuspicious ? '◎' : '△';

    return (
        <Card
            p="xs"
            radius="sm"
            style={{
                background: bgColor,
                border: `1px solid ${borderColor}`,
            }}
        >
            <Group gap={6} wrap="nowrap">
                <Text size="sm" fw={700} style={{ color: textColor, minWidth: '20px' }}>
                    {icon}
                </Text>
                <Stack gap={0} style={{ flex: 1 }}>
                    <Text size="sm" fw={600} style={{ color: textColor }}>
                        {DIRECTION_LABELS[direction] || direction}
                    </Text>
                    {info.reason && (
                        <Text size="xs" c="dimmed" lineClamp={1}>
                            {info.reason}
                        </Text>
                    )}
                </Stack>
                {info.marks?.length > 0 && (
                    <Group gap={2}>
                        {info.marks.map((m, i) => (
                            <Text key={i} size="xs" style={{ opacity: 0.7 }}>
                                {m}
                            </Text>
                        ))}
                    </Group>
                )}
            </Group>
        </Card>
    );
};

/** 小さな構成気学ストーンカード */
const GogyoStoneCard: React.FC<{ label: string; stone: GogyoStone; accentColor: string }> = ({
    label,
    stone,
    accentColor,
}) => (
    <Card
        shadow="xs"
        p="sm"
        radius="md"
        style={{
            background: `linear-gradient(135deg, ${accentColor}08, ${accentColor}15)`,
            border: `1px solid ${accentColor}25`,
        }}
    >
        <Text fw={600} size="xs" c="dimmed" mb={4}>
            {label}
        </Text>
        <Text fw={700} size="sm" style={{ color: '#2d3748' }}>
            {stone.stone_name}
        </Text>
        <Text size="xs" c="dimmed" mt={2}>
            {stone.reason}
        </Text>
    </Card>
);

const accentColor = '#0ea5e9';

/**
 * Section C: 今月の運勢 (九星気学)
 * ⑦ 本命星 + 月命星 + ⑧ 吉方位テキストリスト + 月運石/護身石
 */
const MonthlyFortuneSection: React.FC<MonthlyFortuneSectionProps> = ({
    mainStar,
    monthStar,
    currentMonthData,
    monthlyStone,
    protectionStone,
}) => {
    // 方位データの分類
    const auspicious: [string, MonthDirectionInfo][] = [];
    const inauspicious: [string, MonthDirectionInfo][] = [];

    if (currentMonthData?.directions) {
        Object.entries(currentMonthData.directions).forEach(([dir, info]) => {
            if (info.is_auspicious) {
                auspicious.push([dir, info]);
            } else {
                inauspicious.push([dir, info]);
            }
        });
    }

    const mainColor = getStarColor(mainStar.star_number);
    const monthColor = getStarColor(monthStar.star_number);

    return (
        <Paper
            shadow="sm"
            p={0}
            radius="md"
            style={{
                background: 'linear-gradient(to bottom right, rgba(255,255,255,0.98), rgba(240,249,255,0.9))',
                border: '1px solid rgba(209, 213, 219, 0.5)',
                overflow: 'hidden',
            }}
        >
            {/* ─── ヘッダー ─── */}
            <Title
                order={3}
                ta="center"
                style={{
                    color: '#2d3748',
                    fontSize: 'clamp(0.9rem, 2.5vw, 1.2rem)',
                    fontWeight: 700,
                    padding: '14px 16px',
                    borderBottom: '1px solid rgba(209, 213, 219, 0.6)',
                    letterSpacing: '0.03em',
                }}
            >
                🌟 今月の運勢
                {currentMonthData?.display_month && (
                    <Text component="span" size="sm" fw={400} c="dimmed" ml="xs">
                        ({currentMonthData.display_month})
                    </Text>
                )}
            </Title>

            {/* ─── ⑦ 九星気学の星 ─── */}
            <Box p="md" style={{ borderBottom: `1px solid ${accentColor}12` }}>
                <SimpleGrid cols={2} spacing="sm">
                    <Card
                        p="sm"
                        radius="md"
                        style={{
                            background: `${mainColor}10`,
                            border: `2px solid ${mainColor}50`,
                            textAlign: 'center',
                        }}
                    >
                        <Text size="xs" fw={600} c="dimmed" mb={4}>本命星</Text>
                        <Text size="xl" fw={800} style={{ color: mainColor, lineHeight: 1 }}>
                            {mainStar.star_number}
                        </Text>
                        <Badge
                            size="sm"
                            mt={4}
                            style={{
                                background: mainColor,
                                color: 'white',
                                fontSize: '0.65rem',
                            }}
                        >
                            {mainStar.name_jp}
                        </Badge>
                    </Card>

                    <Card
                        p="sm"
                        radius="md"
                        style={{
                            background: `${monthColor}10`,
                            border: `2px solid ${monthColor}50`,
                            textAlign: 'center',
                        }}
                    >
                        <Text size="xs" fw={600} c="dimmed" mb={4}>月命星</Text>
                        <Text size="xl" fw={800} style={{ color: monthColor, lineHeight: 1 }}>
                            {monthStar.star_number}
                        </Text>
                        <Badge
                            size="sm"
                            mt={4}
                            style={{
                                background: monthColor,
                                color: 'white',
                                fontSize: '0.65rem',
                            }}
                        >
                            {monthStar.name_jp}
                        </Badge>
                    </Card>
                </SimpleGrid>
            </Box>

            {/* ─── ⑧ 吉方位テキストリスト ─── */}
            {currentMonthData?.directions && (
                <Box p="md" style={{ borderBottom: `1px solid ${accentColor}12` }}>
                    <Text fw={600} size="sm" mb="sm" style={{ color: '#374151' }}>
                        📍 今月の方位
                    </Text>

                    {auspicious.length > 0 && (
                        <Box mb="sm">
                            <Text size="xs" fw={600} c="teal" mb={4}>吉方位</Text>
                            <Stack gap={4}>
                                {auspicious.map(([dir, info]) => (
                                    <DirectionBadge key={dir} direction={dir} info={info} />
                                ))}
                            </Stack>
                        </Box>
                    )}

                    {inauspicious.length > 0 && (
                        <Box>
                            <Text size="xs" fw={600} c="red" mb={4}>注意方位</Text>
                            <Stack gap={4}>
                                {inauspicious.map(([dir, info]) => (
                                    <DirectionBadge key={dir} direction={dir} info={info} />
                                ))}
                            </Stack>
                        </Box>
                    )}
                </Box>
            )}

            {/* ─── 月運石 / 護身石 ─── */}
            {(monthlyStone || protectionStone) && (
                <Box p="md">
                    <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="sm">
                        {monthlyStone && (
                            <GogyoStoneCard label="✦ 月運石" stone={monthlyStone} accentColor="#0ea5e9" />
                        )}
                        {protectionStone && (
                            <GogyoStoneCard label="✦ 護身石" stone={protectionStone} accentColor="#6366f1" />
                        )}
                    </SimpleGrid>
                </Box>
            )}
        </Paper>
    );
};

export default MonthlyFortuneSection;
