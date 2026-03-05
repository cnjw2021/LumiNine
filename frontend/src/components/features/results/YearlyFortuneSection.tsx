'use client';

import React from 'react';
import { NumerologyStone } from '@/types/directionFortune';

interface YearlyFortuneSectionProps {
    yearlyStone: NumerologyStone;
    personalYearNumber?: number;
    targetYear?: number;
}

const YearlyFortuneSection: React.FC<YearlyFortuneSectionProps> = ({
    yearlyStone,
    personalYearNumber,
    targetYear,
}) => {
    const currentYear = targetYear || new Date().getFullYear();

    return (
        <section style={{ position: 'relative' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
                <h3 style={{
                    color: '#d4af37', fontSize: '11px', letterSpacing: '0.3em',
                    fontWeight: 500, textTransform: 'uppercase' as const,
                    flexShrink: 0, fontFamily: '"Montserrat", sans-serif', margin: 0
                }}>
                    Yearly Fortune {currentYear}
                </h3>
                <div style={{ height: '1px', backgroundColor: 'rgba(212, 175, 55, 0.2)', width: '100%' }} />
            </div>

            {/* Card Container */}
            <div style={{
                position: 'relative',
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                borderRadius: '32px',
                padding: '36px',
                border: '1px solid rgba(212, 175, 55, 0.1)',
                boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
                overflow: 'hidden'
            }}>
                {/* Decorative background circle */}
                <div style={{
                    position: 'absolute', top: 0, right: 0,
                    width: '200px', height: '200px',
                    backgroundColor: 'rgba(216, 167, 167, 0.05)',
                    borderRadius: '50%',
                    transform: 'translate(50%, -50%)'
                }} />

                {/* Inner Grid: Icon left + Description right */}
                <div className="yearly-fortune-inner" style={{ position: 'relative', zIndex: 10 }}>
                    {/* Left: Stone icon + name */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <div style={{
                            width: '100px', height: '100px',
                            borderRadius: '50%',
                            backgroundColor: '#f9f7f2',
                            border: '1px solid rgba(212, 175, 55, 0.3)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            marginBottom: '12px'
                        }}>
                            <span style={{ fontSize: '40px', color: '#d4af37' }}>👁</span>
                        </div>
                        <span style={{
                            fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                            fontSize: '18px', color: '#4a4a4a', fontWeight: 700
                        }}>
                            {yearlyStone.stone_name}
                        </span>
                    </div>

                    {/* Right: Description */}
                    <div style={{ borderLeft: '1px solid rgba(212, 175, 55, 0.1)', paddingLeft: '24px' }}>
                        <p style={{
                            color: 'rgba(74, 74, 74, 0.8)',
                            fontFamily: '"Noto Serif JP", serif',
                            fontSize: '15px', lineHeight: 1.8, margin: 0
                        }}>
                            {yearlyStone.description}
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default YearlyFortuneSection;
