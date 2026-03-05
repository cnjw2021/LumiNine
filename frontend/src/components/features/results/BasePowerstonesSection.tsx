'use client';

import React from 'react';
import { Title, Text, Box, Stack, Group } from '@mantine/core';
import { NumerologyStone, SixLayerPowerStones } from '@/types/directionFortune';

interface BasePowerstonesSectionProps {
    stoneData: SixLayerPowerStones;
}

const STONE_CONFIGS = [
    { labelEn: 'OVERALL', labelJp: '全体運', key: 'overall_stone' as const, icon: 'diamond' },
    { labelEn: 'HEALTH', labelJp: '健康運', key: 'health_stone' as const, icon: 'spa' },
    { labelEn: 'WEALTH', labelJp: '金運', key: 'wealth_stone' as const, icon: 'currency_yen' },
    { labelEn: 'LOVE', labelJp: '恋愛運', key: 'love_stone' as const, icon: 'favorite' },
];

const PowerstoneCard: React.FC<{
    labelEn: string;
    labelJp: string;
    stone: NumerologyStone;
    icon: string;
}> = ({ labelEn, labelJp, stone, icon }) => (
    <Box
        style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.6)',
            padding: '20px',
            borderRadius: '16px',
            border: '1px solid #ffffff',
            boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
            transition: 'all 0.3s ease',
            cursor: 'default',
        }}
    >
        {/* Icon Box (w-16 h-16 rounded-xl bg-greige) */}
        <Box
            style={{
                width: '64px',
                height: '64px',
                backgroundColor: '#f0ede9',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '24px',
                flexShrink: 0,
            }}
        >
            <span
                className="material-symbols-outlined"
                style={{ fontSize: '28px', color: '#d8a7a7' }}
            >
                {icon}
            </span>
        </Box>

        {/* Text Content */}
        <Box style={{ flex: 1 }}>
            <Box style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '4px' }}>
                <Text style={{
                    fontSize: '10px',
                    color: '#d4af37',
                    fontWeight: 700,
                    letterSpacing: '0.1em',
                    fontFamily: '"Montserrat", sans-serif',
                }}>
                    {labelEn}
                </Text>
                <Text style={{
                    fontSize: '12px',
                    fontFamily: '"Noto Serif JP", serif',
                    color: 'rgba(74, 74, 74, 0.4)',
                }}>
                    {labelJp}
                </Text>
            </Box>
            <Title order={4} style={{
                fontFamily: '"Noto Serif JP", serif',
                color: '#4a4a4a',
                fontSize: '16px',
                fontWeight: 700,
            }}>
                {stone.stone_name}
            </Title>
        </Box>
    </Box>
);

const BasePowerstonesSection: React.FC<BasePowerstonesSectionProps> = ({ stoneData }) => {
    return (
        <Stack gap="md">
            {STONE_CONFIGS.map((cfg) => (
                <PowerstoneCard
                    key={cfg.key}
                    labelEn={cfg.labelEn}
                    labelJp={cfg.labelJp}
                    stone={stoneData[cfg.key]}
                    icon={cfg.icon}
                />
            ))}
        </Stack>
    );
};

export default BasePowerstonesSection;
