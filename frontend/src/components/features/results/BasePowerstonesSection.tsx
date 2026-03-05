'use client';

import React from 'react';
import { NumerologyStone, SixLayerPowerStones } from '@/types/directionFortune';

interface BasePowerstonesSectionProps {
    stoneData: SixLayerPowerStones;
}

const STONE_CONFIGS = [
    { labelEn: 'OVERALL', labelJp: '全体運', key: 'overall_stone' as const, icon: '💎', color: '#d8a7a7' },
    { labelEn: 'HEALTH', labelJp: '健康運', key: 'health_stone' as const, icon: '🌿', color: '#9bb0a5' },
    { labelEn: 'WEALTH', labelJp: '金運', key: 'wealth_stone' as const, icon: '¥', color: '#d4af37' },
    { labelEn: 'LOVE', labelJp: '恋愛運', key: 'love_stone' as const, icon: '♡', color: '#d8a7a7' },
];

const PowerstoneCard: React.FC<{
    labelEn: string;
    labelJp: string;
    stone: NumerologyStone;
    icon: string;
    color: string;
}> = ({ labelEn, labelJp, stone, icon, color }) => (
    <div style={{
        display: 'flex',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.6)',
        padding: '16px 20px',
        borderRadius: '16px',
        border: '1px solid #ffffff',
        boxShadow: '0 4px 20px -5px rgba(0, 0, 0, 0.04)',
    }}>
        {/* Icon Box */}
        <div style={{
            width: '52px', height: '52px',
            backgroundColor: '#f5f0eb',
            borderRadius: '14px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            marginRight: '16px', flexShrink: 0,
        }}>
            <span style={{ fontSize: '22px', color, lineHeight: 1 }}>
                {icon}
            </span>
        </div>

        {/* Text Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '2px' }}>
                <span style={{
                    fontSize: '10px', color: '#d4af37', fontWeight: 700,
                    letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif',
                }}>
                    {labelEn}
                </span>
                <span style={{
                    fontSize: '11px', color: 'rgba(74, 74, 74, 0.35)',
                    fontFamily: '"Noto Serif JP", serif',
                }}>
                    {labelJp}
                </span>
            </div>
            <span style={{
                fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                color: '#4a4a4a', fontSize: '15px', fontWeight: 700,
                display: 'block',
            }}>
                {stone.stone_name}
            </span>
        </div>
    </div>
);

const BasePowerstonesSection: React.FC<BasePowerstonesSectionProps> = ({ stoneData }) => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {STONE_CONFIGS.map((cfg) => (
                <PowerstoneCard
                    key={cfg.key}
                    labelEn={cfg.labelEn}
                    labelJp={cfg.labelJp}
                    stone={stoneData[cfg.key]}
                    icon={cfg.icon}
                    color={cfg.color}
                />
            ))}
        </div>
    );
};

export default BasePowerstonesSection;
