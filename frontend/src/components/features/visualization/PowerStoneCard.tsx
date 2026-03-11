'use client';

import React from 'react';
import { Card, Text, Group, Badge, SimpleGrid } from '@mantine/core';
import {
    PowerStones,
    SixLayerPowerStones,
    isSixLayer,
} from '@/types/directionFortune';
import { StoneItem3 } from './StoneItem3';
import { SixLayerStoneItem } from './SixLayerStoneItem';

/**
 * パワーストーンカード
 *
 * SRP: ストーンレイアウトの組み立てのみを担当
 *      個別ストーン表示は StoneItem3 / SixLayerStoneItem に委譲
 *      定数はすべて powerStoneConstants.ts で管理
 */

/** カード共通スタイル */
const CARD_STYLE = {
    background: 'rgba(255,255,255,0.85)',
    backdropFilter: 'blur(4px)',
} as const;

interface PowerStoneCardProps {
    powerStones: PowerStones | SixLayerPowerStones;
    targetYear?: number;
}

const PowerStoneCard: React.FC<PowerStoneCardProps> = ({ powerStones, targetYear }) => {
    // ── 6-Layer ──
    if (isSixLayer(powerStones)) {
        return (
            <Card shadow="xs" withBorder p="sm" radius="md" mt="sm" style={CARD_STYLE}>
                <Text fw={700} size="sm" mb={4} ta="center" c="violet.7">
                    ✨ あなたのパワーストーン
                </Text>

                {/* ライフパスメタ情報 */}
                <Group justify="center" gap={8} mb="xs">
                    <Badge
                        size="sm"
                        variant="gradient"
                        gradient={{ from: '#667eea', to: '#764ba2', deg: 135 }}
                    >
                        ライフパス {powerStones.life_path_number}
                    </Badge>
                    <Badge size="sm" variant="light" color="violet">
                        {powerStones.planet}
                    </Badge>
                </Group>

                {/* 数秘術 4-Layer (2×2) */}
                <Text size="xs" fw={600} c="dimmed" mb={4}>
                    🔮 数秘術ストーン（一生の守護石）
                </Text>
                <SimpleGrid cols={{ base: 2, sm: 2 }} spacing="xs" mb="sm">
                    <SixLayerStoneItem stone={powerStones.overall_stone} layerKey="overall" />
                    <SixLayerStoneItem stone={powerStones.health_stone} layerKey="health" />
                    <SixLayerStoneItem stone={powerStones.wealth_stone} layerKey="wealth" />
                    <SixLayerStoneItem stone={powerStones.love_stone} layerKey="love" />
                </SimpleGrid>

                {/* 年運石 (Personal Year Number) */}
                {powerStones.yearly_stone && (
                    <>
                        <Text component="div" size="xs" fw={600} c="dimmed" mb={4}>
                            🌟 {targetYear || new Date().getFullYear()}年のストーン
                            {powerStones.personal_year_number && (
                                <Badge size="xs" variant="light" color="orange" ml={6}>
                                    パーソナルイヤー {powerStones.personal_year_number}
                                </Badge>
                            )}
                        </Text>
                        <SimpleGrid cols={{ base: 1, sm: 1 }} spacing="xs" mb="sm">
                            <SixLayerStoneItem stone={powerStones.yearly_stone} layerKey="yearly" />
                        </SimpleGrid>
                    </>
                )}

                {/* 九星気学 2-Layer */}
                {(powerStones.monthly_stone || powerStones.protection_stone) && (
                    <>
                        <Text size="xs" fw={600} c="dimmed" mb={4}>
                            📅 今月のストーン（方位エネルギー）
                        </Text>
                        <SimpleGrid cols={{ base: 2, sm: 2 }} spacing="xs">
                            {powerStones.monthly_stone && (
                                <SixLayerStoneItem stone={powerStones.monthly_stone} layerKey="monthly" />
                            )}
                            {powerStones.protection_stone && (
                                <SixLayerStoneItem stone={powerStones.protection_stone} layerKey="protection" />
                            )}
                        </SimpleGrid>
                    </>
                )}
            </Card>
        );
    }

    // ── 3-Layer（既存互換）──
    return (
        <Card shadow="xs" withBorder p="sm" radius="md" mt="sm" style={CARD_STYLE}>
            <Text fw={700} size="sm" mb="xs" ta="center" c="violet.7">
                ✨ 今月のパワーストーン
            </Text>

            <Group gap="xs" grow align="stretch" wrap="nowrap">
                <StoneItem3 stone={powerStones.base_stone} />
                {powerStones.monthly_stone && (
                    <StoneItem3 stone={powerStones.monthly_stone} />
                )}
                {powerStones.protection_stone && (
                    <StoneItem3 stone={powerStones.protection_stone} />
                )}
            </Group>
        </Card>
    );
};

export default PowerStoneCard;
