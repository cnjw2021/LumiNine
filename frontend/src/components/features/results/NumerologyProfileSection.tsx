'use client';

import React from 'react';
import { NumerologyStone, SixLayerPowerStones } from '@/types/directionFortune';

interface NumerologyProfileSectionProps {
    stoneData: SixLayerPowerStones;
}

/**
 * Section A: 数秘術プロフィール — Stitch Design
 * Circular wreath with life path number + title + description
 */
const NumerologyProfileSection: React.FC<NumerologyProfileSectionProps> = ({ stoneData }) => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>

            {/* Botanical Wreath Circle */}
            <div style={{
                position: 'relative',
                width: '200px', height: '200px',
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                borderRadius: '50%',
                border: '1px solid rgba(212, 175, 55, 0.2)',
                backgroundColor: '#ffffff',
                boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
                marginBottom: '24px'
            }}>
                <span style={{
                    fontSize: '10px', fontFamily: '"Montserrat", sans-serif',
                    letterSpacing: '0.4em', color: '#d4af37', marginBottom: '8px'
                }}>
                    NUMEROLOGY
                </span>
                <span style={{
                    fontSize: '36px', fontWeight: 700,
                    fontFamily: '"Noto Serif JP", serif',
                    color: '#d8a7a7', lineHeight: 1
                }}>
                    {stoneData.life_path_number}
                </span>
                {stoneData.title && (
                    <span style={{
                        fontSize: '16px',
                        fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                        marginTop: '4px', letterSpacing: '0.1em', color: '#4a4a4a'
                    }}>
                        {stoneData.title}
                    </span>
                )}
            </div>

            {/* Description Text */}
            {stoneData.traits && (
                <p style={{
                    color: 'rgba(74, 74, 74, 0.7)',
                    fontSize: '13px', lineHeight: 1.7,
                    fontFamily: '"Noto Serif JP", serif',
                    maxWidth: '280px', margin: 0
                }}>
                    {stoneData.traits}
                </p>
            )}
        </div>
    );
};

export default NumerologyProfileSection;
