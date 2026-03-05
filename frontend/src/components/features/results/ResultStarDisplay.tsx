'use client';

import React from 'react';

interface StarInfo {
    star_number: number;
    name_jp: string;
    name_en?: string;
    element?: string;
}

interface ResultStarDisplayProps {
    mainStar: StarInfo;
    monthStar: StarInfo;
    dayStar: StarInfo;
}

// 星番号に基づいて色を返す関数
const getStarColor = (starNumber: number): string => {
    const colors = [
        '#3490dc',  // 1: 一白水星 - 鮮やかな青
        '#2d3748',  // 2: 二黒土星 - 深い黒
        '#38a169',  // 3: 三碧木星 - 爽やかな緑
        '#319795',  // 4: 四緑木星 - ティール
        '#ecc94b',  // 5: 五黄土星 - 黄金色
        '#a0aec0',  // 6: 六白金星 - シルバー
        '#e53e3e',  // 7: 七赤金星 - 情熱的な赤
        '#805ad5',  // 8: 八白土星 - 神秘的な紫
        '#ed64a6'   // 9: 九紫火星 - 鮮やかなピンク
    ];
    return colors[starNumber - 1] || '#3490dc';
};

const StarBox: React.FC<{ label: string; star: StarInfo }> = ({ label, star }) => {
    const color = getStarColor(star.star_number);

    return (
        <div style={{
            borderRadius: '8px',
            padding: '10px',
            backgroundColor: `${color}10`,
            border: `2px solid ${color}80`,
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
        }}>
            <p style={{ fontSize: '0.75rem', fontWeight: 600, color: '#666', margin: '0 0 5px 0' }}>{label}</p>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '2px' }}>
                <span style={{
                    fontSize: '2.2rem',
                    fontWeight: 800,
                    color: color,
                    lineHeight: 1,
                    textShadow: '0px 2px 4px rgba(0,0,0,0.1)',
                    margin: 0
                }}>
                    {star.star_number}
                </span>
                <span style={{
                    margin: '2px 0',
                    fontWeight: 600,
                    fontSize: '0.6rem',
                    backgroundColor: color,
                    color: 'white',
                    padding: '2px 4px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap',
                    minWidth: 'auto'
                }}>
                    {star.name_jp}
                </span>
            </div>
        </div>
    );
};

export default function ResultStarDisplay({ mainStar, monthStar, dayStar }: ResultStarDisplayProps) {
    return (
        <div style={{ margin: '20px 0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                <StarBox label="本命星" star={mainStar} />
                <StarBox label="月命星" star={monthStar} />
                <StarBox label="日命星" star={dayStar} />
            </div>
        </div>
    );
}
