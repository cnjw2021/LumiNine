'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { GogyoStone, PeriodFortuneData } from '@/types/directionFortune';
import { getStoneImagePath } from '@/utils/stoneImageMap';

interface MonthlyFortuneSectionProps {
    currentMonthData: PeriodFortuneData | null;
    monthlyStone: GogyoStone | null;
    protectionStone: GogyoStone | null;
}

const DIRECTION_ORDER = [
    'southeast', 'south', 'southwest',
    'east', 'center', 'west',
    'northeast', 'north', 'northwest'
];

const DIRECTION_ABBR: Record<string, string> = {
    southeast: 'SE', south: 'S', southwest: 'SW',
    east: 'E', center: '中宮', west: 'W',
    northeast: 'NE', north: 'N', northwest: 'NW',
};

/** Stone card for monthly/protection stone */
const MonthlyStoneCard: React.FC<{ label: string; stone: GogyoStone; type: string }> = ({ label, stone, type }) => (
    <div style={{
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(212, 175, 55, 0.1)',
        padding: '24px', borderRadius: '20px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.02)',
        height: '100%',
    }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{
                fontSize: '10px', letterSpacing: '0.15em', color: '#d4af37',
                fontFamily: '"Montserrat", sans-serif', fontWeight: 600
            }}>{label} GUIDANCE</span>
            <span style={{
                fontSize: '11px', color: '#3a3a3a', padding: '3px 10px',
                border: '1px solid rgba(212, 175, 55, 0.5)', borderRadius: '4px',
                fontFamily: '"Noto Serif JP", serif', fontWeight: 600,
            }}>{type}</span>
        </div>

        {/* Stone Image + Name row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <div style={{
                width: '48px', height: '48px',
                borderRadius: '50%', overflow: 'hidden',
                border: '1px solid rgba(212, 175, 55, 0.2)',
                backgroundColor: '#f9f7f2', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
                <Image
                    src={getStoneImagePath(stone.stone_id)}
                    alt={stone.stone_name}
                    width={44}
                    height={44}
                    style={{ objectFit: 'cover', borderRadius: '50%' }}
                />
            </div>
            <h4 style={{
                fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                color: '#4a4a4a', fontSize: '16px', fontWeight: 700, margin: 0
            }}>
                {stone.stone_name}
            </h4>
        </div>

        <p style={{
            fontFamily: '"Noto Serif JP", serif', fontSize: '13px',
            color: '#4a4a4a', lineHeight: 1.8, margin: 0
        }}>
            {stone.reason}
        </p>
    </div>
);

const MonthlyFortuneSection: React.FC<MonthlyFortuneSectionProps> = ({
    currentMonthData,
    monthlyStone,
    protectionStone,
}) => {
    const [selectedDirection, setSelectedDirection] = useState<string | null>(null);

    return (
        <section>
            {/* Directional Guide Header */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                <h3 style={{
                    color: '#d4af37', fontSize: '11px', letterSpacing: '0.3em',
                    fontWeight: 500, textTransform: 'uppercase' as const,
                    fontFamily: '"Montserrat", sans-serif', margin: 0
                }}>
                    Directional Guide
                </h3>
                <span style={{
                    color: 'rgba(74, 74, 74, 0.5)', fontSize: '10px',
                    fontFamily: '"Montserrat", sans-serif', letterSpacing: '0.1em'
                }}>
                    {currentMonthData?.display_month || '今月'}
                </span>
            </div>

            {/* 3×3 Direction Grid Board */}
            {currentMonthData && (
                <div className="direction-grid-board" style={{
                    position: 'relative',
                    backgroundColor: 'rgba(255, 255, 255, 0.4)',
                    borderRadius: '20px',
                    border: '1px solid #ffffff',
                    boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
                    marginBottom: '36px'
                }}>
                    {/* Cross Lines */}
                    <div style={{ position: 'absolute', top: '40px', bottom: '40px', left: '33.33%', width: '1px', background: 'linear-gradient(180deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />
                    <div style={{ position: 'absolute', top: '40px', bottom: '40px', right: '33.33%', width: '1px', background: 'linear-gradient(180deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />
                    <div style={{ position: 'absolute', left: '40px', right: '40px', top: '33.33%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />
                    <div style={{ position: 'absolute', left: '40px', right: '40px', bottom: '33.33%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', position: 'relative', zIndex: 10 }}>
                        {DIRECTION_ORDER.map((dir) => {
                            if (dir === 'center') {
                                return (
                                    <div
                                        key={dir}
                                        onClick={() => setSelectedDirection(dir)}
                                        style={{
                                            aspectRatio: '1/1', borderRadius: '14px',
                                            backgroundColor: '#ffffff',
                                            display: 'flex', flexDirection: 'column',
                                            alignItems: 'center', justifyContent: 'center',
                                            border: '1px solid rgba(212, 175, 55, 0.2)',
                                            boxShadow: selectedDirection === dir
                                                ? '0 0 0 2px rgba(212, 175, 55, 0.6), inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
                                                : 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s ease'
                                        }}
                                    >
                                        <span style={{ fontSize: '10px', color: '#d4af37', fontWeight: 700, marginBottom: '4px', fontFamily: '"Noto Serif JP", serif' }}>中宮</span>
                                        <span style={{ color: '#d4af37', fontSize: '20px' }}>○</span>
                                    </div>
                                );
                            }

                            const info = currentMonthData.directions?.[dir];
                            const fortuneLevel = info?.fortune_level ?? (
                                info?.is_auspicious === true ? 'auspicious'
                                    : info?.is_auspicious === false ? 'inauspicious'
                                        : 'neutral'
                            );

                            let bgColor = 'transparent';
                            let textColor = '#a0a0a0';
                            let icon = '·';

                            switch (fortuneLevel) {
                                case 'best_auspicious':
                                    bgColor = 'rgba(212, 175, 55, 0.12)';
                                    textColor = '#b8860b';
                                    icon = '✿';
                                    break;
                                case 'auspicious':
                                    bgColor = 'rgba(90, 138, 110, 0.10)';
                                    textColor = '#3d7a56';
                                    icon = '✿';
                                    break;
                                case 'inauspicious':
                                    bgColor = 'rgba(192, 82, 77, 0.08)';
                                    textColor = '#b04a46';
                                    icon = '✕';
                                    break;
                                default: // neutral
                                    bgColor = 'transparent';
                                    textColor = '#a0a0a0';
                                    icon = '·';
                            }

                            return (
                                <div
                                    key={dir}
                                    onClick={() => setSelectedDirection(dir)}
                                    style={{
                                        aspectRatio: '1/1', borderRadius: '14px',
                                        backgroundColor: bgColor,
                                        display: 'flex', flexDirection: 'column',
                                        alignItems: 'center', justifyContent: 'center',
                                        border: '1px solid #ffffff',
                                        boxShadow: selectedDirection === dir ? '0 0 0 2px rgba(212, 175, 55, 0.6)' : 'none',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s ease'
                                    }}
                                    title={info?.reason || '無難'}
                                >
                                    <span style={{
                                        fontSize: '10px', color: textColor, fontWeight: 700,
                                        marginBottom: '4px', fontFamily: '"Montserrat", sans-serif'
                                    }}>
                                        {DIRECTION_ABBR[dir]}
                                    </span>
                                    <span style={{ color: textColor, fontSize: '18px', fontWeight: 700 }}>{icon}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Selected Direction Detail Box (Mobile Friendly Tooltip alternative) */}
            {selectedDirection && currentMonthData && (
                <div style={{
                    marginTop: '-20px',
                    marginBottom: '36px',
                    padding: '16px 20px',
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid rgba(212, 175, 55, 0.2)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.03)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    animation: 'fadeIn 0.3s ease'
                }}>
                    <div style={{
                        fontFamily: '"Montserrat", sans-serif',
                        fontSize: '16px',
                        fontWeight: 700,
                        color: '#d4af37',
                        width: '40px',
                        textAlign: 'center',
                        flexShrink: 0
                    }}>
                        {DIRECTION_ABBR[selectedDirection]}
                    </div>
                    <div style={{ width: '1px', alignSelf: 'stretch', backgroundColor: 'rgba(212, 175, 55, 0.2)' }}></div>
                    <div style={{ flex: 1 }}>
                        <p style={{
                            margin: 0,
                            fontFamily: '"Noto Serif JP", serif',
                            fontSize: '13px',
                            color: '#4a4a4a',
                            lineHeight: 1.6
                        }}>
                            {selectedDirection === 'center'
                                ? '無難'
                                : (currentMonthData.directions?.[selectedDirection]?.reason || '無難')}
                        </p>
                    </div>
                </div>
            )}

            {/* Monthly and Protection Stones */}
            {(monthlyStone || protectionStone) && (
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                        <h3 style={{
                            fontFamily: '"Montserrat", sans-serif', color: '#d4af37',
                            fontSize: '11px', letterSpacing: '0.3em', fontWeight: 500,
                            textTransform: 'uppercase' as const, margin: 0
                        }}>
                            Monthly Guidance Stones
                        </h3>
                    </div>
                    <div className="monthly-stones-grid">
                        {monthlyStone && (
                            <MonthlyStoneCard label="MONTHLY" stone={monthlyStone} type="月運" />
                        )}
                        {protectionStone && (
                            <MonthlyStoneCard label="PROTECTION" stone={protectionStone} type="護身" />
                        )}
                    </div>
                </div>
            )}
        </section>
    );
};

export default MonthlyFortuneSection;
