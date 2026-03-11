'use client';

import React from 'react';
import Image from 'next/image';
import { Box, Text, Group, Badge, Divider } from '@mantine/core';
import { getStoneImagePath } from '@/utils/stoneImageMap';
import { GogyoStone } from '@/types/directionFortune';
import { GOGYO_THEME, GOGYO_NORMALIZE, LAYER_META_3, LAYER_LABEL_TO_KEY, DEFAULT_THEME } from './powerStoneConstants';

/**
 * 3-Layer 個別ストーンアイテム（既存互換）
 *
 * SRP: 3-Layer用の単一ストーン表示のみを担当
 */
export const StoneItem3: React.FC<{ stone: GogyoStone }> = ({ stone }) => {
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
            <Group gap={8} wrap="nowrap">
                <Box style={{
                    width: '36px', height: '36px', borderRadius: '50%',
                    overflow: 'hidden', flexShrink: 0,
                    border: '1px solid rgba(212, 175, 55, 0.2)',
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
