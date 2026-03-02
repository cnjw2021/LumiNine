'use client';

import React, { useState, useEffect } from 'react';
import { Card, Text, Box, Loader } from '@mantine/core';
import { fetchStarLifeGuidance, StarLifeGuidanceResult } from '@/lib/api/nineStarKiApi';

interface StarLifeGuidanceProps {
  mainStar: number;
  monthStar: number;
}

const StarLifeGuidance: React.FC<StarLifeGuidanceProps> = ({ mainStar, monthStar }) => {
  const [loading, setLoading] = useState(true);
  const [guidanceData, setGuidanceData] = useState<StarLifeGuidanceResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await fetchStarLifeGuidance(mainStar, monthStar);
        setGuidanceData(data);
        setError(null);
      } catch (err) {
        console.error('星と人生のガイダンス情報の取得に失敗しました:', err);
        setError('データの読み込みに失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (mainStar && monthStar) {
      fetchData();
    }
  }, [mainStar, monthStar]);

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

  const mainStarColor = getStarColor(mainStar);

  return (
    <Card 
      shadow="md" 
      p="xl" 
      radius="sm" 
      withBorder
      style={{ 
        marginBottom: '1.5rem',
        background: `linear-gradient(145deg, white, ${mainStarColor}05)`,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* 背景装飾 */}
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: '150px',
        height: '150px',
        background: `radial-gradient(circle at top right, ${mainStarColor}10, transparent 70%)`,
        zIndex: 0
      }} />

      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          marginBottom: '20px',
          gap: '12px'
        }}>
          <h3 style={{
            fontSize: '1.4rem', 
            margin: 0, 
            fontWeight: 600,
            background: `linear-gradient(135deg, #333, ${mainStarColor})`,
            WebkitBackgroundClip: 'text',
          }}>
            適職
          </h3>
        </div>

        {loading ? (
          <Box style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
            <Loader size="md" color={mainStarColor} />
          </Box>
        ) : error ? (
          <Text c="red.7" ta="center" py="md">{error}</Text>
        ) : guidanceData ? (
          <>
            <Box>
              <Text 
                style={{ 
                  whiteSpace: 'pre-wrap', 
                  lineHeight: '1.8', 
                  fontSize: '1rem',
                  padding: '0 0.5rem 0.5rem',
                  color: '#444',
                  textAlign: 'justify'
                }}
              >
                {guidanceData.job}
              </Text>
            </Box>
          </>
        ) : ""}
      </div>
    </Card>
  );
};

export default StarLifeGuidance;