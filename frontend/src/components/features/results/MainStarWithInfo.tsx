'use client';

import React from 'react';
import { Paper, Title, Box, Text, Group, Badge, Stack } from '@mantine/core';

// 星の型定義
interface Star {
  id?: number;
  number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;  // キーワードを追加
  title?: string;     // 特性タイトルを追加
  advice?: string;    // アドバイスを追加
}

interface MainStarWithInfoProps {
  star: Star;
  title?: string;
  isMonthStar?: boolean;  // 月命星かどうか
  isDayStar?: boolean;    // 日命星かどうか
}

/**
 * 본명성/월명성을 심플하게 표시하는 컴포넌트
 */
const MainStarWithInfo: React.FC<MainStarWithInfoProps> = ({
  star,
  title = '本命星(基本性格・運命の流れ)',
  isMonthStar = false,
  isDayStar = false
}) => {
  if (!star) return null;

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

  const starColor = getStarColor(star.number);

  // 별의 키워드 추출
  const getStarKeywords = (star: Star): string[] => {
    if (star.keywords) {
      return star.keywords.split(/[,、・\s]+/).map(keyword => keyword.trim()).filter(keyword => keyword);
    }
    return [];
  };

  const starKeywords = getStarKeywords(star);

  // 컨테이너 배경색 설정
  const bgColor = `linear-gradient(135deg, ${starColor}05, ${starColor}08)`;

  return (
    <Paper
      shadow="sm"
      p={0}
      radius="md"
      style={{
        background: '#ffffff',
        border: '1px solid #e0e0e0',
        position: 'relative',
        width: '100%',
        margin: '0 0 20px 0',
        padding: 0,
        boxSizing: 'border-box',
        overflow: 'hidden'
      }}
    >
      {/* 타이틀 바 추가 */}
      <Box style={{
        borderBottom: '1px solid #e0e0e0',
        background: '#f8f9fa'
      }}>
        <Title
          order={3}
          ta="center"
          style={{
            color: '#333',
            fontSize: '1.1rem',
            fontWeight: 700,
            padding: '12px 16px',
            margin: 0
          }}
        >
          {title}
        </Title>
      </Box>

      {/* 메인 콘텐츠 영역 */}
      <Box style={{
        padding: '30px 20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: bgColor
      }}>
        <Stack align="center" gap="lg" style={{ width: '100%' }}>

          {/* 큰 별 숫자 */}
          <Box style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '80px',
            height: '80px',
            borderRadius: '16px',
            background: starColor,
            boxShadow: `0 4px 15px ${starColor}40`
          }}>
            <Text
              fw={800}
              style={{
                color: 'white',
                fontSize: '3rem',
                lineHeight: 1
              }}
            >
              {star.number}
            </Text>
          </Box>

          {/* 키워드 태그들 */}
          {starKeywords.length > 0 && (
            <Group gap="sm" justify="center" style={{ maxWidth: '600px' }}>
              {starKeywords.map((keyword, index) => (
                <Badge
                  key={index}
                  color={starColor}
                  size="md"
                  radius="sm"
                  variant="light"
                  style={{
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    padding: '0.4rem 0.8rem',
                    backgroundColor: `${starColor}15`,
                    color: starColor,
                    border: `1px solid ${starColor}30`
                  }}
                >
                  {keyword}
                </Badge>
              ))}
            </Group>
          )}

        </Stack>
      </Box>
    </Paper>
  );
};

export default MainStarWithInfo; 