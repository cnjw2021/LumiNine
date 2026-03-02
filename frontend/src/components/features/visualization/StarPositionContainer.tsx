'use client';

import React from 'react';
import { Title, Paper, Box, Divider, Text } from '@mantine/core';
import Image from 'next/image';

// 星の型定義
interface Star {
  id?: number;
  star_number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  color?: string;
  direction?: string;
}

// 位置情報の型定義
type Position = 'center' | 'north' | 'northeast' | 'east' | 'southeast' | 'south' | 'southwest' | 'west' | 'northwest';

interface StarPositionContainerProps {
  star: Star;
  title: string;
  color?: string;
  position?: Position; // 方位情報
  isMainStar?: boolean; // 本命星かどうか
}

/**
 * 九星のSVG画像と方位情報を表示するコンポーネント
 */
const StarPositionContainer: React.FC<StarPositionContainerProps> = ({ 
  star, 
  title, 
  color = 'black', 
}) => {
  if (!star) return null;

  // SVGファイルのパスを生成
  const svgPath = `/images/main_star/${star.star_number}.svg`;
  
  return (
    <Paper 
      shadow="sm" 
      p="md" 
      withBorder 
      style={{ 
        maxWidth: '270px', 
        margin: '0 auto',
        position: 'relative'
      }}
    >
      
      <Title order={3} mb="sm" ta="center" c={color}>{title}</Title>
      
      {/* SVG画像表示 */}
      <Box mx="auto" style={{ maxWidth: '100%', position: 'relative', aspectRatio: '1/1' }}>
        <Image
          src={svgPath}
          alt={`星：${star.name_jp}`}
          fill
          style={{ objectFit: 'contain', opacity: 0.8 }}
          priority
        />
      </Box>
      
      <Divider my="md" />
      <Text>{star.star_number} {star.name_jp}</Text>
    </Paper>
  );
};

export default StarPositionContainer; 