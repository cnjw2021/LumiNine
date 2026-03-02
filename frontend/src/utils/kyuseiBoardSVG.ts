// 九星盤SVG生成ユーティリティ
// React版と完全に同じデザインのSVGを生成

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

// 九星ごとの正確な配置データ
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

// 五行カラーマッピング
const elementColors: Record<string, string> = {
  木: "#22C55E", // 緑
  火: "#EF4444", // 赤
  土: "#F59E0B", // 黄
  金: "#D4AF37", // 金
  水: "#3B82F6"  // 青
};

const getElementColor = (element: string): string => {
  return elementColors[element] || '#D4AF37';
};

const calculatePosition = (angle: number, radius: number): { x: number; y: number } => {
  const radian = ((angle + 90) * Math.PI) / 180;
  const x = Math.cos(radian) * radius;
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

export const generateKyuseiBoardSVG = (
  centerStar: string = "一白水星",
  size: number = 600
): string => {
  const currentData = starConfigurations[centerStar] || starConfigurations["一白水星"];
  const svgSize = size;
  const centerX = svgSize / 2;
  const centerY = svgSize / 2;

  let svgContent = `
    <svg width="${svgSize}" height="${svgSize}" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Noto Sans JP', 'Inter', sans-serif;">
      <defs>
        <!-- 背景のラジアルグラデーション（React版と同じ） -->
        <radialGradient id="backgroundRadialGradient" cx="50%" cy="50%" r="70%">
          <stop offset="0%" style="stop-color:#343481;stop-opacity:1"/>
          <stop offset="50%" style="stop-color:#24245f;stop-opacity:1"/>
          <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:1"/>
        </radialGradient>
        
        <!-- 中央星のグラデーション（五行色に応じた動的グラデーション） -->
        <linearGradient id="centerStarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${getElementColor(currentData.center.element)};stop-opacity:1"/>
          <stop offset="100%" style="stop-color:#FFA500;stop-opacity:1"/>
        </linearGradient>
        
        <!-- 光の線のグラデーション -->
        <linearGradient id="lightLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
          <stop offset="5%" style="stop-color:rgba(212,175,55,0.05);stop-opacity:1"/>
          <stop offset="15%" style="stop-color:rgba(212,175,55,0.2);stop-opacity:1"/>
          <stop offset="25%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="35%" style="stop-color:rgba(212,175,55,0.7);stop-opacity:1"/>
          <stop offset="45%" style="stop-color:rgba(212,175,55,0.9);stop-opacity:1"/>
          <stop offset="55%" style="stop-color:rgba(212,175,55,0.7);stop-opacity:1"/>
          <stop offset="70%" style="stop-color:rgba(212,175,55,0.4);stop-opacity:1"/>
          <stop offset="90%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- 光の線の先端効果 -->
        <linearGradient id="lightLineTipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:rgba(212,175,55,0.3);stop-opacity:1"/>
          <stop offset="30%" style="stop-color:rgba(212,175,55,0.1);stop-opacity:1"/>
          <stop offset="70%" style="stop-color:rgba(212,175,55,0.02);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
        </linearGradient>
        
        <!-- 星のグロー効果 -->
        <radialGradient id="starGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:rgba(255,255,255,0.3);stop-opacity:1"/>
          <stop offset="100%" style="stop-color:rgba(255,255,255,0.1);stop-opacity:1"/>
        </radialGradient>
        
        <!-- ドロップシャドウフィルター -->
        <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(0,0,0,0.15)"/>
        </filter>
        
        <!-- 光るエフェクトフィルター -->
        <filter id="glowFilter" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        <!-- 強い光るエフェクト -->
        <filter id="strongGlow" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- 背景円（ラジアルグラデーション） -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.48}" fill="url(#backgroundRadialGradient)" stroke="none"/>
      
      <!-- メインボード円 -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.42}" 
              fill="rgba(255, 255, 255, 0.05)" stroke="rgba(135, 206, 250, 0.3)" stroke-width="1" 
              filter="url(#dropShadow)"/>
      
      <!-- 内側の円 -->
      <circle cx="${centerX}" cy="${centerY}" r="${svgSize * 0.25}" 
              fill="none" stroke="rgba(212, 175, 55, 0.3)" stroke-width="2"/>
  `;

  // 光の線を追加（九星気学の正しい方位境界：東西南北30度、傾斜面60度）
  const boundaryAngles = [0, 15, 75, 105, 165, 195, 255, 285, 345]; // 方位境界線
  
  boundaryAngles.forEach(angle => {
    const radian = (angle * Math.PI) / 180;
    // 外周から中心に向かう線（React版のCSS仕様に合わせる）
    const x1 = centerX + Math.cos(radian) * svgSize * 0.48; // 外周から開始
    const y1 = centerY + Math.sin(radian) * svgSize * 0.48;
    const x2 = centerX; // 中心で終了
    const y2 = centerY;
    
    // メインライン（外周から中心へ）
    svgContent += `
      <line x1="${x1.toFixed(2)}" y1="${y1.toFixed(2)}" x2="${x2.toFixed(2)}" y2="${y2.toFixed(2)}" 
            stroke="url(#lightLineGradient)" stroke-width="0.5" opacity="1" filter="url(#strongGlow)"/>
    `;
    
    // 光の先端効果（外周の15%部分）
    const tipLength = svgSize * 0.48 * 0.15; // 外周の15%
    const tipX1 = centerX + Math.cos(radian) * svgSize * 0.48;
    const tipY1 = centerY + Math.sin(radian) * svgSize * 0.48;
    const tipX2 = centerX + Math.cos(radian) * (svgSize * 0.48 - tipLength);
    const tipY2 = centerY + Math.sin(radian) * (svgSize * 0.48 - tipLength);
    
    svgContent += `
      <line x1="${tipX1.toFixed(2)}" y1="${tipY1.toFixed(2)}" x2="${tipX2.toFixed(2)}" y2="${tipY2.toFixed(2)}" 
            stroke="url(#lightLineTipGradient)" stroke-width="0.2" opacity="1" filter="url(#glowFilter)"/>
    `;
  });

  // 中央の星（金色グラデーション、白い枠線なし）
  svgContent += `
    <circle cx="${centerX}" cy="${centerY}" r="50" 
            fill="url(#centerStarGradient)" filter="url(#dropShadow)"/>
    <text x="${centerX}" y="${centerY + 4}" text-anchor="middle" 
          font-size="14" font-weight="700" fill="#FFFFFF" 
          font-family="'Noto Sans JP', 'Inter', sans-serif"
          text-shadow="0 2px 4px rgba(0, 0, 0, 0.5)">
      ${currentData.center.name}
    </text>
  `;

  // 八方位の星、干支ラベル、方位ラベルを追加（文字回転付き）
  currentData.positions.forEach((star: Star, index: number) => {
    // 八方位の星
    const radius = svgSize * 0.35;
    const position = calculatePosition(star.angle, radius);
    const x = centerX + position.x;
    const y = centerY + position.y;
    const directionInfo = FIXED_DIRECTIONS[index];
    const readableAngle = getReadableRotation(star.angle);
    
    const boxWidth = svgSize * 0.14;
    const boxHeight = svgSize * 0.1;
    
    // 各九星の五行色を取得
    const starElementColor = getElementColor(star.element);
    
    // ボックス自体も回転させる
    svgContent += `
      <g transform="rotate(${readableAngle}, ${x.toFixed(2)}, ${y.toFixed(2)})">
        <rect x="${(x - boxWidth/2).toFixed(2)}" y="${(y - boxHeight/2).toFixed(2)}" 
              width="${boxWidth.toFixed(2)}" height="${boxHeight.toFixed(2)}" 
              fill="rgba(255, 255, 255, 0.1)" stroke="${starElementColor}" stroke-width="1" 
              rx="${(svgSize * 0.02).toFixed(2)}" ry="${(svgSize * 0.02).toFixed(2)}" filter="url(#dropShadow)"/>
        <text x="${x.toFixed(2)}" y="${(y + 2).toFixed(2)}" text-anchor="middle" 
              font-size="${(svgSize * 0.022).toFixed(2)}" font-weight="600" fill="#F9FAFB" 
              font-family="'Noto Sans JP', 'Inter', sans-serif" letter-spacing="0.5px">
          ${star.name}
        </text>
      </g>
    `;

    // 干支ラベル（回転付き）
    const zodiacRadius = svgSize * 0.25;
    const zodiacPosition = calculatePosition(star.angle, zodiacRadius);
    const zodiacX = centerX + zodiacPosition.x;
    const zodiacY = centerY + zodiacPosition.y;
    
    svgContent += `
      <text x="${zodiacX.toFixed(2)}" y="${(zodiacY + 2).toFixed(2)}" text-anchor="middle" 
            font-size="${(svgSize * 0.018).toFixed(2)}" font-weight="500" fill="#E5E7EB" 
            font-family="'Noto Sans JP', 'Inter', sans-serif"
            transform="rotate(${readableAngle}, ${zodiacX.toFixed(2)}, ${(zodiacY + 2).toFixed(2)})">
        ${directionInfo.zodiac}
      </text>
    `;

    // 外側の方位ラベル（回転付き）
    const directionRadius = svgSize * 0.17;
    const directionPosition = calculatePosition(star.angle, directionRadius);
    const directionX = centerX + directionPosition.x;
    const directionY = centerY + directionPosition.y;
    
    svgContent += `
      <text x="${directionX.toFixed(2)}" y="${(directionY + 2).toFixed(2)}" text-anchor="middle" 
            font-size="${(svgSize * 0.023).toFixed(2)}" font-weight="600" fill="#F3F4F6" 
            font-family="'Noto Sans JP', 'Inter', sans-serif"
            transform="rotate(${readableAngle}, ${directionX.toFixed(2)}, ${(directionY + 2).toFixed(2)})">
        ${directionInfo.direction}
      </text>
    `;
  });

  svgContent += '</svg>';
  return svgContent;
}; 