import React, { useState, useEffect } from 'react';
import '../styles/KyuseiBoard.css';

interface StarData {
  center: { name: string; element: string };
  positions: Array<{
    name: string;
    direction: string;
    zodiac: string;
    element: string;
  }>;
}

interface KyuseiBoardProps {
  starData?: StarData | null;
  size?: number;
  interactive?: boolean;
  theme?: 'luxury' | 'minimal' | 'classic';
}

const KyuseiBoard: React.FC<KyuseiBoardProps> = ({ 
  starData = null, 
  size = 600, 
  interactive = true,
  theme = "luxury"
}) => {
  const [hoveredStar, setHoveredStar] = useState<number | null>(null);
  const [rotation, setRotation] = useState(0);

  // デフォルトの星配置データ
  const defaultStarData: StarData = {
    center: { name: "七赤金星", element: "金" },
    positions: [
      { name: "三碧木星", direction: "北", zodiac: "子", element: "木" },
      { name: "八白土星", direction: "北東", zodiac: "寅・丑", element: "土" },
      { name: "五黄土星", direction: "東", zodiac: "卯", element: "土" },
      { name: "六白金星", direction: "南東", zodiac: "辰・巳", element: "金" },
      { name: "九紫火星", direction: "南", zodiac: "午", element: "火" },
      { name: "二黒土星", direction: "南西", zodiac: "未・申", element: "土" },
      { name: "四緑木星", direction: "西", zodiac: "酉", element: "木" },
      { name: "一白水星", direction: "北西", zodiac: "亥・戌", element: "水" }
    ]
  };

  const currentData = starData || defaultStarData;

  // 五行カラーマッピング
  const elementColors = {
    木: "#22C55E", // 緑
    火: "#EF4444", // 赤
    土: "#F59E0B", // 黄
    金: "#D4AF37", // 金
    水: "#3B82F6"  // 青
  };

  const directionClasses = [
    'north', 'northeast', 'east', 'southeast',
    'south', 'southwest', 'west', 'northwest'
  ];

  useEffect(() => {
    if (interactive) {
      const interval = setInterval(() => {
        setRotation(prev => (prev + 0.1) % 360);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [interactive]);

  const handleStarClick = (star: { name: string; direction: string; zodiac: string; element: string }) => {
    if (interactive) {
      console.log(`Clicked: ${star.name}`, star);
      // ここでコールバック関数を呼び出し可能
    }
  };

  const getElementColor = (element: string) => {
    return elementColors[element as keyof typeof elementColors] || '#D4AF37';
  };

  return (
    <div 
      className={`kyusei-container ${theme}`}
      style={{ width: size, height: size }}
    >
      <h1 className="kyusei-title">九星気学</h1>
      
      <div 
        className="kyusei-board"
        style={{ 
          transform: interactive ? `rotate(${rotation}deg)` : 'none',
          transition: 'transform 0.1s linear'
        }}
      >
        <div className="glow-effect"></div>
        
        <div className="compass-lines">
          <div className="compass-line horizontal"></div>
          <div className="compass-line vertical"></div>
          <div className="compass-line diagonal1"></div>
          <div className="compass-line diagonal2"></div>
        </div>
        
        <div className="direction-ring"></div>
        
        {/* 中央の星 */}
        <div 
          className="center-star"
          style={{
            background: `linear-gradient(135deg, ${getElementColor(currentData.center.element)}, #FFD700, #FFA500)`
          }}
          onClick={() => console.log('Center star clicked:', currentData.center)}
        >
          <div className="star-name">
            {currentData.center.name.replace('星', '').split('').map((char, i) => (
              <div key={i}>{char}</div>
            ))}
          </div>
        </div>
        
        {/* 八方位の星 */}
        {currentData.positions.map((star, index) => (
          <div
            key={index}
            className={`star-element ${directionClasses[index]} ${hoveredStar === index ? 'hovered' : ''}`}
            onMouseEnter={() => interactive && setHoveredStar(index)}
            onMouseLeave={() => interactive && setHoveredStar(null)}
            onClick={() => handleStarClick(star)}
            style={{
              borderColor: getElementColor(star.element),
              '--element-color': getElementColor(star.element)
            } as React.CSSProperties}
          >
            <div className="star-name">{star.name}</div>
            <div className="direction">{star.direction}</div>
            <div className="zodiac">{star.zodiac}</div>
          </div>
        ))}
      </div>
      
      <p className="kyusei-subtitle">Modern Luxury Design</p>
    </div>
  );
};

export default KyuseiBoard; 