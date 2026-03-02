'use client';

import React, { useState } from 'react';
import '../styles/KyuseiBoard_Authentic.css';

interface Star {
  name: string;
  element: string;
  angle: number;
}

interface StarConfiguration {
  center: { name: string; element: string };
  positions: Star[];
}

// 固定の方位と干支データ（九星に関係なく不変）
const FIXED_DIRECTIONS = [
  { direction: "北東", zodiac: "寅・丑", angle: 45 },
  { direction: "東", zodiac: "卯", angle: 90 },
  { direction: "南東", zodiac: "辰・巳", angle: 135 },
  { direction: "南", zodiac: "午", angle: 180 },
  { direction: "南西", zodiac: "未・申", angle: 225 },
  { direction: "西", zodiac: "酉", angle: 270 },
  { direction: "北西", zodiac: "亥・戌", angle: 315 },
  { direction: "北", zodiac: "子", angle: 0 }
];

interface KyuseiBoardAuthenticProps {
  centerStar?: string;
  size?: number;
  interactive?: boolean;
  theme?: 'luxury' | 'minimal' | 'classic';
  glowEffect?: boolean;
  backgroundGradient?: 'classic' | 'blue-yellow' | 'purple-pink' | 'green-lime' | 'orange-red' | 'gray-white' | 'dark-purple';
  compact?: boolean; // 鑑定結果用のコンパクトモード
}

const KyuseiBoard_Authentic: React.FC<KyuseiBoardAuthenticProps> = ({ 
  centerStar = "一白水星", 
  size = 600, 
  interactive = true,
  theme = "luxury",
  glowEffect = false,
  backgroundGradient = "classic",
  compact = false
}) => {
  const [hoveredStar, setHoveredStar] = useState<number | null>(null);

  // 九星ごとの正確な配置データ（SQLファイルの実際のデータに基づく）
  const starConfigurations: Record<string, StarConfiguration> = {
    "一白水星": {
      center: { name: "一白水星", element: "水" },
      positions: [
        { name: "四緑木星", element: "木", angle: 45 },    // 北東
        { name: "八白土星", element: "土", angle: 90 },    // 東
        { name: "九紫火星", element: "火", angle: 135 },   // 南東
        { name: "五黄土星", element: "土", angle: 180 },   // 南
        { name: "七赤金星", element: "金", angle: 225 },   // 南西
        { name: "三碧木星", element: "木", angle: 270 },   // 西
        { name: "二黒土星", element: "土", angle: 315 },   // 北西
        { name: "六白金星", element: "金", angle: 0 }      // 北
      ]
    },
    "二黒土星": {
      center: { name: "二黒土星", element: "土" },
      positions: [
        { name: "五黄土星", element: "土", angle: 45 },    // 北東
        { name: "九紫火星", element: "火", angle: 90 },    // 東
        { name: "一白水星", element: "水", angle: 135 },   // 南東
        { name: "六白金星", element: "金", angle: 180 },   // 南
        { name: "八白土星", element: "土", angle: 225 },   // 南西
        { name: "四緑木星", element: "木", angle: 270 },   // 西
        { name: "三碧木星", element: "木", angle: 315 },   // 北西
        { name: "七赤金星", element: "金", angle: 0 }      // 北
      ]
    },
    "三碧木星": {
      center: { name: "三碧木星", element: "木" },
      positions: [
        { name: "六白金星", element: "金", angle: 45 },    // 北東
        { name: "一白水星", element: "水", angle: 90 },    // 東
        { name: "二黒土星", element: "土", angle: 135 },   // 南東
        { name: "七赤金星", element: "金", angle: 180 },   // 南
        { name: "九紫火星", element: "火", angle: 225 },   // 南西
        { name: "五黄土星", element: "土", angle: 270 },   // 西
        { name: "四緑木星", element: "木", angle: 315 },   // 北西
        { name: "八白土星", element: "土", angle: 0 }      // 北
      ]
    },
    "四緑木星": {
      center: { name: "四緑木星", element: "木" },
      positions: [
        { name: "七赤金星", element: "金", angle: 45 },    // 北東
        { name: "二黒土星", element: "土", angle: 90 },    // 東
        { name: "三碧木星", element: "木", angle: 135 },   // 南東
        { name: "八白土星", element: "土", angle: 180 },   // 南
        { name: "一白水星", element: "水", angle: 225 },   // 南西
        { name: "六白金星", element: "金", angle: 270 },   // 西
        { name: "五黄土星", element: "土", angle: 315 },   // 北西
        { name: "九紫火星", element: "火", angle: 0 }      // 北
      ]
    },
    "五黄土星": {
      center: { name: "五黄土星", element: "土" },
      positions: [
        { name: "八白土星", element: "土", angle: 45 },    // 北東
        { name: "三碧木星", element: "木", angle: 90 },    // 東
        { name: "四緑木星", element: "木", angle: 135 },   // 南東
        { name: "九紫火星", element: "火", angle: 180 },   // 南
        { name: "二黒土星", element: "土", angle: 225 },   // 南西
        { name: "七赤金星", element: "金", angle: 270 },   // 西
        { name: "六白金星", element: "金", angle: 315 },   // 北西
        { name: "一白水星", element: "水", angle: 0 }      // 北
      ]
    },
    "六白金星": {
      center: { name: "六白金星", element: "金" },
      positions: [
        { name: "九紫火星", element: "火", angle: 45 },    // 北東
        { name: "四緑木星", element: "木", angle: 90 },    // 東
        { name: "五黄土星", element: "土", angle: 135 },   // 南東
        { name: "一白水星", element: "水", angle: 180 },   // 南
        { name: "三碧木星", element: "木", angle: 225 },   // 南西
        { name: "八白土星", element: "土", angle: 270 },   // 西
        { name: "七赤金星", element: "金", angle: 315 },   // 北西
        { name: "二黒土星", element: "土", angle: 0 }      // 北
      ]
    },
    "七赤金星": {
      center: { name: "七赤金星", element: "金" },
      positions: [
        { name: "一白水星", element: "水", angle: 45 },    // 北東
        { name: "五黄土星", element: "土", angle: 90 },    // 東
        { name: "六白金星", element: "金", angle: 135 },   // 南東
        { name: "二黒土星", element: "土", angle: 180 },   // 南
        { name: "四緑木星", element: "木", angle: 225 },   // 南西
        { name: "九紫火星", element: "火", angle: 270 },   // 西
        { name: "八白土星", element: "土", angle: 315 },   // 北西
        { name: "三碧木星", element: "木", angle: 0 }      // 北
      ]
    },
    "八白土星": {
      center: { name: "八白土星", element: "土" },
      positions: [
        { name: "二黒土星", element: "土", angle: 45 },    // 北東
        { name: "六白金星", element: "金", angle: 90 },    // 東
        { name: "七赤金星", element: "金", angle: 135 },   // 南東
        { name: "三碧木星", element: "木", angle: 180 },   // 南
        { name: "五黄土星", element: "土", angle: 225 },   // 南西
        { name: "一白水星", element: "水", angle: 270 },   // 西
        { name: "九紫火星", element: "火", angle: 315 },   // 北西
        { name: "四緑木星", element: "木", angle: 0 }      // 北
      ]
    },
    "九紫火星": {
      center: { name: "九紫火星", element: "火" },
      positions: [
        { name: "三碧木星", element: "木", angle: 45 },    // 北東
        { name: "七赤金星", element: "金", angle: 90 },    // 東
        { name: "八白土星", element: "土", angle: 135 },   // 南東
        { name: "四緑木星", element: "木", angle: 180 },   // 南
        { name: "六白金星", element: "金", angle: 225 },   // 南西
        { name: "二黒土星", element: "土", angle: 270 },   // 西
        { name: "一白水星", element: "水", angle: 315 },   // 北西
        { name: "五黄土星", element: "土", angle: 0 }      // 北
      ]
    }
  };

  const currentData = starConfigurations[centerStar] || starConfigurations["一白水星"];

  // 五行カラーマッピング
  const elementColors: Record<string, string> = {
    木: "#22C55E", // 緑
    火: "#EF4444", // 赤
    土: "#F59E0B", // 黄
    金: "#D4AF37", // 金
    水: "#3B82F6"  // 青
  };

  const handleStarClick = (star: Star, directionInfo: { direction: string; zodiac: string }) => {
    if (interactive) {
      console.log(`Clicked: ${star.name}`, { 
        star, 
        direction: directionInfo.direction, 
        zodiac: directionInfo.zodiac 
      });
    }
  };

  const getElementColor = (element: string): string => {
    return elementColors[element] || '#D4AF37';
  };

  // 背景グラデーションパターンの定義
  const backgroundGradients: Record<string, string> = {
    'classic': 'linear-gradient(135deg, #0F0F23, #1A1A3E, #2D1B69)',
    'blue-yellow': 'radial-gradient(circle at 30% 20%, rgba(224, 242, 254, 0.6) 0%, rgba(191, 219, 254, 0.4) 50%, rgba(147, 197, 253, 0.3) 100%)', // 薄い水色グラデーション
    'purple-pink': 'radial-gradient(circle at 30% 20%, rgba(243, 232, 255, 0.6) 0%, rgba(233, 213, 255, 0.4) 50%, rgba(221, 214, 254, 0.3) 100%)', // 薄い紫色グラデーション
    'green-lime': 'radial-gradient(circle at 30% 20%, rgba(220, 252, 231, 0.6) 0%, rgba(187, 247, 208, 0.4) 50%, rgba(167, 243, 208, 0.3) 100%)', // 薄い緑色グラデーション
    'orange-red': 'radial-gradient(circle at 30% 20%, rgba(254, 240, 138, 0.6) 0%, rgba(253, 224, 71, 0.4) 50%, rgba(251, 191, 36, 0.3) 100%)', // 薄い黄色グラデーション
    'gray-white': 'radial-gradient(circle at 30% 20%, rgba(249, 250, 251, 0.8) 0%, rgba(243, 244, 246, 0.6) 50%, rgba(229, 231, 235, 0.4) 100%)', // 薄いグレーグラデーション
    'dark-purple': 'radial-gradient(circle at 30% 20%, rgba(135, 206, 250, 0.8) 0%, rgba(147, 197, 253, 0.6) 50%, rgba(191, 219, 254, 0.4) 100%)' // 鮮明な青空色グラデーション
  };

  // 方位角度の計算（九星気学の正しい方位：東西が逆、反時計回り、0度が上（北）から開始）
  const calculatePosition = (angle: number, radius: number): { x: number; y: number } => {
    // 九星気学では東西が逆で反時計回り、0度は上（北）
    const radian = ((angle + 90) * Math.PI) / 180; // 九星気学の正しい方位計算
    const x = Math.cos(radian) * radius; // 九星気学では東が左、西が右
    const y = Math.sin(radian) * radius;
    return { x, y };
  };

  // 読みやすい回転角度を計算（逆さまにならないように調整）
  const getReadableRotation = (angle: number): number => {
    // 90度を超える角度は180度回転させて読みやすくする
    if (angle > 90 && angle <= 270) {
      return angle + 180;
    }
    return angle;
  };

  return (
    <div 
      className={`kyusei-authentic-container ${theme} ${glowEffect ? 'glow-enabled' : ''} ${compact ? 'compact-mode' : ''} bg-${backgroundGradient}`}
      style={{ 
        width: size, 
        height: size,
        '--board-size': `${size}px`,
        ...(backgroundGradient !== 'classic' && { background: backgroundGradients[backgroundGradient] || backgroundGradients['classic'] })
      } as React.CSSProperties}
      data-glow-effect={glowEffect} // デバッグ用
    >
      <div className="kyusei-board-authentic">
        <div className="glow-effect"></div>
        
        {/* 九星気学の正確な方位線（東西南北30°、その他60°の境界） */}
        <div className="compass-lines-authentic">
          {/* 九星気学の方位境界線（東西が逆） */}
          <div className="compass-line-main north-east-boundary" style={{ transform: 'translate(-50%, 0) rotate(-15deg)' }}></div>
          <div className="compass-line-main north-west-boundary" style={{ transform: 'translate(-50%, 0) rotate(15deg)' }}></div>
          <div className="compass-line-main east-north-boundary" style={{ transform: 'translate(-50%, 0) rotate(-75deg)' }}></div>
          <div className="compass-line-main east-south-boundary" style={{ transform: 'translate(-50%, 0) rotate(-105deg)' }}></div>
          <div className="compass-line-main south-east-boundary" style={{ transform: 'translate(-50%, 0) rotate(-165deg)' }}></div>
          <div className="compass-line-main south-west-boundary" style={{ transform: 'translate(-50%, 0) rotate(-195deg)' }}></div>
          <div className="compass-line-main west-south-boundary" style={{ transform: 'translate(-50%, 0) rotate(-255deg)' }}></div>
          <div className="compass-line-main west-north-boundary" style={{ transform: 'translate(-50%, 0) rotate(-285deg)' }}></div>
        </div>
        
        <div className="direction-ring-authentic"></div>
        
        {/* 中央の星 */}
        <div 
          className="center-star-authentic"
          style={{
            background: `linear-gradient(135deg, ${getElementColor(currentData.center.element)}, #FFA500)`
          }}
          onClick={() => console.log('Center star clicked:', currentData.center)}
        >
          <div className="star-name-center">
            {currentData.center.name}
          </div>
        </div>
        
        {/* 八方位の星（正確な九星気学配置） */}
        {currentData.positions.map((star, index) => {
          const radius = size * 0.35; // 半径を0.32から0.35に増加
          const position = calculatePosition(star.angle, radius);
          const directionInfo = FIXED_DIRECTIONS[index]; // 固定の方位・干支情報を取得
          const readableAngle = getReadableRotation(star.angle);
          
          return (
            <div
              key={index}
              className={`star-element-authentic ${hoveredStar === index ? 'hovered' : ''} ${glowEffect ? 'force-glow' : ''}`}
              onMouseEnter={() => interactive && setHoveredStar(index)}
              onMouseLeave={() => interactive && setHoveredStar(null)}
              onClick={() => handleStarClick(star, directionInfo)}
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                transform: `translate(${position.x - (size * 0.0625)}px, ${position.y - (size * 0.05)}px) rotate(${readableAngle}deg)`,
                borderColor: getElementColor(star.element),
                '--element-color': getElementColor(star.element)
              } as React.CSSProperties}
            >
              <div 
                className="star-name" 
                data-angle={star.angle}
              >
                {star.name}
              </div>
            </div>
          );
        })}
        
        {/* 干支ラベル（中心寄りに配置） */}
        <div className="zodiac-labels">
          {currentData.positions.map((star, index) => {
            const radius = size * 0.25;
            const position = calculatePosition(star.angle, radius);
            const directionInfo = FIXED_DIRECTIONS[index];
            const readableAngle = getReadableRotation(star.angle);
            
            return (
              <div
                key={`zodiac-${index}`}
                className="zodiac-label"
                data-angle={star.angle}
                style={{
                  position: 'absolute',
                  left: '50%',
                  top: '50%',
                  transform: `translate(${position.x - (size * 0.025)}px, ${position.y - (size * 0.017)}px) rotate(${readableAngle}deg)`,
                }}
              >
                {directionInfo.zodiac}
              </div>
            );
          })}
        </div>

        {/* 外側の方位ラベル */}
        <div className="outer-direction-labels">
          {currentData.positions.map((star, index) => {
            const radius = size * 0.17;
            const position = calculatePosition(star.angle, radius);
            const directionInfo = FIXED_DIRECTIONS[index];
            const readableAngle = getReadableRotation(star.angle);
            
            return (
              <div
                key={`direction-${index}`}
                className="outer-direction-label"
                data-angle={star.angle}
                style={{
                  position: 'absolute',
                  left: '50%',
                  top: '50%',
                  transform: `translate(${position.x - (size * 0.025)}px, ${position.y - (size * 0.017)}px) rotate(${readableAngle}deg)`,
                }}
              >
                {directionInfo.direction}
              </div>
            );
          })}
        </div>

      </div>

      {/* SVG保存ボタンを削除 */}
      
      {/* 星の詳細情報 */}
    </div>
  );
};

// SVG生成関数をexport
export const generateKyuseiBoardSVG = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  // 九星ごとの正確な配置データ（完全版）
  const starConfigurations: Record<string, StarConfiguration> = {
    "一白水星": {
      center: { name: "一白水星", element: "水" },
      positions: [
        { name: "四緑木星", element: "木", angle: 45 },    // 北東
        { name: "八白土星", element: "土", angle: 90 },    // 東
        { name: "九紫火星", element: "火", angle: 135 },   // 南東
        { name: "五黄土星", element: "土", angle: 180 },   // 南
        { name: "七赤金星", element: "金", angle: 225 },   // 南西
        { name: "三碧木星", element: "木", angle: 270 },   // 西
        { name: "二黒土星", element: "土", angle: 315 },   // 北西
        { name: "六白金星", element: "金", angle: 0 }      // 北
      ]
    },
    "二黒土星": {
      center: { name: "二黒土星", element: "土" },
      positions: [
        { name: "五黄土星", element: "土", angle: 45 },    // 北東
        { name: "九紫火星", element: "火", angle: 90 },    // 東
        { name: "一白水星", element: "水", angle: 135 },   // 南東
        { name: "六白金星", element: "金", angle: 180 },   // 南
        { name: "八白土星", element: "土", angle: 225 },   // 南西
        { name: "四緑木星", element: "木", angle: 270 },   // 西
        { name: "三碧木星", element: "木", angle: 315 },   // 北西
        { name: "七赤金星", element: "金", angle: 0 }      // 北
      ]
    },
    "三碧木星": {
      center: { name: "三碧木星", element: "木" },
      positions: [
        { name: "六白金星", element: "金", angle: 45 },    // 北東
        { name: "一白水星", element: "水", angle: 90 },    // 東
        { name: "二黒土星", element: "土", angle: 135 },   // 南東
        { name: "七赤金星", element: "金", angle: 180 },   // 南
        { name: "九紫火星", element: "火", angle: 225 },   // 南西
        { name: "五黄土星", element: "土", angle: 270 },   // 西
        { name: "四緑木星", element: "木", angle: 315 },   // 北西
        { name: "八白土星", element: "土", angle: 0 }      // 北
      ]
    },
    "四緑木星": {
      center: { name: "四緑木星", element: "木" },
      positions: [
        { name: "七赤金星", element: "金", angle: 45 },    // 北東
        { name: "二黒土星", element: "土", angle: 90 },    // 東
        { name: "三碧木星", element: "木", angle: 135 },   // 南東
        { name: "八白土星", element: "土", angle: 180 },   // 南
        { name: "一白水星", element: "水", angle: 225 },   // 南西
        { name: "六白金星", element: "金", angle: 270 },   // 西
        { name: "五黄土星", element: "土", angle: 315 },   // 北西
        { name: "九紫火星", element: "火", angle: 0 }      // 北
      ]
    },
    "五黄土星": {
      center: { name: "五黄土星", element: "土" },
      positions: [
        { name: "八白土星", element: "土", angle: 45 },    // 北東
        { name: "三碧木星", element: "木", angle: 90 },    // 東
        { name: "四緑木星", element: "木", angle: 135 },   // 南東
        { name: "九紫火星", element: "火", angle: 180 },   // 南
        { name: "二黒土星", element: "土", angle: 225 },   // 南西
        { name: "七赤金星", element: "金", angle: 270 },   // 西
        { name: "六白金星", element: "金", angle: 315 },   // 北西
        { name: "一白水星", element: "水", angle: 0 }      // 北
      ]
    },
    "六白金星": {
      center: { name: "六白金星", element: "金" },
      positions: [
        { name: "九紫火星", element: "火", angle: 45 },    // 北東
        { name: "四緑木星", element: "木", angle: 90 },    // 東
        { name: "五黄土星", element: "土", angle: 135 },   // 南東
        { name: "一白水星", element: "水", angle: 180 },   // 南
        { name: "三碧木星", element: "木", angle: 225 },   // 南西
        { name: "八白土星", element: "土", angle: 270 },   // 西
        { name: "七赤金星", element: "金", angle: 315 },   // 北西
        { name: "二黒土星", element: "土", angle: 0 }      // 北
      ]
    },
    "七赤金星": {
      center: { name: "七赤金星", element: "金" },
      positions: [
        { name: "一白水星", element: "水", angle: 45 },    // 北東
        { name: "五黄土星", element: "土", angle: 90 },    // 東
        { name: "六白金星", element: "金", angle: 135 },   // 南東
        { name: "二黒土星", element: "土", angle: 180 },   // 南
        { name: "四緑木星", element: "木", angle: 225 },   // 南西
        { name: "九紫火星", element: "火", angle: 270 },   // 西
        { name: "八白土星", element: "土", angle: 315 },   // 北西
        { name: "三碧木星", element: "木", angle: 0 }      // 北
      ]
    },
    "八白土星": {
      center: { name: "八白土星", element: "土" },
      positions: [
        { name: "二黒土星", element: "土", angle: 45 },    // 北東
        { name: "六白金星", element: "金", angle: 90 },    // 東
        { name: "七赤金星", element: "金", angle: 135 },   // 南東
        { name: "三碧木星", element: "木", angle: 180 },   // 南
        { name: "五黄土星", element: "土", angle: 225 },   // 南西
        { name: "一白水星", element: "水", angle: 270 },   // 西
        { name: "九紫火星", element: "火", angle: 315 },   // 北西
        { name: "四緑木星", element: "木", angle: 0 }      // 北
      ]
    },
    "九紫火星": {
      center: { name: "九紫火星", element: "火" },
      positions: [
        { name: "三碧木星", element: "木", angle: 45 },    // 北東
        { name: "七赤金星", element: "金", angle: 90 },    // 東
        { name: "八白土星", element: "土", angle: 135 },   // 南東
        { name: "四緑木星", element: "木", angle: 180 },   // 南
        { name: "六白金星", element: "金", angle: 225 },   // 南西
        { name: "二黒土星", element: "土", angle: 270 },   // 西
        { name: "一白水星", element: "水", angle: 315 },   // 北西
        { name: "五黄土星", element: "土", angle: 0 }      // 北
      ]
    }
  };

  const FIXED_DIRECTIONS = [
    { direction: "北東", zodiac: "寅・丑", angle: 45 },
    { direction: "東", zodiac: "卯", angle: 90 },
    { direction: "南東", zodiac: "辰・巳", angle: 135 },
    { direction: "南", zodiac: "午", angle: 180 },
    { direction: "南西", zodiac: "未・申", angle: 225 },
    { direction: "西", zodiac: "酉", angle: 270 },
    { direction: "北西", zodiac: "亥・戌", angle: 315 },
    { direction: "北", zodiac: "子", angle: 0 }
  ];

  const elementColors: Record<string, string> = {
    木: "#22C55E",
    火: "#EF4444", 
    土: "#F59E0B",
    金: "#D4AF37",
    水: "#3B82F6"
  };

  const getElementColor = (element: string): string => {
    return elementColors[element] || '#D4AF37';
  };

  const calculatePosition = (angle: number, radius: number): { x: number; y: number } => {
    // 九星気学では東西が逆で反時計回り、0度は上（北）
    const radian = ((angle + 90) * Math.PI) / 180; // 九星気学の正しい方位計算
    const x = Math.cos(radian) * radius; // 九星気学では東が左、西が右
    const y = Math.sin(radian) * radius;
    return { x, y };
  };

  // 読みやすい回転角度を計算（React版と同じロジック）
  const getReadableRotation = (angle: number): number => {
    if (angle > 90 && angle <= 270) {
      return angle + 180;
    }
    return angle;
  };

  const currentData = starConfigurations[centerStar] || starConfigurations["一白水星"];
  const svgSize = size;
  const centerX = svgSize / 2;
  const centerY = svgSize / 2;

  // React画面のエフェクトを再現するSVG
  const svgContent = `
    <svg width="${svgSize}" height="${svgSize}" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Noto Sans JP', 'Inter', sans-serif;">
      <defs>
        <!-- 🎨 React背景の美しいラジアルグラデーション再現 -->
        <radialGradient id="luxuryBackground" cx="50%" cy="50%" r="80%">
          <stop offset="0%" style="stop-color:#4a4fb8;stop-opacity:0.9"/>
          <stop offset="25%" style="stop-color:#343481;stop-opacity:0.85"/>
          <stop offset="60%" style="stop-color:#24245f;stop-opacity:0.9"/>
          <stop offset="100%" style="stop-color:#0F0F23;stop-opacity:1"/>
        </radialGradient>
        
        <!-- 🌟 中央星の立体的グラデーション -->
        <radialGradient id="centerStarGradient" cx="30%" cy="30%" r="80%">
          <stop offset="0%" style="stop-color:${getElementColor(currentData.center.element)};stop-opacity:1"/>
          <stop offset="40%" style="stop-color:${getElementColor(currentData.center.element)};stop-opacity:0.8"/>
          <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:0.7"/>
        </radialGradient>
        
        <!-- ✨ 光るボーダーエフェクト -->
        <linearGradient id="glowBorder" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:rgba(135,206,250,0.6);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(212,175,55,0.8);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:rgba(135,206,250,0.6);stop-opacity:1"/>
        </linearGradient>
        
        <!-- 🔆 星のホバーエフェクト用グラデーション -->
        <radialGradient id="starHoverGlow" cx="50%" cy="50%" r="60%">
          <stop offset="0%" style="stop-color:rgba(135,206,250,0.3);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(135,206,250,0.2);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:rgba(135,206,250,0.1);stop-opacity:1"/>
        </radialGradient>
        
        <!-- 🌠 各九星のカラフルグラデーション -->
        ${Object.entries(elementColors).map(([element, color]) => `
        <radialGradient id="elementGradient${element}" cx="30%" cy="30%" r="70%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:0.9"/>
          <stop offset="60%" style="stop-color:${color};stop-opacity:0.6"/>
          <stop offset="100%" style="stop-color:rgba(45,27,105,0.4);stop-opacity:1"/>
        </radialGradient>`).join('')}
        
        <!-- 💎 ドロップシャドウ効果 -->
        <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(135,206,250,0.4)"/>
        </filter>
        
        <!-- ⚡ 光の境界線フィルター -->
        <filter id="lightBorder" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
          <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.53  0 0 0 0 0.81  0 0 0 0 0.98  0 0 0 1 0"/>
          <feMerge>
            <feMergeNode in="SourceGraphic"/>
            <feMergeNode in="blur"/>
          </feMerge>
        </filter>
        
        <!-- 🌟 光の境界線用グラデーション -->
        <linearGradient id="boundaryLightGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
          <stop offset="10%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="30%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(212,175,55,0.8);stop-opacity:1"/>
          <stop offset="70%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="90%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- 🔆 光の外側エフェクト用グラデーション -->
        <linearGradient id="outerGlowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
          <stop offset="20%" style="stop-color:rgba(135,206,250,0.05);stop-opacity:1"/>
          <stop offset="40%" style="stop-color:rgba(135,206,250,0.15);stop-opacity:1"/>
          <stop offset="60%" style="stop-color:rgba(135,206,250,0.15);stop-opacity:1"/>
          <stop offset="80%" style="stop-color:rgba(135,206,250,0.05);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- ✨ 光るエフェクト用フィルター -->
        <filter id="glowingLine" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <!-- 🎯 メイン背景円 (React版のbackdrop-filter効果を再現) -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.45}" 
              fill="url(#luxuryBackground)" 
              stroke="url(#glowBorder)" 
              stroke-width="2"
              filter="url(#lightBorder)"
              opacity="0.95"/>
      
      <!-- 💫 インナーリング (React版の方位リング) -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.35}" 
              fill="none" 
              stroke="rgba(212,175,55,0.4)" 
              stroke-width="1.5"
              opacity="0.7"/>
              
      <!-- 🔘 ミドルリング (方位と干支の間) -->
      <circle cx="${centerX}" cy="${centerY}" r="${size * 0.21}" 
              fill="none" 
              stroke="rgba(212,175,55,0.3)" 
              stroke-width="1"
              opacity="0.6"/>
              
      <!-- 🌈 光る方位境界線 (九星気学の正しい方位：東西南北30度、その他60度) -->
      ${[15, 75, 105, 165, 195, 255, 285, 345].map(angle => {
        const endRadius = svgSize * 0.45;
        const startRadius = svgSize * 0.08;
        const radian = (angle * Math.PI) / 180;
        const startX = centerX + Math.cos(radian) * startRadius;
        const startY = centerY + Math.sin(radian) * startRadius;
        const endX = centerX + Math.cos(radian) * endRadius;
        const endY = centerY + Math.sin(radian) * endRadius;
        
        return `
        <!-- 外側の薄い光 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="url(#outerGlowGradient)" 
              stroke-width="2" 
              opacity="0.4"
              filter="url(#glowingLine)"/>
              
        <!-- メインの光の線 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="url(#boundaryLightGradient)" 
              stroke-width="1" 
              opacity="0.6"
              filter="url(#glowingLine)"/>
              
        <!-- 中心の鋭い光 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="rgba(212,175,55,0.7)" 
              stroke-width="0.3" 
              opacity="0.8"/>`;
      }).join('')}

      <!-- ⭐ 中央星 (React版の立体効果を再現) -->
      <circle cx="${centerX}" cy="${centerY}" r="${size * 0.08}" 
              fill="url(#centerStarGradient)" 
              stroke="rgba(255,255,255,0.3)" 
              stroke-width="2"
              filter="url(#dropShadow)"/>
      
      <!-- 📝 中央星のテキスト -->
      <text x="${centerX}" y="${centerY}" 
            text-anchor="middle" 
            dominant-baseline="middle" 
            font-size="${size * 0.0276}" 
            font-weight="700" 
            fill="#1A1A3E"
            font-family="Arial, sans-serif">
        ${currentData.center.name}
      </text>

             <!-- 🎪 八方位の星 (React版の美しいエフェクト付き) -->
       ${currentData.positions.map((star) => {
                 const radius = size * 0.35;
         const position = calculatePosition(star.angle, radius);
         const starX = centerX + position.x;
         const starY = centerY + position.y;
         const readableAngle = getReadableRotation(star.angle);
        
        // 星の背景矩形
        const rectWidth = size * 0.14;
        const rectHeight = size * 0.1;
        
        // 東西方向（90度、270度）のみ縦書きにする
        const isEastWest = star.angle === 90 || star.angle === 270;
        
        return `
        <!-- 星のグループ (ボックスとテキストを一緒に回転) -->
        <g transform="translate(${starX}, ${starY}) rotate(${readableAngle})">
          <!-- 星の背景 (React版のblur効果を再現) -->
          <rect x="${-rectWidth/2}" y="${-rectHeight/2}" 
                width="${rectWidth}" height="${rectHeight}" 
                rx="${size * 0.02}" 
                fill="url(#elementGradient${star.element})"
                stroke="url(#glowBorder)" 
                stroke-width="1"
                filter="url(#dropShadow)"
                opacity="0.9"/>
                
          <!-- 星名テキスト -->
          ${isEastWest ? `
          <!-- 縦書きテキスト（東西のみ、回転を打ち消して常に上から下に読める） -->
          <g transform="rotate(${-readableAngle})">
            <text text-anchor="middle" 
                  font-size="${size * 0.0264}" 
                  font-weight="600" 
                  fill="#F9FAFB"
                  font-family="Arial, sans-serif">
              ${star.name.split('').map((char, i) => 
                `<tspan x="0" y="${(i - 1.5) * size * 0.04 + size * 0.01}">${char}</tspan>`
              ).join('')}
            </text>
          </g>` : `
          <!-- 横書きテキスト（その他の方向） -->
          <text x="0" y="${-size * 0.01}" 
                text-anchor="middle" 
                dominant-baseline="middle" 
                font-size="${size * 0.0264}" 
                font-weight="600" 
                fill="#F9FAFB"
                font-family="Arial, sans-serif">
            ${star.name}
          </text>`}
        </g>`;
      }).join('')}
      
      <!-- 🧭 方位・干支ラベル -->
      ${currentData.positions.map((star, index) => {
        const directionRadius = size * 0.17;
        const zodiacRadius = size * 0.25;
        const directionPos = calculatePosition(star.angle, directionRadius);
        const zodiacPos = calculatePosition(star.angle, zodiacRadius);
        const directionInfo = FIXED_DIRECTIONS[index];
        const readableAngle = getReadableRotation(star.angle);
        
        // 東西方向（90度、270度）は回転させない
        const shouldRotate = star.angle !== 90 && star.angle !== 270;
        const rotationTransform = shouldRotate ? `transform="rotate(${readableAngle} ${centerX + directionPos.x} ${centerY + directionPos.y})"` : '';
        const zodiacRotationTransform = shouldRotate ? `transform="rotate(${readableAngle} ${centerX + zodiacPos.x} ${centerY + zodiacPos.y})"` : '';
        
        return `
        <!-- 方位ラベル -->
        <text x="${centerX + directionPos.x}" y="${centerY + directionPos.y}" 
              text-anchor="middle" 
              dominant-baseline="middle" 
              font-size="${size * 0.0276}" 
              font-weight="600" 
              fill="#F3F4F6"
              font-family="Arial, sans-serif"
              ${rotationTransform}>
          ${directionInfo.direction}
        </text>
        
        <!-- 干支ラベル -->
        <text x="${centerX + zodiacPos.x}" y="${centerY + zodiacPos.y}" 
              text-anchor="middle" 
              dominant-baseline="middle" 
              font-size="${size * 0.0216}" 
              font-weight="500" 
              fill="#E5E7EB"
              font-family="Arial, sans-serif"
              ${zodiacRotationTransform}>
          ${directionInfo.zodiac}
        </text>`;
      }).join('')}
    </svg>
  `;

  return svgContent;
};

// WeasyPrint Step2: フィルターエフェクトのみ無効化（美しいグラデーション等は保持）
export const generateKyuseiBoardSVG_NoFilters = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  // 基本のSVG生成
  let svgContent = generateKyuseiBoardSVG(centerStar, size);
  
  // フィルターエフェクトのみを無効化（グラデーション、色彩、光エフェクトは保持）
  svgContent = svgContent
    // feDropShadow フィルターを削除
    .replace(/<filter id="dropShadow"[^>]*>[\s\S]*?<\/filter>/g, '')
    // feGaussianBlur関連フィルターを削除
    .replace(/<filter id="lightBorder"[^>]*>[\s\S]*?<\/filter>/g, '')
    .replace(/<filter id="glowingLine"[^>]*>[\s\S]*?<\/filter>/g, '')
    // フィルター参照を削除
    .replace(/filter="url\(#dropShadow\)"/g, '')
    .replace(/filter="url\(#lightBorder\)"/g, '')
    .replace(/filter="url\(#glowingLine\)"/g, '');
    
  return svgContent;
};

// WeasyPrint Step3: ソリッドカラーのみ（グラデーション・フィルター全て除去、レイアウトは保持）
export const generateKyuseiBoardSVG_Solid = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  // 基本のSVG生成
  let svgContent = generateKyuseiBoardSVG(centerStar, size);
  
  // 全ての複雑なエフェクトを除去し、ソリッドカラーに置換
  svgContent = svgContent
    // defs内の全てのグラデーションとフィルターを削除
    .replace(/<defs>[\s\S]*?<\/defs>/g, '')
    // グラデーション参照をソリッドカラーに置換
    .replace(/fill="url\(#luxuryBackground\)"/g, 'fill="#1A1A3E"')
    .replace(/fill="url\(#centerStarGradient\)"/g, 'fill="#2D1B69"') 
    .replace(/fill="url\(#elementGradient水\)"/g, 'fill="#1E40AF"')
    .replace(/fill="url\(#elementGradient木\)"/g, 'fill="#16A34A"')
    .replace(/fill="url\(#elementGradient火\)"/g, 'fill="#DC2626"')
    .replace(/fill="url\(#elementGradient土\)"/g, 'fill="#A16207"')
    .replace(/fill="url\(#elementGradient金\)"/g, 'fill="#6B7280"')
    .replace(/stroke="url\(#glowBorder\)"/g, 'stroke="#D4AF37"')
    .replace(/stroke="url\(#boundaryLightGradient\)"/g, 'stroke="#D4AF37"')
    .replace(/stroke="url\(#outerGlowGradient\)"/g, 'stroke="#87CEEB"')
    // フィルター参照を削除
    .replace(/filter="url\([^"]*\)"/g, '')
    // 複雑なopacity設定を簡素化
    .replace(/opacity="0\.\d+"/g, 'opacity="0.8"');
    
  return svgContent;
};

// WeasyPrint Step4: 美しいグラデーション復活版（フィルターなし、シンプルグラデーション）
export const generateKyuseiBoardSVG_GradientOnly = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  // 基本のSVG生成
  let svgContent = generateKyuseiBoardSVG(centerStar, size);
  
  // フィルターのみ除去し、シンプルなグラデーションは保持
  svgContent = svgContent
    // フィルター定義を削除
    .replace(/<filter id="dropShadow"[^>]*>[\s\S]*?<\/filter>/g, '')
    .replace(/<filter id="lightBorder"[^>]*>[\s\S]*?<\/filter>/g, '')
    .replace(/<filter id="glowingLine"[^>]*>[\s\S]*?<\/filter>/g, '')
    // フィルター参照を削除
    .replace(/filter="url\(#dropShadow\)"/g, '')
    .replace(/filter="url\(#lightBorder\)"/g, '')
    .replace(/filter="url\(#glowingLine\)"/g, '')
    // 複雑なopacity設定を少し簡素化
    .replace(/opacity="0\.95"/g, 'opacity="0.9"')
    .replace(/opacity="0\.9"/g, 'opacity="0.8"');
    
  return svgContent;
};

// WeasyPrint Step5: 美しいストロークエフェクト版（グラデーション・フィルターなし、ストロークで美しさ演出）
export const generateKyuseiBoardSVG_StrokeOnly = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  // 基本のSVG生成
  let svgContent = generateKyuseiBoardSVG(centerStar, size);
  
  // 全ての複雑なエフェクトを除去し、美しいストロークエフェクトで置換
  svgContent = svgContent
    // defs内の全てのグラデーションとフィルターを削除
    .replace(/<defs>[\s\S]*?<\/defs>/g, '')
    // グラデーション参照を美しいソリッドカラー+ストロークに置換
    .replace(/fill="url\(#luxuryBackground\)" stroke="url\(#glowBorder\)" stroke-width="2"/g, 
      'fill="#1A1A3E" stroke="#D4AF37" stroke-width="3"')
    .replace(/fill="url\(#centerStarGradient\)" stroke="rgba\(255,255,255,0\.3\)" stroke-width="2"/g, 
      'fill="#2D1B69" stroke="#FFD700" stroke-width="2"')
    
    // 五行ごとの美しいストロークエフェクト
    .replace(/fill="url\(#elementGradient水\)" stroke="url\(#glowBorder\)" stroke-width="1"/g, 
      'fill="#1E40AF" stroke="#60A5FA" stroke-width="2"')
    .replace(/fill="url\(#elementGradient木\)" stroke="url\(#glowBorder\)" stroke-width="1"/g, 
      'fill="#16A34A" stroke="#4ADE80" stroke-width="2"')  
    .replace(/fill="url\(#elementGradient火\)" stroke="url\(#glowBorder\)" stroke-width="1"/g, 
      'fill="#DC2626" stroke="#F87171" stroke-width="2"')
    .replace(/fill="url\(#elementGradient土\)" stroke="url\(#glowBorder\)" stroke-width="1"/g, 
      'fill="#A16207" stroke="#FBBF24" stroke-width="2"')
    .replace(/fill="url\(#elementGradient金\)" stroke="url\(#glowBorder\)" stroke-width="1"/g, 
      'fill="#6B7280" stroke="#D1D5DB" stroke-width="2"')
    
    // 残りのグラデーション参照を削除
    .replace(/fill="url\([^"]*\)"/g, 'fill="#4A5568"')
    .replace(/stroke="url\([^"]*\)"/g, 'stroke="#D4AF37"')
    
    // フィルター参照を削除
    .replace(/filter="url\([^"]*\)"/g, '')
    
    // opacity を統一
    .replace(/opacity="0\.\d+"/g, 'opacity="0.9"')
    
    // 光る境界線をダブルストロークで表現
    .replace(/stroke="rgba\(212,175,55,0\.7\)" stroke-width="0\.3"/g, 
      'stroke="#D4AF37" stroke-width="1"')
    .replace(/stroke="rgba\(135,206,250,0\.4\)" stroke-width="2"/g, 
      'stroke="#87CEEB" stroke-width="2"');
    
  return svgContent;
};

export const generateKyuseiBoardSVG_Step10 = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  /**
   * Step10: Step1をそのままコピーして、グラデーション領域のみ小さく調整
   * - ベース: Step1の完全コピー
   * - 変更点: グラデーションのr値を70%→50%に縮小
   */
  
  // 九星ごとの正確な配置データ（完全版）
  const starConfigurations: Record<string, StarConfiguration> = {
    "一白水星": {
      center: { name: "一白水星", element: "水" },
      positions: [
        { name: "四緑木星", element: "木", angle: 45 },    // 北東
        { name: "八白土星", element: "土", angle: 90 },    // 東
        { name: "九紫火星", element: "火", angle: 135 },   // 南東
        { name: "五黄土星", element: "土", angle: 180 },   // 南
        { name: "七赤金星", element: "金", angle: 225 },   // 南西
        { name: "三碧木星", element: "木", angle: 270 },   // 西
        { name: "二黒土星", element: "土", angle: 315 },   // 北西
        { name: "六白金星", element: "金", angle: 0 }      // 北
      ]
    },
    "二黒土星": {
      center: { name: "二黒土星", element: "土" },
      positions: [
        { name: "五黄土星", element: "土", angle: 45 },    // 北東
        { name: "九紫火星", element: "火", angle: 90 },    // 東
        { name: "一白水星", element: "水", angle: 135 },   // 南東
        { name: "六白金星", element: "金", angle: 180 },   // 南
        { name: "八白土星", element: "土", angle: 225 },   // 南西
        { name: "四緑木星", element: "木", angle: 270 },   // 西
        { name: "三碧木星", element: "木", angle: 315 },   // 北西
        { name: "七赤金星", element: "金", angle: 0 }      // 北
      ]
    },
    "三碧木星": {
      center: { name: "三碧木星", element: "木" },
      positions: [
        { name: "六白金星", element: "金", angle: 45 },    // 北東
        { name: "一白水星", element: "水", angle: 90 },    // 東
        { name: "二黒土星", element: "土", angle: 135 },   // 南東
        { name: "七赤金星", element: "金", angle: 180 },   // 南
        { name: "九紫火星", element: "火", angle: 225 },   // 南西
        { name: "五黄土星", element: "土", angle: 270 },   // 西
        { name: "四緑木星", element: "木", angle: 315 },   // 北西
        { name: "八白土星", element: "土", angle: 0 }      // 北
      ]
    },
    "四緑木星": {
      center: { name: "四緑木星", element: "木" },
      positions: [
        { name: "七赤金星", element: "金", angle: 45 },    // 北東
        { name: "二黒土星", element: "土", angle: 90 },    // 東
        { name: "三碧木星", element: "木", angle: 135 },   // 南東
        { name: "八白土星", element: "土", angle: 180 },   // 南
        { name: "一白水星", element: "水", angle: 225 },   // 南西
        { name: "六白金星", element: "金", angle: 270 },   // 西
        { name: "五黄土星", element: "土", angle: 315 },   // 北西
        { name: "九紫火星", element: "火", angle: 0 }      // 北
      ]
    },
    "五黄土星": {
      center: { name: "五黄土星", element: "土" },
      positions: [
        { name: "八白土星", element: "土", angle: 45 },    // 北東
        { name: "三碧木星", element: "木", angle: 90 },    // 東
        { name: "四緑木星", element: "木", angle: 135 },   // 南東
        { name: "九紫火星", element: "火", angle: 180 },   // 南
        { name: "二黒土星", element: "土", angle: 225 },   // 南西
        { name: "七赤金星", element: "金", angle: 270 },   // 西
        { name: "六白金星", element: "金", angle: 315 },   // 北西
        { name: "一白水星", element: "水", angle: 0 }      // 北
      ]
    },
    "六白金星": {
      center: { name: "六白金星", element: "金" },
      positions: [
        { name: "九紫火星", element: "火", angle: 45 },    // 北東
        { name: "四緑木星", element: "木", angle: 90 },    // 東
        { name: "五黄土星", element: "土", angle: 135 },   // 南東
        { name: "一白水星", element: "水", angle: 180 },   // 南
        { name: "三碧木星", element: "木", angle: 225 },   // 南西
        { name: "八白土星", element: "土", angle: 270 },   // 西
        { name: "七赤金星", element: "金", angle: 315 },   // 北西
        { name: "二黒土星", element: "土", angle: 0 }      // 北
      ]
    },
    "七赤金星": {
      center: { name: "七赤金星", element: "金" },
      positions: [
        { name: "一白水星", element: "水", angle: 45 },    // 北東
        { name: "五黄土星", element: "土", angle: 90 },    // 東
        { name: "六白金星", element: "金", angle: 135 },   // 南東
        { name: "二黒土星", element: "土", angle: 180 },   // 南
        { name: "四緑木星", element: "木", angle: 225 },   // 南西
        { name: "九紫火星", element: "火", angle: 270 },   // 西
        { name: "八白土星", element: "土", angle: 315 },   // 北西
        { name: "三碧木星", element: "木", angle: 0 }      // 北
      ]
    },
    "八白土星": {
      center: { name: "八白土星", element: "土" },
      positions: [
        { name: "二黒土星", element: "土", angle: 45 },    // 北東
        { name: "六白金星", element: "金", angle: 90 },    // 東
        { name: "七赤金星", element: "金", angle: 135 },   // 南東
        { name: "三碧木星", element: "木", angle: 180 },   // 南
        { name: "五黄土星", element: "土", angle: 225 },   // 南西
        { name: "一白水星", element: "水", angle: 270 },   // 西
        { name: "九紫火星", element: "火", angle: 315 },   // 北西
        { name: "四緑木星", element: "木", angle: 0 }      // 北
      ]
    },
    "九紫火星": {
      center: { name: "九紫火星", element: "火" },
      positions: [
        { name: "三碧木星", element: "木", angle: 45 },    // 北東
        { name: "七赤金星", element: "金", angle: 90 },    // 東
        { name: "八白土星", element: "土", angle: 135 },   // 南東
        { name: "四緑木星", element: "木", angle: 180 },   // 南
        { name: "六白金星", element: "金", angle: 225 },   // 南西
        { name: "二黒土星", element: "土", angle: 270 },   // 西
        { name: "一白水星", element: "水", angle: 315 },   // 北西
        { name: "五黄土星", element: "土", angle: 0 }      // 北
      ]
    }
  };

  const FIXED_DIRECTIONS = [
    { direction: "北東", zodiac: "寅・丑", angle: 45 },
    { direction: "東", zodiac: "卯", angle: 90 },
    { direction: "南東", zodiac: "辰・巳", angle: 135 },
    { direction: "南", zodiac: "午", angle: 180 },
    { direction: "南西", zodiac: "未・申", angle: 225 },
    { direction: "西", zodiac: "酉", angle: 270 },
    { direction: "北西", zodiac: "亥・戌", angle: 315 },
    { direction: "北", zodiac: "子", angle: 0 }
  ];

  const elementColors: Record<string, string> = {
    木: "#22C55E",
    火: "#EF4444", 
    土: "#F59E0B",
    金: "#D4AF37",
    水: "#3B82F6"
  };

  const getElementColor = (element: string): string => {
    return elementColors[element] || '#D4AF37';
  };

  const calculatePosition = (angle: number, radius: number): { x: number; y: number } => {
    // 九星気学では東西が逆で反時計回り、0度は上（北）
    const radian = ((angle + 90) * Math.PI) / 180; // 九星気学の正しい方位計算
    const x = Math.cos(radian) * radius; // 九星気学では東が左、西が右
    const y = Math.sin(radian) * radius;
    return { x, y };
  };

  // 読みやすい回転角度を計算（React版と同じロジック）
  const getReadableRotation = (angle: number): number => {
    if (angle > 90 && angle <= 270) {
      return angle + 180;
    }
    return angle;
  };

  const currentData = starConfigurations[centerStar] || starConfigurations["一白水星"];
  const svgSize = size;
  const centerX = svgSize / 2;
  const centerY = svgSize / 2;

  // React画面のエフェクトを再現するSVG (グラデーション範囲のみ調整)
  const svgContent = `
    <svg width="${svgSize}" height="${svgSize}" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Noto Sans JP', 'Inter', sans-serif;">
      <defs>
        <!-- 🎨 React背景の美しいラジアルグラデーション再現 (80%→50%に縮小) -->
        <radialGradient id="luxuryBackground" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#4a4fb8;stop-opacity:0.9"/>
          <stop offset="25%" style="stop-color:#343481;stop-opacity:0.85"/>
          <stop offset="60%" style="stop-color:#24245f;stop-opacity:0.9"/>
          <stop offset="100%" style="stop-color:#0F0F23;stop-opacity:1"/>
        </radialGradient>
        
        <!-- 🌟 中央星の立体的グラデーション (80%→50%に縮小) -->
        <radialGradient id="centerStarGradient" cx="30%" cy="30%" r="50%">
          <stop offset="0%" style="stop-color:${getElementColor(currentData.center.element)};stop-opacity:1"/>
          <stop offset="40%" style="stop-color:${getElementColor(currentData.center.element)};stop-opacity:0.8"/>
          <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:0.7"/>
        </radialGradient>
        
        <!-- ✨ 光るボーダーエフェクト -->
        <linearGradient id="glowBorder" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:rgba(135,206,250,0.6);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(212,175,55,0.8);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:rgba(135,206,250,0.6);stop-opacity:1"/>
        </linearGradient>
        
        <!-- 🔆 星のホバーエフェクト用グラデーション (60%→50%に縮小) -->
        <radialGradient id="starHoverGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:rgba(135,206,250,0.3);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(135,206,250,0.2);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:rgba(135,206,250,0.1);stop-opacity:1"/>
        </radialGradient>
        
        <!-- 🌠 各九星のカラフルグラデーション (70%→50%に縮小) -->
        ${Object.entries(elementColors).map(([element, color]) => `
        <radialGradient id="elementGradient${element}" cx="30%" cy="30%" r="50%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:0.9"/>
          <stop offset="60%" style="stop-color:${color};stop-opacity:0.6"/>
          <stop offset="100%" style="stop-color:rgba(45,27,105,0.4);stop-opacity:1"/>
        </radialGradient>`).join('')}
        
        <!-- 💎 ドロップシャドウ効果 -->
        <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(135,206,250,0.4)"/>
        </filter>
        
        <!-- ⚡ 光の境界線フィルター -->
        <filter id="lightBorder" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
          <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0.53  0 0 0 0 0.81  0 0 0 0 0.98  0 0 0 1 0"/>
          <feMerge>
            <feMergeNode in="SourceGraphic"/>
            <feMergeNode in="blur"/>
          </feMerge>
        </filter>
        
        <!-- 🌟 光の境界線用グラデーション -->
        <linearGradient id="boundaryLightGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
          <stop offset="10%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="30%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="50%" style="stop-color:rgba(212,175,55,0.8);stop-opacity:1"/>
          <stop offset="70%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="90%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- 🔆 光の外側エフェクト用グラデーション -->
        <linearGradient id="outerGlowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
          <stop offset="20%" style="stop-color:rgba(135,206,250,0.05);stop-opacity:1"/>
          <stop offset="40%" style="stop-color:rgba(135,206,250,0.15);stop-opacity:1"/>
          <stop offset="60%" style="stop-color:rgba(135,206,250,0.15);stop-opacity:1"/>
          <stop offset="80%" style="stop-color:rgba(135,206,250,0.05);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- ✨ 光るエフェクト用フィルター -->
        <filter id="glowingLine" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <!-- 🎯 メイン背景円 (React版のbackdrop-filter効果を再現) -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.45}" 
              fill="url(#luxuryBackground)" 
              stroke="url(#glowBorder)" 
              stroke-width="2"
              filter="url(#lightBorder)"
              opacity="0.95"/>
      
      <!-- 💫 インナーリング (React版の方位リング) -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.35}" 
              fill="none" 
              stroke="rgba(212,175,55,0.4)" 
              stroke-width="1.5"
              opacity="0.7"/>
              
      <!-- 🔘 ミドルリング (方位と干支の間) -->
      <circle cx="${centerX}" cy="${centerY}" r="${size * 0.21}" 
              fill="none" 
              stroke="rgba(212,175,55,0.3)" 
              stroke-width="1"
              opacity="0.6"/>
              
      <!-- 🌈 光る方位境界線 (九星気学の正しい方位：東西南北30度、その他60度) -->
      ${[15, 75, 105, 165, 195, 255, 285, 345].map(angle => {
        const endRadius = svgSize * 0.45;
        const startRadius = svgSize * 0.08;
        const radian = (angle * Math.PI) / 180;
        const startX = centerX + Math.cos(radian) * startRadius;
        const startY = centerY + Math.sin(radian) * startRadius;
        const endX = centerX + Math.cos(radian) * endRadius;
        const endY = centerY + Math.sin(radian) * endRadius;
        
        return `
        <!-- 外側の薄い光 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="url(#outerGlowGradient)" 
              stroke-width="2" 
              opacity="0.4"
              filter="url(#glowingLine)"/>
              
        <!-- メインの光の線 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="url(#boundaryLightGradient)" 
              stroke-width="1" 
              opacity="0.6"
              filter="url(#glowingLine)"/>
              
        <!-- 中心の鋭い光 -->
        <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" 
              stroke="rgba(212,175,55,0.7)" 
              stroke-width="0.3" 
              opacity="0.8"/>`;
      }).join('')}

      <!-- ⭐ 中央星 (React版の立体効果を再現) -->
      <circle cx="${centerX}" cy="${centerY}" r="${size * 0.09}" 
              fill="url(#centerStarGradient)" 
              stroke="rgba(255,255,255,0.3)" 
              stroke-width="2"
              filter="url(#dropShadow)"/>
      
      <!-- 📝 中央星のテキスト -->
      <text x="${centerX}" y="${centerY}" 
            text-anchor="middle" 
            dominant-baseline="middle" 
            font-size="${size * 0.0331}" 
            font-weight="700" 
            fill="#1A1A3E"
            font-family="Arial, sans-serif">
        ${currentData.center.name}
      </text>

             <!-- 🎪 八方位の星 (React版の美しいエフェクト付き) -->
       ${currentData.positions.map((star) => {
                 const radius = size * 0.35;
         const position = calculatePosition(star.angle, radius);
         const starX = centerX + position.x;
         const starY = centerY + position.y;
         const readableAngle = getReadableRotation(star.angle);
        
        // 星の背景矩形
        const rectWidth = size * 0.14;
        const rectHeight = size * 0.1;
        
        // 東西方向（90度、270度）のみ縦書きにする
        const isEastWest = star.angle === 90 || star.angle === 270;
        
        return `
        <!-- 星のグループ (ボックスとテキストを一緒に回転) -->
        <g transform="translate(${starX}, ${starY}) rotate(${readableAngle})">
          <!-- 星の背景 (シンプル版・フィルター除去) -->
          <rect x="${-rectWidth/2}" y="${-rectHeight/2}" 
                width="${rectWidth}" height="${rectHeight}" 
                rx="${size * 0.02}" 
                fill="url(#elementGradient${star.element})"
                stroke="rgba(212,175,55,0.6)" 
                stroke-width="1"
                opacity="0.9"/>
                
          <!-- 星名テキスト -->
          ${isEastWest ? `` : `
          <!-- 横書きテキスト（その他の方向） -->
          <text x="0" y="${-size * 0.01}" 
                text-anchor="middle" 
                dominant-baseline="middle" 
                font-size="${size * 0.0317}" 
                font-weight="600" 
                fill="#F9FAFB"
                font-family="Arial, sans-serif">
            ${star.name}
          </text>`}
        </g>`;
      }).join('')}
      
      <!-- 🧭 方位・干支ラベル -->
      ${currentData.positions.map((star, index) => {
        const directionRadius = size * 0.17;
        const zodiacRadius = size * 0.25;
        const directionPos = calculatePosition(star.angle, directionRadius);
        const zodiacPos = calculatePosition(star.angle, zodiacRadius);
        const directionInfo = FIXED_DIRECTIONS[index];
        const readableAngle = getReadableRotation(star.angle);
        
        // 東西方向（90度、270度）は回転させない
        const shouldRotate = star.angle !== 90 && star.angle !== 270;
        const rotationTransform = shouldRotate ? `transform="rotate(${readableAngle} ${centerX + directionPos.x} ${centerY + directionPos.y})"` : '';
        const zodiacRotationTransform = shouldRotate ? `transform="rotate(${readableAngle} ${centerX + zodiacPos.x} ${centerY + zodiacPos.y})"` : '';
        
        return `
        <!-- 方位ラベル -->
        <text x="${centerX + directionPos.x}" y="${centerY + directionPos.y}" 
              text-anchor="middle" 
              dominant-baseline="middle" 
              font-size="${size * 0.0331}" 
              font-weight="600" 
              fill="#F3F4F6"
              font-family="Arial, sans-serif"
              ${rotationTransform}>
          ${directionInfo.direction}
        </text>
        
        <!-- 干支ラベル -->
        <text x="${centerX + zodiacPos.x}" y="${centerY + zodiacPos.y}" 
              text-anchor="middle" 
              dominant-baseline="middle" 
              font-size="${size * 0.0259}" 
              font-weight="500" 
              fill="#E5E7EB"
              font-family="Arial, sans-serif"
              ${zodiacRotationTransform}>
          ${directionInfo.zodiac}
        </text>`;
      }).join('')}
      
      <!-- 🎪 東西の縦書きテキスト（独立配置） -->
      ${currentData.positions.filter(star => star.angle === 90 || star.angle === 270).map((star) => {
        const radius = size * 0.35;
        const position = calculatePosition(star.angle, radius);
        const starX = centerX + position.x;
        const starY = centerY + position.y;
        
        return `
        <!-- ${star.name}の縦書きテキスト（WeasyPrint最適化・シンプル版） -->
        <text x="${starX}" y="${starY - size * 0.06}" 
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="${size * 0.0317}" 
              font-weight="600" 
              fill="#FFFFFF"
              font-family="Arial, sans-serif">${star.name.charAt(0)}</text>
        <text x="${starX}" y="${starY - size * 0.022}" 
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="${size * 0.0317}" 
              font-weight="600" 
              fill="#FFFFFF"
              font-family="Arial, sans-serif">${star.name.charAt(1)}</text>
        <text x="${starX}" y="${starY + size * 0.022}" 
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="${size * 0.0317}" 
              font-weight="600" 
              fill="#FFFFFF"
              font-family="Arial, sans-serif">${star.name.charAt(2)}</text>
        <text x="${starX}" y="${starY + size * 0.06}" 
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="${size * 0.0317}" 
              font-weight="600" 
              fill="#FFFFFF"
              font-family="Arial, sans-serif">${star.name.charAt(3)}</text>`;
      }).join('')}
    </svg>
  `;

  return svgContent;
};

export const generateKyuseiBoardSVG_Step11 = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  /**
   * Step11: Step10 をベースに文字サイズを 15% 拡大した PDF 対応版
   * - 盤面レイアウトは維持し、文字が線やボックスを跨がない範囲で可読性を向上
   */
  const baseSvg = generateKyuseiBoardSVG_Step10(centerStar, size);

  // font-size="XX" を 1.3 倍に置換
  let enlargedSvg = baseSvg.replace(/font-size="([\d\.]+)"/g, (_match, p1) => {
    const newSize = (parseFloat(p1) * 1.3).toFixed(2);
    return `font-size="${newSize}"`;
  });

  // 九星ラベルボックスの幅・高さを 10% 拡大（崩れ防止範囲）
  enlargedSvg = enlargedSvg.replace(/width="([\d\.]+)"/g, (_m, w) => {
    const newW = (parseFloat(w) * 1.1).toFixed(2);
    return `width="${newW}"`;
  });

  // 幅を拡大しつつ、x 座標を −(新幅/2) に補正して中央揃えを維持
  enlargedSvg = enlargedSvg.replace(/<rect ([^>]*?)x="(-?[\d\.]+)"([^>]*?)width="([\d\.]+)"([^>]*?)>/g, (_match, pre, xVal, mid1, widthVal, post) => {
    const oldWidth = parseFloat(widthVal);
    const newWidth = parseFloat((oldWidth * 1.1).toFixed(2));
    const newX = (-newWidth / 2).toFixed(2);
    return `<rect ${pre}x="${newX}"${mid1}width="${newWidth}"${post}>`;
  });

  // 縦書き tspan (x="0") の y を 1.15 倍して行間を広げる
  enlargedSvg = enlargedSvg.replace(/<tspan x="0" y="(-?[\d\.]+)">/g, (_m, yVal) => {
    const newY = (parseFloat(yVal) * 1.15).toFixed(2);
    return `<tspan x="0" y="${newY}">`;
  });

  return enlargedSvg;
};

export default KyuseiBoard_Authentic; 