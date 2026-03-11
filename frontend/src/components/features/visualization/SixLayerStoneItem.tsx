'use client';

import React from 'react';
import Image from 'next/image';
import { Box, Text, Group, Badge, Divider } from '@mantine/core';
import { getStoneImagePath } from '@/utils/stoneImageMap';
import { StoneRecommendation, isGogyoStone } from '@/types/directionFortune';
import { LAYER_META_7, GOGYO_THEME, GOGYO_NORMALIZE } from './powerStoneConstants';

/**
 * 7-Layer ストーンカード（数秘術・九星気学共用）
 *
 * SRP: 7-Layer用の単一ストーン表示のみを担当
 */
export const SixLayerStoneItem: React.FC<{
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
            <Group gap={8} wrap="nowrap">
                <Box style={{
                    width: '36px', height: '36px', borderRadius: '50%',
                    overflow: 'hidden', flexShrink: 0,
                    border: `1px solid ${meta.color}30`,
                    backgroundColor: '#f9f7f2',
                }}>
                    <Image
                        src={getStoneImagePath(stone.stone_id)}
                        alt={stone.stone_name}
                        width={36} height={36}
                        style={{ objectFit: 'cover', borderRadius: '50%' }}
                    />
                </Box>
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

            {/* description (数秘術) or reason (九星気学) */}
            <Text size="xs" c="dimmed" style={{ lineHeight: 1.4 }} lineClamp={2}>
                {gogyo ? stone.reason : stone.description}
            </Text>

            {/* 五行バッジ（九星気学 stones） */}
            {gogyo && (
                <Badge size="xs" variant="light" color={GOGYO_THEME[GOGYO_NORMALIZE[stone.gogyo] || '']?.badge || 'gray'} style={{ alignSelf: 'flex-start' }}>
                    {stone.gogyo}
                </Badge>
            )}

            {/* サブストーン（数秘術 stones） */}
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
