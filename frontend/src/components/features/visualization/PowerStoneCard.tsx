'use client';

import React from 'react';
import { Card, Text, Box, Group, Badge, Divider, SimpleGrid } from '@mantine/core';
import {
    GogyoStone,
    PowerStones,
    SixLayerPowerStones,
    StoneRecommendation,
    isSixLayer,
    isGogyoStone,
} from '@/types/directionFortune';

// ── 오행(五行) 색상 맵 ──────────────────────────────────
const GOGYO_THEME: Record<string, { bg: string; border: string; badge: string; label: string }> = {
    '水': { bg: 'linear-gradient(135deg, rgba(30,136,229,0.10) 0%, rgba(30,136,229,0.04) 100%)', border: 'rgba(30,136,229,0.35)', badge: 'blue', label: '水 (Water)' },
    '木': { bg: 'linear-gradient(135deg, rgba(67,160,71,0.10)  0%, rgba(67,160,71,0.04)  100%)', border: 'rgba(67,160,71,0.35)', badge: 'green', label: '木 (Wood)' },
    '火': { bg: 'linear-gradient(135deg, rgba(229,57,53,0.10)  0%, rgba(229,57,53,0.04)  100%)', border: 'rgba(229,57,53,0.35)', badge: 'red', label: '火 (Fire)' },
    '土': { bg: 'linear-gradient(135deg, rgba(249,168,37,0.10) 0%, rgba(249,168,37,0.04) 100%)', border: 'rgba(249,168,37,0.35)', badge: 'gray', label: '土 (Earth)' },
    '金': { bg: 'linear-gradient(135deg, rgba(120,144,156,0.10) 0%, rgba(120,144,156,0.04) 100%)', border: 'rgba(120,144,156,0.35)', badge: 'yellow', label: '金 (Metal)' },
};

// ── 3-Layer 메타 ─────────────────────────────────────────
const LAYER_META_3: Record<string, { icon: string; label: string; sublabel: string }> = {
    base: { icon: '💎', label: '基本石', sublabel: '本命石 — 一生の守護石' },
    monthly: { icon: '🌙', label: '月運石', sublabel: '今月の吉方位エネルギー' },
    protection: { icon: '🛡️', label: '護身石', sublabel: '今月の凶方位を抑制' },
};

// ── 7-Layer 메타 ─────────────────────────────────────────
const LAYER_META_7: Record<string, { icon: string; label: string; sublabel: string; color: string }> = {
    overall: { icon: '💎', label: '全体運', sublabel: '人生の総合的な守護石', color: '#7c3aed' },
    health: { icon: '❤️', label: '健康運', sublabel: '心身の健康をサポート', color: '#dc2626' },
    wealth: { icon: '💰', label: '財運', sublabel: '豊かさと繁栄を引き寄せる', color: '#d97706' },
    love: { icon: '💕', label: '恋愛運', sublabel: '愛と人間関係の調和', color: '#ec4899' },
    yearly: { icon: '✨', label: '年運石', sublabel: '今年のエネルギー補充石', color: '#f59e0b' },
    monthly: { icon: '🌙', label: '月運石', sublabel: '今月の吉方位エネルギー', color: '#0891b2' },
    protection: { icon: '🛡️', label: '護身石', sublabel: '今月の凶方位を抑制', color: '#4b5563' },
};

const DEFAULT_THEME = { bg: 'rgba(240,240,240,0.3)', border: 'rgba(200,200,200,0.4)', badge: 'gray', label: '?' };

// ── ローカライズ正規化 ──────────────────────────────────
const LAYER_LABEL_TO_KEY: Record<string, string> = {
    '基本石': 'base', '기본석': 'base', 'Base Stone': 'base', 'base': 'base',
    '月運石': 'monthly', '월운석': 'monthly', 'Monthly Stone': 'monthly', 'monthly': 'monthly',
    '護身石': 'protection', '호신석': 'protection', 'Protection Stone': 'protection', 'protection': 'protection',
};

const GOGYO_NORMALIZE: Record<string, string> = {
    '水': '水', 'Water': '水', '수': '水',
    '木': '木', 'Wood': '木', '목': '木',
    '火': '火', 'Fire': '火', '화': '火',
    '土': '土', 'Earth': '土', '토': '土',
    '金': '金', 'Metal': '金', '금': '金',
};

// ══════════════════════════════════════════════════════════
// 3-Layer 個別ストーンアイテム（既存互換）
// ══════════════════════════════════════════════════════════
const StoneItem3: React.FC<{ stone: GogyoStone }> = ({ stone }) => {
    const gogyoKey = GOGYO_NORMALIZE[stone.gogyo] || stone.gogyo;
    const theme = GOGYO_THEME[gogyoKey] || DEFAULT_THEME;
    const layerKey = LAYER_LABEL_TO_KEY[stone.layer] || stone.layer;
    const meta = LAYER_META_3[layerKey] || { icon: '✦', label: stone.layer, sublabel: '' };

    return (
        <Box style={{
            flex: '1 1 0',
            minWidth: 0,
            background: theme.bg,
            border: `1px solid ${theme.border}`,
            borderRadius: '12px',
            padding: '12px 10px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
        }}>
            <Group gap={6} wrap="nowrap">
                <Text size="lg" style={{ lineHeight: 1 }}>{meta.icon}</Text>
                <Box>
                    <Text fw={700} size="xs" style={{ lineHeight: 1.2 }}>{meta.label}</Text>
                    <Text size="10px" c="dimmed" style={{ lineHeight: 1.2 }}>{meta.sublabel}</Text>
                </Box>
            </Group>

            <Divider size="xs" style={{ opacity: 0.4 }} />

            <Group gap={6} wrap="nowrap" align="center">
                <Text fw={600} size="sm" style={{ flex: 1, lineHeight: 1.3 }} lineClamp={1}>
                    {stone.stone_name}
                </Text>
                <Badge size="xs" variant="light" color={theme.badge} style={{ flexShrink: 0 }}>
                    {stone.gogyo}
                </Badge>
            </Group>

            <Text size="xs" c="dimmed" style={{ lineHeight: 1.4 }} lineClamp={3}>
                {stone.reason}
            </Text>
        </Box>
    );
};

// ══════════════════════════════════════════════════════════
// 6-Layer ストーンカード（수비술・구성기학 共用）
// ══════════════════════════════════════════════════════════
const SixLayerStoneItem: React.FC<{
    stone: StoneRecommendation;
    layerKey: string;
}> = ({ stone, layerKey }) => {
    const meta = LAYER_META_7[layerKey] || { icon: '✦', label: stone.layer, sublabel: '', color: '#6b7280' };
    const gogyo = isGogyoStone(stone);

    return (
        <Box style={{
            background: `linear-gradient(135deg, ${meta.color}08 0%, ${meta.color}03 100%)`,
            border: `1px solid ${meta.color}30`,
            borderRadius: '12px',
            padding: '12px 10px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            height: '100%',
        }}>
            {/* レイヤーラベル */}
            <Group gap={6} wrap="nowrap">
                <Text size="lg" style={{ lineHeight: 1 }}>{meta.icon}</Text>
                <Box>
                    <Text fw={700} size="xs" style={{ lineHeight: 1.2, color: meta.color }}>
                        {meta.label}
                    </Text>
                    <Text size="10px" c="dimmed" style={{ lineHeight: 1.2 }}>{meta.sublabel}</Text>
                </Box>
            </Group>

            <Divider size="xs" style={{ opacity: 0.3 }} />

            {/* メインストーン */}
            <Text fw={600} size="sm" style={{ lineHeight: 1.3 }} lineClamp={1}>
                {stone.stone_name}
            </Text>

            {/* description (수비술) or reason (구성기학) */}
            <Text size="xs" c="dimmed" style={{ lineHeight: 1.4 }} lineClamp={2}>
                {gogyo ? stone.reason : stone.description}
            </Text>

            {/* 五行バッジ（구성기학 stones） */}
            {gogyo && (
                <Badge size="xs" variant="light" color={GOGYO_THEME[GOGYO_NORMALIZE[stone.gogyo] || '']?.badge || 'gray'} style={{ alignSelf: 'flex-start' }}>
                    {stone.gogyo}
                </Badge>
            )}

            {/* サブストーン（수비술 stones） */}
            {!gogyo && stone.secondary && (
                <Box style={{
                    marginTop: 'auto',
                    padding: '6px 8px',
                    borderRadius: '8px',
                    background: `${meta.color}06`,
                    border: `1px dashed ${meta.color}20`,
                }}>
                    <Text size="10px" c="dimmed" fw={600} style={{ lineHeight: 1.2 }}>
                        サブストーン
                    </Text>
                    <Text size="xs" fw={500} style={{ lineHeight: 1.3 }}>
                        {stone.secondary.stone_name}
                    </Text>
                </Box>
            )}
        </Box>
    );
};

// ══════════════════════════════════════════════════════════
// メインコンポーネント
// ══════════════════════════════════════════════════════════
interface PowerStoneCardProps {
    powerStones: PowerStones | SixLayerPowerStones;
    targetYear?: number;
}

const PowerStoneCard: React.FC<PowerStoneCardProps> = ({ powerStones, targetYear }) => {
    // ── 6-Layer ──
    if (isSixLayer(powerStones)) {
        return (
            <Card shadow="xs" withBorder p="sm" radius="md" mt="sm" style={{
                background: 'rgba(255,255,255,0.85)',
                backdropFilter: 'blur(4px)',
            }}>
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

                {/* 수비술 4-Layer (2×2) */}
                <Text size="xs" fw={600} c="dimmed" mb={4}>
                    🔮 数秘術ストーン（一生の守護石）
                </Text>
                <SimpleGrid cols={{ base: 2, sm: 2 }} spacing="xs" mb="sm">
                    <SixLayerStoneItem stone={powerStones.overall_stone} layerKey="overall" />
                    <SixLayerStoneItem stone={powerStones.health_stone} layerKey="health" />
                    <SixLayerStoneItem stone={powerStones.wealth_stone} layerKey="wealth" />
                    <SixLayerStoneItem stone={powerStones.love_stone} layerKey="love" />
                </SimpleGrid>

                {/* 연운석 (Personal Year Number) */}
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

                {/* 구성기학 2-Layer */}
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
        <Card shadow="xs" withBorder p="sm" radius="md" mt="sm" style={{
            background: 'rgba(255,255,255,0.85)',
            backdropFilter: 'blur(4px)',
        }}>
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
