'use client';

import React from 'react';
import { Paper, Title, Box, Text, Card, Group, Badge, Stack, SimpleGrid } from '@mantine/core';
import { NumerologyStone, SixLayerPowerStones } from '@/types/directionFortune';

interface NumerologyProfileSectionProps {
    stoneData: SixLayerPowerStones;
}

/** 小さなパワーストーンカード */
const StoneCard: React.FC<{ label: string; stone: NumerologyStone; accentColor: string }> = ({
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
            {stone.description}
        </Text>
        {stone.secondary && (
            <Text size="xs" c="dimmed" mt={4} style={{ opacity: 0.8 }}>
                サブ: {stone.secondary.stone_name}
            </Text>
        )}
    </Card>
);

const primaryColor = '#667eea';
const secondaryColor = '#764ba2';

/**
 * Section A: 数秘術プロフィール
 * ① 数秘の数字 + ② 特性 + ③~⑥ 4つの運石
 */
const NumerologyProfileSection: React.FC<NumerologyProfileSectionProps> = ({ stoneData }) => {
    return (
        <Paper
            shadow="sm"
            p={0}
            radius="md"
            style={{
                background: 'linear-gradient(to bottom right, rgba(255,255,255,0.98), rgba(245,247,250,0.9))',
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
                🔮 あなたの数秘
            </Title>

            {/* ─── ① 数秘の数字 ─── */}
            <Box
                p="md"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor}12, ${secondaryColor}08)`,
                    borderBottom: `1px solid ${primaryColor}15`,
                }}
            >
                <Stack align="center" gap="xs">
                    <Group justify="center" align="center" gap="md">
                        <Badge
                            size="xl"
                            radius="xl"
                            variant="filled"
                            style={{
                                fontSize: '2rem',
                                padding: '0.3rem 0.8rem',
                                fontWeight: 800,
                                height: '64px',
                                minWidth: '64px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`,
                                boxShadow: `0 4px 14px ${primaryColor}40`,
                            }}
                        >
                            {stoneData.life_path_number}
                        </Badge>

                        {stoneData.title && (
                            <Badge
                                size="lg"
                                radius="md"
                                variant="light"
                                style={{
                                    padding: '0.3rem 1rem',
                                    fontSize: '1rem',
                                    fontWeight: 600,
                                    background: `${primaryColor}12`,
                                    color: '#2d3748',
                                    border: `1.5px solid ${primaryColor}30`,
                                }}
                            >
                                {stoneData.title}
                            </Badge>
                        )}
                    </Group>
                </Stack>
            </Box>

            {/* ─── ② 特性テキスト ─── */}
            {stoneData.traits && (
                <Box
                    p="md"
                    style={{
                        borderBottom: `1px solid ${primaryColor}12`,
                    }}
                >
                    <Text
                        size="sm"
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.75',
                            color: '#374151',
                            fontSize: 'clamp(0.85rem, 1.6vw, 0.95rem)',
                        }}
                    >
                        {stoneData.traits}
                    </Text>
                </Box>
            )}

            {/* ─── ③~⑥ 4つの運石 ─── */}
            <Box p="md">
                <SimpleGrid cols={{ base: 2, sm: 2 }} spacing="sm">
                    <StoneCard label="✦ 全体運" stone={stoneData.overall_stone} accentColor="#6366f1" />
                    <StoneCard label="✦ 健康運" stone={stoneData.health_stone} accentColor="#10b981" />
                    <StoneCard label="✦ 金運" stone={stoneData.wealth_stone} accentColor="#f59e0b" />
                    <StoneCard label="✦ 恋愛運" stone={stoneData.love_stone} accentColor="#ec4899" />
                </SimpleGrid>
            </Box>
        </Paper>
    );
};

export default NumerologyProfileSection;
