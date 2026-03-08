'use client';

import React from 'react';

interface FoodRecommendationSectionProps {
    foods: string[];
    element: string;
}

/** 五行 → 表示用アイコン・色マッピング */
const ELEMENT_STYLE: Record<string, { icon: string; color: string; label: string }> = {
    '水': { icon: '💧', color: '#5b8fa8', label: '水 Water' },
    '木': { icon: '🌿', color: '#6a9b5e', label: '木 Wood' },
    '火': { icon: '🔥', color: '#c0594a', label: '火 Fire' },
    '土': { icon: '🏔', color: '#a08050', label: '土 Earth' },
    '金': { icon: '✨', color: '#b8952b', label: '金 Metal' },
};

const FoodRecommendationSection: React.FC<FoodRecommendationSectionProps> = ({ foods, element }) => {
    if (!foods || foods.length === 0) return null;

    const style = ELEMENT_STYLE[element] || { icon: '🍽', color: '#d4af37', label: element };

    return (
        <div>
            {/* Section Header */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                <h3 style={{
                    color: '#d4af37', fontSize: '11px', letterSpacing: '0.3em',
                    fontWeight: 500, textTransform: 'uppercase' as const,
                    fontFamily: '"Montserrat", sans-serif', margin: 0
                }}>
                    Recommended Foods
                </h3>
                <div style={{ width: '48px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />
            </div>

            {/* Element Badge */}
            <div style={{
                display: 'flex', justifyContent: 'center', marginBottom: '16px',
            }}>
                <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: '6px',
                    padding: '4px 14px', borderRadius: '9999px',
                    backgroundColor: `${style.color}10`,
                    border: `1px solid ${style.color}30`,
                    fontSize: '11px', color: style.color,
                    fontFamily: '"Montserrat", sans-serif',
                    letterSpacing: '0.1em', fontWeight: 600,
                }}>
                    {style.icon} {style.label}
                </span>
            </div>

            {/* Food Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {foods.map((food, i) => (
                    <div key={i} style={{
                        display: 'flex', alignItems: 'center',
                        backgroundColor: 'rgba(255, 255, 255, 0.6)',
                        padding: '14px 20px',
                        borderRadius: '16px',
                        border: '1px solid #ffffff',
                        boxShadow: '0 4px 20px -5px rgba(0, 0, 0, 0.04)',
                        pageBreakInside: 'avoid',
                    }}>
                        {/* Icon Circle */}
                        <div style={{
                            width: '40px', height: '40px',
                            borderRadius: '50%',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            marginRight: '14px', flexShrink: 0,
                            backgroundColor: `${style.color}08`,
                            border: `1px solid ${style.color}20`,
                            fontSize: '18px',
                        }}>
                            🍽
                        </div>

                        {/* Text */}
                        <span style={{
                            fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                            color: '#4a4a4a', fontSize: '14px', fontWeight: 500,
                            lineHeight: 1.5,
                        }}>
                            {food}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FoodRecommendationSection;
