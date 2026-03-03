'use client';

import React from 'react';
import { Card, Text, Box, Group, Badge, Divider } from '@mantine/core';
import { PowerStones, StoneRecommendation } from '@/types/directionFortune';

// ── 오행(五行) 색상 맵 ──────────────────────────────────
const GOGYO_THEME: Record<string, { bg: string; border: string; badge: string; label: string }> = {
    '水': { bg: 'linear-gradient(135deg, rgba(30,136,229,0.10) 0%, rgba(30,136,229,0.04) 100%)', border: 'rgba(30,136,229,0.35)', badge: 'blue', label: '水 (Water)' },
    '木': { bg: 'linear-gradient(135deg, rgba(67,160,71,0.10)  0%, rgba(67,160,71,0.04)  100%)', border: 'rgba(67,160,71,0.35)', badge: 'green', label: '木 (Wood)' },
    '火': { bg: 'linear-gradient(135deg, rgba(229,57,53,0.10)  0%, rgba(229,57,53,0.04)  100%)', border: 'rgba(229,57,53,0.35)', badge: 'red', label: '火 (Fire)' },
    '土': { bg: 'linear-gradient(135deg, rgba(249,168,37,0.10) 0%, rgba(249,168,37,0.04) 100%)', border: 'rgba(249,168,37,0.35)', badge: 'gray', label: '土 (Earth)' },
    '金': { bg: 'linear-gradient(135deg, rgba(120,144,156,0.10) 0%, rgba(120,144,156,0.04) 100%)', border: 'rgba(120,144,156,0.35)', badge: 'yellow', label: '金 (Metal)' },
};

const LAYER_META: Record<string, { icon: string; label: string; sublabel: string }> = {
    base: { icon: '💎', label: '基本石', sublabel: '本命石 — 一生の守護石' },
    monthly: { icon: '🌙', label: '月運石', sublabel: '今月の吉方位エネルギー' },
    protection: { icon: '🛡️', label: '護身石', sublabel: '今月の凶方位を抑制' },
};

const DEFAULT_THEME = { bg: 'rgba(240,240,240,0.3)', border: 'rgba(200,200,200,0.4)', badge: 'gray', label: '?' };

// ── ローカライズされた layer → 内部コード ──────────────────
const LAYER_LABEL_TO_KEY: Record<string, string> = {
    '基本石': 'base', '기본석': 'base', 'Base Stone': 'base', 'base': 'base',
    '月運石': 'monthly', '월운석': 'monthly', 'Monthly Stone': 'monthly', 'monthly': 'monthly',
    '護身石': 'protection', '호신석': 'protection', 'Protection Stone': 'protection', 'protection': 'protection',
};

// ── ローカライズされた gogyo → 正規コード ─────────────────
const GOGYO_NORMALIZE: Record<string, string> = {
    '水': '水', 'Water': '水', '수': '水',
    '木': '木', 'Wood': '木', '목': '木',
    '火': '火', 'Fire': '火', '화': '火',
    '土': '土', 'Earth': '土', '토': '土',
    '金': '金', 'Metal': '金', '금': '金',
};

// ── 個別ストーンアイテム ─────────────────────────────────
const StoneItem: React.FC<{ stone: StoneRecommendation }> = ({ stone }) => {
    const gogyoKey = GOGYO_NORMALIZE[stone.gogyo] || stone.gogyo;
    const theme = GOGYO_THEME[gogyoKey] || DEFAULT_THEME;
    const layerKey = LAYER_LABEL_TO_KEY[stone.layer] || stone.layer;
    const meta = LAYER_META[layerKey] || { icon: '✦', label: stone.layer, sublabel: '' };

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
            {/* レイヤーラベル */}
            <Group gap={6} wrap="nowrap">
                <Text size="lg" style={{ lineHeight: 1 }}>{meta.icon}</Text>
                <Box>
                    <Text fw={700} size="xs" style={{ lineHeight: 1.2 }}>{meta.label}</Text>
                    <Text size="10px" c="dimmed" style={{ lineHeight: 1.2 }}>{meta.sublabel}</Text>
                </Box>
            </Group>

            <Divider size="xs" style={{ opacity: 0.4 }} />

            {/* ストーン名 + 五行バッジ */}
            <Group gap={6} wrap="nowrap" align="center">
                <Text fw={600} size="sm" style={{ flex: 1, lineHeight: 1.3 }} lineClamp={1}>
                    {stone.stone_name}
                </Text>
                <Badge size="xs" variant="light" color={theme.badge} style={{ flexShrink: 0 }}>
                    {stone.gogyo}
                </Badge>
            </Group>

            {/* 推薦理由 */}
            <Text size="xs" c="dimmed" style={{ lineHeight: 1.4 }} lineClamp={3}>
                {stone.reason}
            </Text>
        </Box>
    );
};

// ── メインコンポーネント ─────────────────────────────────
interface PowerStoneCardProps {
    powerStones: PowerStones;
}

const PowerStoneCard: React.FC<PowerStoneCardProps> = ({ powerStones }) => {
    return (
        <Card shadow="xs" withBorder p="sm" radius="md" mt="sm" style={{
            background: 'rgba(255,255,255,0.85)',
            backdropFilter: 'blur(4px)',
        }}>
            <Text fw={700} size="sm" mb="xs" ta="center" c="violet.7">
                ✨ 今月のパワーストーン
            </Text>

            <Group gap="xs" grow align="stretch" wrap="nowrap">
                <StoneItem stone={powerStones.base_stone} />
                <StoneItem stone={powerStones.monthly_stone} />
                <StoneItem stone={powerStones.protection_stone} />
            </Group>
        </Card>
    );
};

export default PowerStoneCard;
