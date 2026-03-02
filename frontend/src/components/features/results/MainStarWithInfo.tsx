'use client';

import React from 'react';
import { Paper, Grid, Title, Box, Text, Card, Group, Badge, Divider, Stack } from '@mantine/core';
import KyuseiBoard_Compact from '@/app/svg-test/components/KyuseiBoard_Compact';

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
 * 本命星のSVG画像と基本情報を同時に表示するコンポーネント
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

  // 五行の色とスタイルを取得
  const getElementStyle = (element?: string): { color: string, bgColor: string, symbol: string } => {
    if (!element) return { color: '#6c757d', bgColor: '#f8f9fa', symbol: '?' };
    
    switch (element) {
      case '金': return { color: '#d4af37', bgColor: 'rgba(251, 211, 141, 0.2)', symbol: '◯' };
      case '木': return { color: '#228b22', bgColor: 'rgba(144, 238, 144, 0.2)', symbol: '▱' };
      case '水': return { color: '#1e90ff', bgColor: 'rgba(173, 216, 230, 0.2)', symbol: '▽' };
      case '火': return { color: '#ff4500', bgColor: 'rgba(255, 192, 173, 0.2)', symbol: '△' };
      case '土': return { color: '#8b4513', bgColor: 'rgba(222, 184, 135, 0.2)', symbol: '□' };
      default: return { color: '#6c757d', bgColor: '#f8f9fa', symbol: '?' };
    }
  };

  const starColor = getStarColor(star.number);
  const elementStyle = getElementStyle(star.element);

  // 星と五行に基づく共通のグラデーションを生成
  const commonGradient = `linear-gradient(135deg, ${elementStyle.color}15, ${starColor}10, ${elementStyle.color}20)`;

  // 星のキーワードを取得
  const getStarKeywords = (star: Star): string[] => {
    // バックエンドから返されたkeywordsプロパティがある場合はそれを使用
    if (star.keywords) {
      // カンマ区切りのキーワードを配列に変換
      return star.keywords.split(/[,、・\s]+/).map(keyword => keyword.trim()).filter(keyword => keyword);
    }
    return [];
  };

  const starKeywords = getStarKeywords(star);

  // 基本情報・鑑定結果（SVGの下）のタイトルを決定
  const getInfoSectionTitle = () => {
    if (isDayStar) return '日命星の特性';
    if (isMonthStar) return '月命星の特性';
    return '基本情報・運命の大きな流れ';
  };

  return (
    <Paper 
      shadow="sm" 
      p={0}
      radius="md"
      style={{ 
        background: 'linear-gradient(to bottom right, rgba(255,255,255,0.98), rgba(245,247,250,0.9))',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(209, 213, 219, 0.5)',
        position: 'relative',
        width: '100%',
        margin: 0,
        padding: 0,
        boxSizing: 'border-box',
        overflow: 'hidden'
      }}
    >
      {/* メインコンテンツ */}
      <Box style={{ position: 'relative', zIndex: 1, width: '100%', padding: 0 }}>
        <Title 
          order={2} 
          mb={{ base: 'xs', sm: 'sm' }} 
          ta="center" 
          style={{ 
            color: '#2d3748',
            fontSize: 'clamp(0.9rem, 2.5vw, 1.4rem)',
            fontWeight: 700,
            letterSpacing: '0.01em',
            padding: '12px 16px',
            textAlign: 'center',
            width: '100%',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            lineHeight: 1.4,
            boxSizing: 'border-box',
            hyphens: 'auto',
            borderBottom: '1px solid rgba(209, 213, 219, 0.8)'
          }}
        >
          {title}
        </Title>
        
        {/* SVGと詳細情報のコンテナ */}
        <Card 
          shadow="xs" 
          p="md"
          radius={0}
          style={{ 
            background: commonGradient,
            backdropFilter: 'blur(8px)',
            border: 0,
            borderTop: `1px solid ${starColor}20`,
            borderBottom: `1px solid ${starColor}20`,
            marginBottom: 0,
            width: '100%',
            padding: '16px'
          }}
        >
          <Grid gutter={{ base: 'md', sm: 'lg' }} align="center">
            {/* SVG画像（左側） */}
            <Grid.Col span={{ base: 12, md: 5 }} order={{ base: 1, md: 1 }}>
                <Card 
                  p={0}
                  radius="sm" 
                  style={{
                    background: 'transparent',
                    border: 'none',
                    boxShadow: 'none',
                    position: 'relative',
                    overflow: 'visible',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    width: '100%',
                    height: '320px',
                    padding: '0'
                  }}
                >
                  {/* 九星盤表示 */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    width: '320px',
                    height: '320px',
                    position: 'relative'
                  }}>
                    <KyuseiBoard_Compact
                      centerStar={star.name_jp}
                      size={320}
                      theme="classic"
                      backgroundGradient="classic"
                    />
                  </div>
                </Card>
            </Grid.Col>
            
            {/* 詳細情報（右側） */}
            <Grid.Col span={{ base: 12, md: 7 }} order={{ base: 2, md: 2 }}>
              <Box py={{ base: 'xs' }} px={{ base: 'xs' }}>
                {/* 本命星情報 */}
                <Card 
                  p={{ base: 'md', sm: 'md' }}
                  radius="md" 
                  style={{
                    background: `linear-gradient(135deg, ${starColor}08, ${starColor}15)`,
                    border: `1px solid ${starColor}25`,
                    boxShadow: `0 4px 12px ${starColor}10`,
                    marginBottom: '0.5rem',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                >
                  <Stack gap="md" style={{ position: 'relative', zIndex: 1 }}>
                    <Group justify="center" align="center" gap="md">
                      <Badge 
                        size="lg" 
                        radius="md"
                        color={starColor} 
                        variant="filled"
                        style={{ 
                          fontSize: '1.8rem',
                          padding: '0.2rem 0.6rem',
                          fontWeight: 700,
                          boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
                          height: '42px',
                          minWidth: '42px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: `linear-gradient(135deg, ${starColor}, ${starColor}e0)`
                        }}
                      >
                        {star.number}
                      </Badge>
                      
                      <Badge 
                        color={elementStyle.color}
                        size="lg"
                        radius="md"
                        variant="outline"
                        style={{ 
                          padding: '0.25rem 0.6rem',
                          fontSize: '1rem',
                          fontWeight: 500,
                          border: `2px solid ${elementStyle.color}40`,
                          background: elementStyle.bgColor,
                          color: '#333'
                        }}
                      >
                        五行：{star.element}
                      </Badge>
                    </Group>
                    
                    <Text 
                      fw={600} 
                      ta="center" 
                      size="lg" 
                      style={{ 
                        color: `${starColor}`,
                        fontSize: '1.3rem',
                        letterSpacing: '0.04em',
                        marginTop: '-4px'
                      }}
                    >
                      {star.name_jp}
                    </Text>
                  </Stack>
                  
                  {/* キーワード */}
                  <Box style={{ position: 'relative', zIndex: 1 }}>
                    <Group gap="xs" mt="sm" style={{ flexWrap: 'wrap', justifyContent: 'center' }}>
                      {starKeywords.map((keyword, index) => (
                        <Badge 
                          key={index} 
                          color={starColor}
                          size="md"
                          radius="sm"
                          variant="light"
                          style={{ 
                            fontSize: '0.75rem',
                            fontWeight: 500,
                            opacity: 0.95,
                            padding: '0.3rem 0.6rem', 
                            margin: '0.15rem 0.1rem',
                            color: '#333'
                          }}
                        >
                          {keyword}
                        </Badge>
                      ))}
                    </Group>
                  </Box>
                </Card>
              </Box>
            </Grid.Col>
          </Grid>
        </Card>
        
        {/* 基本情報・鑑定結果（SVGの下） */}
        <Card 
          shadow="md" 
          p={{ base: 'md', sm: 'lg' }}
          radius={0}
          style={{ 
            background: commonGradient,
            border: 0,
            borderTop: `1px solid ${elementStyle.color}30`,
            boxShadow: `0 10px 20px -15px ${elementStyle.color}25`,
            position: 'relative',
            overflow: 'hidden',
            width: '100%',
            padding: '20px'
          }}
        >
          <Title order={3} mb="sm" style={{ 
            color: '#2d3748', 
            borderBottom: `2px solid ${elementStyle.color}30`,
            paddingBottom: '10px',
            fontSize: 'clamp(1rem, 2.2vw, 1.2rem)',
            fontWeight: 600,
            letterSpacing: '0.02em',
            position: 'relative',
            zIndex: 1
          }}>
            {getInfoSectionTitle()}
            {star.title ? `（${star.title}）` : ''}
          </Title>
          
          <Text 
            size="sm" 
            className="paragraph-text"
            style={{ 
              whiteSpace: 'pre-wrap',
              lineHeight: '1.8',
              color: '#2d3748',
              fontSize: 'clamp(0.9rem, 1.8vw, 1rem)',
              position: 'relative',
              zIndex: 1
            }}
          >
            {star.description}
          </Text>
          
          {/* アドバイスがある場合のみ表示 */}
          {star.advice && (
            <>
              <Divider my="lg" />
              <Text fw={600} mb="sm" style={{ color: '#4a5568' }}>アドバイス</Text>
              <Text 
                size="sm"
                className="paragraph-text"
                style={{ 
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.8',
                  color: '#2d3748',
                  fontSize: 'clamp(0.9rem, 1.8vw, 1rem)',
                  position: 'relative',
                  zIndex: 1
                }}
              >
                {star.advice}
              </Text>
            </>
          )}
        </Card>
      </Box>
    </Paper>
  );
};

export default MainStarWithInfo; 