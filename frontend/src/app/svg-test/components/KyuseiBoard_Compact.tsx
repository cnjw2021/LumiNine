'use client';

import React from 'react';
import KyuseiBoard_Authentic from './KyuseiBoard_Authentic';

interface KyuseiBoardCompactProps {
  centerStar?: string;
  size?: number;
  theme?: 'luxury' | 'minimal' | 'classic';
  backgroundGradient?: 'classic' | 'blue-yellow' | 'purple-pink' | 'green-lime' | 'orange-red' | 'gray-white' | 'dark-purple';
  glowEffect?: boolean;
}

const KyuseiBoard_Compact: React.FC<KyuseiBoardCompactProps> = ({ 
  centerStar = "一白水星", 
  size = 300, // デフォルトサイズを小さく
  theme = "classic",
  backgroundGradient = "classic",
  glowEffect = true // デフォルトで光エフェクトを有効に
}) => {
  return (
    <KyuseiBoard_Authentic
      centerStar={centerStar}
      size={size}
      interactive={false} // 鑑定結果では非インタラクティブ
      theme={theme}
      glowEffect={glowEffect} // プロパティとして渡す
      backgroundGradient={backgroundGradient}
      compact={true} // コンパクトモードを有効
    />
  );
};

export default KyuseiBoard_Compact; 