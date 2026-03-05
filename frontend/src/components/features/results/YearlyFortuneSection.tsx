'use client';

import React from 'react';
import { Paper, Title, Box, Text, Card, Badge, Group, Stack } from '@mantine/core';
import { NumerologyStone } from '@/types/directionFortune';

interface YearlyFortuneSectionProps {
    yearlyStone: NumerologyStone;
    personalYearNumber?: number;
}

const accentColor = '#8b5cf6';

/**
 * Section B: 今年の運勢
 * ⑥½ 年運石 + Personal Year Number
 */
const YearlyFortuneSection: React.FC<YearlyFortuneSectionProps> = ({
    yearlyStone,
    personalYearNumber,
}) => {
    return (
        <Paper
            shadow="sm"
            p={0}
            radius="md"
            style={{
                background: 'linear-gradient(to bottom right, rgba(255,255,255,0.98), rgba(250,245,255,0.9))',
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
                ✨ 今年の運勢
            </Title>

            <Box p="md">
                <Card
                    shadow="xs"
                    p="md"
                    radius="md"
                    style={{
                        background: `linear-gradient(135deg, ${accentColor}08, ${accentColor}15)`,
                        border: `1px solid ${accentColor}25`,
                    }}
                >
                    <Group justify="space-between" align="flex-start">
                        <Stack gap={4} style={{ flex: 1 }}>
                            <Text fw={600} size="xs" c="dimmed">
                                ✦ 年運石
                            </Text>
                            <Text fw={700} size="sm" style={{ color: '#2d3748' }}>
                                {yearlyStone.stone_name}
                            </Text>
                            <Text size="xs" c="dimmed" mt={2}>
                                {yearlyStone.description}
                            </Text>
                            {yearlyStone.secondary && (
                                <Text size="xs" c="dimmed" mt={2} style={{ opacity: 0.8 }}>
                                    サブ: {yearlyStone.secondary.stone_name}
                                </Text>
                            )}
                        </Stack>

                        {personalYearNumber && (
                            <Badge
                                size="lg"
                                radius="xl"
                                variant="filled"
                                style={{
                                    fontSize: '1.2rem',
                                    padding: '0.2rem 0.5rem',
                                    fontWeight: 700,
                                    height: '40px',
                                    minWidth: '40px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: `linear-gradient(135deg, ${accentColor} 0%, #a855f7 100%)`,
                                    boxShadow: `0 3px 10px ${accentColor}40`,
                                    flexShrink: 0,
                                }}
                            >
                                {personalYearNumber}
                            </Badge>
                        )}
                    </Group>
                </Card>
            </Box>
        </Paper>
    );
};

export default YearlyFortuneSection;
