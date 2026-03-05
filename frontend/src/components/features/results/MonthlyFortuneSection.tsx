'use client';

import React from 'react';
import { GogyoStone, PeriodFortuneData } from '@/types/directionFortune';

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
                fontSize: '10px', color: '#4a4a4a', padding: '2px 8px',
                border: '1px solid rgba(212, 175, 55, 0.4)', borderRadius: '4px',
                fontFamily: '"Noto Serif JP", serif'
            }}>{type}</span>
        </div>
        <h4 style={{
            fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
            color: '#4a4a4a', fontSize: '16px', fontWeight: 700, marginBottom: '8px', marginTop: 0
        }}>
            {stone.stone_name}
        </h4>
        <p style={{
            fontFamily: '"Noto Serif JP", serif', fontSize: '13px',
            color: 'rgba(74, 74, 74, 0.8)', lineHeight: 1.8, margin: 0
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
                    color: 'rgba(74, 74, 74, 0.4)', fontSize: '10px',
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
                                /**
                                 * 中宮 (center palace) is always rendered as neutral.
                                 * In Nine Star Ki, the center position represents the
                                 * observer's current star — it has no directional fortune.
                                 * API `directions` may include a `center` key, but it is
                                 * intentionally ignored here by design.
                                 */
                                return (
                                    <div key={dir} style={{
                                        aspectRatio: '1/1', borderRadius: '14px',
                                        backgroundColor: '#ffffff',
                                        display: 'flex', flexDirection: 'column',
                                        alignItems: 'center', justifyContent: 'center',
                                        border: '1px solid rgba(212, 175, 55, 0.2)',
                                        boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
                                    }}>
                                        <span style={{ fontSize: '10px', color: '#d4af37', fontWeight: 700, marginBottom: '4px', fontFamily: '"Noto Serif JP", serif' }}>中宮</span>
                                        <span style={{ color: '#d4af37', fontSize: '20px' }}>○</span>
                                    </div>
                                );
                            }

                            const info = currentMonthData.directions?.[dir];
                            const isAuspicious = info?.is_auspicious === true;
                            const isInauspicious = info?.is_auspicious === false;

                            let bgColor = 'transparent';
                            let textColor = '#4a4a4a';
                            let icon = '·';

                            if (isAuspicious) {
                                bgColor = 'rgba(155, 176, 165, 0.1)';
                                textColor = '#9bb0a5';
                                icon = '✿';
                            } else if (isInauspicious) {
                                bgColor = 'rgba(239, 213, 195, 0.3)';
                                textColor = '#d8a7a7';
                                icon = '✕';
                            }

                            return (
                                <div key={dir} style={{
                                    aspectRatio: '1/1', borderRadius: '14px',
                                    backgroundColor: bgColor,
                                    display: 'flex', flexDirection: 'column',
                                    alignItems: 'center', justifyContent: 'center',
                                    border: '1px solid #ffffff'
                                }}>
                                    <span style={{
                                        fontSize: '9px', color: textColor, fontWeight: 700,
                                        marginBottom: '4px', fontFamily: '"Montserrat", sans-serif'
                                    }}>
                                        {DIRECTION_ABBR[dir]}
                                    </span>
                                    <span style={{ color: textColor, fontSize: '16px' }}>{icon}</span>
                                </div>
                            );
                        })}
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
