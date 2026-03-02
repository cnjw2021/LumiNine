'use client';

import React from 'react';
import { Paper, Title, Text, Box, Group, Badge, Stack } from '@mantine/core';
import KyuseiBoard_Compact from '@/app/svg-test/components/KyuseiBoard_Compact';

interface MainStarKyuseiBoardProps {
  mainStar: number;
  mainStarName: string;
  mainStarElement?: string;
  description?: string;
  keywords?: string[];
  size?: number;
}

// 九星の名前マッピング
const STAR_NAMES: Record<number, string> = {
  1: "一白水星",
  2: "二黒土星", 
  3: "三碧木星",
  4: "四緑木星",
  5: "五黄土星",
  6: "六白金星",
  7: "七赤金星",
  8: "八白土星",
  9: "九紫火星"
};

// 五行の色マッピング
const ELEMENT_COLORS: Record<string, string> = {
  水: "#3B82F6", // 青
  土: "#F59E0B", // 黄
  木: "#22C55E", // 緑
  金: "#D4AF37", // 金
  火: "#EF4444"  // 赤
};

// 五行マッピング
const STAR_ELEMENTS: Record<number, string> = {
  1: "水",
  2: "土",
  3: "木", 
  4: "木",
  5: "土",
  6: "金",
  7: "金",
  8: "土",
  9: "火"
};

const MainStarKyuseiBoard: React.FC<MainStarKyuseiBoardProps> = ({
  mainStar,
  mainStarName,
  mainStarElement,
  description,
  keywords = [],
  size = 280
}) => {
  const starName = STAR_NAMES[mainStar] || mainStarName;
  const element = mainStarElement || STAR_ELEMENTS[mainStar];
  const elementColor = ELEMENT_COLORS[element] || "#6B7280";

  return (
    <Paper shadow="sm" p="md" withBorder>
      <Stack gap="md">
        <Title order={3} ta="center" c="dark">
          本命星（性格・運命の流れ）
        </Title>
        
        <Box>
          <div style={{ 
            display: 'flex', 
            gap: '20px', 
            alignItems: 'flex-start',
            flexWrap: 'wrap'
          }}>
            {/* 左側：コンパクト九星盤 */}
            <div style={{ flex: '0 0 300px', minWidth: '280px' }}>
              <KyuseiBoard_Compact
                centerStar={starName}
                size={size}
                theme="classic"
                backgroundGradient="classic"
              />
            </div>
            
            {/* 右側：詳細情報 */}
            <div style={{ 
              flex: '1', 
              minWidth: '300px',
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              {/* 星番号と五行 */}
              <Group mb="md" align="center">
                <div style={{ 
                  backgroundColor: elementColor, 
                  color: 'white', 
                  padding: '8px 16px', 
                  borderRadius: '20px', 
                  fontSize: '1.2rem', 
                  fontWeight: 'bold'
                }}>
                  {mainStar}
                </div>
                <Badge 
                  color="gray" 
                  variant="light"
                  style={{ 
                    backgroundColor: `${elementColor}20`,
                    color: elementColor,
                    fontSize: '0.9rem'
                  }}
                >
                  五行：{element}
                </Badge>
              </Group>
              
              {/* 星の名前 */}
              <Title 
                order={2} 
                mb="md"
                style={{ 
                  color: elementColor,
                  fontSize: '1.5rem'
                }}
              >
                {starName}
              </Title>
              
              {/* キーワード */}
              {keywords.length > 0 && (
                <Group mb="md" gap="xs">
                  {keywords.map((keyword, index) => (
                    <Badge 
                      key={index}
                      variant="light"
                      color="gray"
                      size="sm"
                    >
                      {keyword}
                    </Badge>
                  ))}
                </Group>
              )}
              
              {/* 説明文 */}
              {description && (
                <Text 
                  size="sm" 
                  style={{ 
                    lineHeight: '1.6', 
                    color: '#333'
                  }}
                >
                  {description}
                </Text>
              )}
            </div>
          </div>
        </Box>
      </Stack>
    </Paper>
  );
};

export default MainStarKyuseiBoard; 