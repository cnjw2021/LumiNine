export interface ElementData {
  label: string;
  color: string;
  starNames: string[];
  iconPath?: string;
}

/**
 * 五行生成サイクルSVGを生成
 * @param size SVGの幅・高さ(px)
 * @returns SVG文字列
 */
export const generateFiveElementsCycleSVG = (size: number = 600): string => {
  // 外側の要素を考慮したパディングを追加
  const padding = size * 0.2; // 20%のパディング
  const viewBoxSize = size + (padding * 2); // ビューボックスサイズ
  const centerX = viewBoxSize / 2;
  const centerY = viewBoxSize / 2;
  
  // メインの円の半径（パディングを考慮）
  const radius = size * 0.35;
  const circleRadius = size * 0.0675;
  const iconSizeGlobal = circleRadius * 4;
  const iconRadius = iconSizeGlobal / 2;

  // 円形矢印と要素間のギャップを増加
  const gap = size * 0.015;
  const arrowRadius = radius + iconRadius + gap;
  const angleGap = 8 * Math.PI / 180;

  // 五行要素データ（変更なし）
  const elements: ElementData[] = [
    {
      label: "木",
      color: "#22C55E",
      starNames: ["三碧木星", "四緑木星"],
      iconPath: "/images/elements/wood.png",
    },
    {
      label: "火",
      color: "#EF4444",
      starNames: ["九紫火星"],
      iconPath: "/images/elements/fire.png",
    },
    {
      label: "土",
      color: "#F59E0B",
      starNames: ["二黒土星", "五黄土星", "八白土星"],
      iconPath: "/images/elements/earth.png",
    },
    {
      label: "金",
      color: "#D4AF37",
      starNames: ["六白金星", "七赤金星"],
      iconPath: "/images/elements/metal.png",
    },
    {
      label: "水",
      color: "#3B82F6",
      starNames: ["一白水星"],
      iconPath: "/images/elements/water.png",
    },
  ];

  // 各要素の座標を計算（時計回り、木を上に）
  const positions = elements.map((_, i) => {
    const angleDeg = 90 - i * 72; // 0:木(90°) → 時計回り
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: centerX + Math.cos(rad) * radius,
      y: centerY - Math.sin(rad) * radius,
    };
  });

  // SVGコンテンツ生成
  const iconSymbols = `
    <!-- カラー木アイコン（tree_nobackground.svg を直接参照） -->
    <symbol id="iconWood" viewBox="0 0 80 80">
      <!-- 元SVGは <rect>+<pattern><image> 構成。パターンを残すと <use> で崩れるため直接 <image> 参照 -->
      <!-- Next.js では /public がウェブルートになるため /images/elements に配置 -->
      <image href="/images/elements/tree_nobackground.svg" width="80" height="80" preserveAspectRatio="xMidYMid meet" />
    </symbol>
    <!-- カラー火アイコン -->
    <symbol id="iconFire" viewBox="0 0 80 80">
      <image href="/images/elements/fire_nobackgound.svg" width="80" height="80" preserveAspectRatio="xMidYMid meet" />
    </symbol>
    <!-- カラー土アイコン -->
    <symbol id="iconEarth" viewBox="0 0 80 80">
      <image href="/images/elements/land_nobackground.svg" width="80" height="80" preserveAspectRatio="xMidYMid meet" />
    </symbol>
    <!-- カラー金アイコン -->
    <symbol id="iconMetal" viewBox="0 0 80 80">
      <image href="/images/elements/metal_background.svg" width="80" height="80" preserveAspectRatio="xMidYMid meet" />
    </symbol>
    <!-- カラー水アイコン -->
    <symbol id="iconWater" viewBox="0 0 80 80">
      <image href="/images/elements/water_nobackground.svg" width="80" height="80" preserveAspectRatio="xMidYMid meet" />
    </symbol>`;

  let svg = `<svg 
    width="${viewBoxSize}" 
    height="${viewBoxSize}" 
    viewBox="0 0 ${viewBoxSize} ${viewBoxSize}" 
    xmlns="http://www.w3.org/2000/svg" 
    style="font-family:'Noto Sans JP', 'Inter', sans-serif;"
  >
    <defs>
      ${iconSymbols}
      <marker id="arrowHead" viewBox="0 0 20 20" refX="18" refY="10" markerWidth="10" markerHeight="10" orient="auto-start-reverse">
        <path d="M 0 0 L 20 10 L 0 20 z" fill="#000" />
      </marker>
      <marker id="arrowHeadGray" viewBox="0 0 14 14" refX="12" refY="7" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 14 7 L 0 14 z" fill="rgba(0,0,0,0.35)" />
      </marker>
    </defs>`;

  // 外周の生成サイクル矢印を円弧で描画
  elements.forEach((_, i) => {
    const fromIdx = i;
    const toIdx = (i + 1) % elements.length;

    // 角度計算
    const angleFromRaw = (90 - fromIdx * 72) * Math.PI / 180;
    const angleToRaw = (90 - toIdx * 72) * Math.PI / 180;
    // アイコンとの間隔を確保するため、始点と終点の角度を調整
    const startAngle = angleFromRaw - angleGap - (Math.PI / 18); // 追加で10度分開始点を手前に
    const endAngle = angleToRaw + angleGap + (Math.PI / 18);   // 追加で10度分終点を先に

    // 始点・終点座標
    const sx = centerX + Math.cos(startAngle) * arrowRadius;
    const sy = centerY - Math.sin(startAngle) * arrowRadius;
    const ex = centerX + Math.cos(endAngle) * arrowRadius;
    const ey = centerY - Math.sin(endAngle) * arrowRadius;

    // SVG arc flags
    const largeArcFlag = 0;
    const sweepFlag = 1;
    const startCol = elements[fromIdx].color;
    const endCol = elements[toIdx].color;
    const gradId = `gradOut${i}`;
    const markerId = `arrowHeadOut${i}`;

    // 説明文を追加
    const isWoodToFire = elements[fromIdx].label === "木" && elements[toIdx].label === "火";
    const isFireToEarth = elements[fromIdx].label === "火" && elements[toIdx].label === "土";
    const isEarthToMetal = elements[fromIdx].label === "土" && elements[toIdx].label === "金";
    const isMetalToWater = elements[fromIdx].label === "金" && elements[toIdx].label === "水";
    const isWaterToWood = elements[fromIdx].label === "水" && elements[toIdx].label === "木";
    
    // 基本の位置計算
    let textRadius = arrowRadius + (size * 0.07); // 基本の半径
    let textAngle = (angleFromRaw + angleToRaw) / 2.2; // 基本の角度

    // 位置調整
    if (isFireToEarth) {
      textRadius = arrowRadius + (size * 0.11); // より外側に
      textAngle = textAngle + (Math.PI / 84); // 反時計回りに7.5度
    } else if (isEarthToMetal) {
      textRadius = arrowRadius + (size * 0.06); // さらに外側に
      textAngle = textAngle - (Math.PI / 24); // 左側に移動（反時計回りに15度）
    } else if (isMetalToWater) {
      textRadius = arrowRadius + (size * 0.1); // より外側に
      textAngle = textAngle - (Math.PI / 12); // 時計回りに5度
    } else if (isWaterToWood) {
      textRadius = arrowRadius + (size * 0.06); // より外側に配置
      textAngle = angleFromRaw - (Math.PI / 6); // 時計回りに30度
    }

    const textX = centerX + Math.cos(textAngle) * textRadius;
    const textY = centerY - Math.sin(textAngle) * textRadius;
    const fontSize = (size * 0.025).toFixed(2);

    svg += `
      <defs>
        <linearGradient id="${gradId}" gradientUnits="userSpaceOnUse" x1="${sx.toFixed(2)}" y1="${sy.toFixed(2)}" x2="${ex.toFixed(2)}" y2="${ey.toFixed(2)}">
          <stop offset="0%" stop-color="${startCol}"/>
          <stop offset="100%" stop-color="${endCol}"/>
        </linearGradient>
        <marker id="${markerId}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="${endCol}"/>
        </marker>
      </defs>
      <path d="M ${sx.toFixed(2)} ${sy.toFixed(2)} A ${arrowRadius.toFixed(2)} ${arrowRadius.toFixed(2)} 0 ${largeArcFlag} ${sweepFlag} ${ex.toFixed(2)} ${ey.toFixed(2)}" 
            stroke="url(#${gradId})" 
            stroke-width="3" 
            fill="none" 
            marker-end="url(#${markerId})" />`;

    // 説明文の描画
    if (isWoodToFire) {
      svg += `
        <text x="${textX.toFixed(2)}" y="${textY.toFixed(2)}"
              text-anchor="middle"
              font-size="${fontSize}"
              fill="#333333"
              style="filter: drop-shadow(0px 0px 2px white)">
          <tspan x="${textX.toFixed(2)}" dy="-0.5em">木は燃えて</tspan>
          <tspan x="${textX.toFixed(2)}" dy="1.2em">火を生む</tspan>
        </text>`;
    } else if (isFireToEarth) {
      svg += `
        <text x="${textX.toFixed(2)}" y="${textY.toFixed(2)}"
              text-anchor="middle"
              font-size="${fontSize}"
              fill="#333333"
              style="filter: drop-shadow(0px 0px 2px white)">
          <tspan x="${textX.toFixed(2)}" dy="-0.5em">火は燃えて</tspan>
          <tspan x="${textX.toFixed(2)}" dy="1.2em">灰と土が生まれる</tspan>
        </text>`;
    } else if (isEarthToMetal) {
      svg += `
        <text x="${textX.toFixed(2)}" y="${textY.toFixed(2)}"
              text-anchor="middle"
              font-size="${fontSize}"
              fill="#333333"
              style="filter: drop-shadow(0px 0px 2px white)">
          <tspan x="${textX.toFixed(2)}" dy="-0.5em">土の中から</tspan>
          <tspan x="${textX.toFixed(2)}" dy="1.2em">金属を産出する</tspan>
        </text>`;
    } else if (isMetalToWater) {
      svg += `
        <text x="${textX.toFixed(2)}" y="${textY.toFixed(2)}"
              text-anchor="middle"
              font-size="${fontSize}"
              fill="#333333"
              style="filter: drop-shadow(0px 0px 2px white)">
          <tspan x="${textX.toFixed(2)}" dy="-0.5em">金属の表面に</tspan>
          <tspan x="${textX.toFixed(2)}" dy="1.2em">水が生じる</tspan>
        </text>`;
    } else if (isWaterToWood) {
      svg += `
        <text x="${textX.toFixed(2)}" y="${textY.toFixed(2)}"
              text-anchor="middle" 
              font-size="${fontSize}"
              fill="#333333"
              style="filter: drop-shadow(0px 0px 2px white)">
            <tspan x="${textX.toFixed(2)}" dy="-0.5em">水は木を</tspan>
            <tspan x="${textX.toFixed(2)}" dy="1.2em">育てる</tspan>
          </text>`;
    }
  });

  // 内側星形の制剋ライン
  const innerRadius = radius * 0.55;
  const starNodes = positions.map((pos) => {
    const ux = (pos.x - centerX) / radius;
    const uy = (pos.y - centerY) / radius;
    return {
      x: centerX + ux * innerRadius,
      y: centerY + uy * innerRadius,
    };
  });

  // 制剋ライン描画
  const controlOrder = [0, 2, 4, 1, 3, 0];
  const gapAlong = size * 0.02;
  for (let i = 0; i < controlOrder.length - 1; i++) {
    const fromNode = starNodes[controlOrder[i]];
    const toNode = starNodes[controlOrder[i + 1]];
    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const len = Math.hypot(dx, dy);
    const ux = dx / len;
    const uy = dy / len;
    const sx = fromNode.x + ux * gapAlong;
    const sy = fromNode.y + uy * gapAlong;
    const ex = toNode.x - ux * gapAlong;
    const ey = toNode.y - uy * gapAlong;
    
    svg += `
      <line x1="${sx.toFixed(2)}" y1="${sy.toFixed(2)}" 
            x2="${ex.toFixed(2)}" y2="${ey.toFixed(2)}" 
            stroke="rgba(0,0,0,0.35)" 
            stroke-width="1.2" 
            marker-end="url(#arrowHeadGray)" />`;
  }

  // 各要素のアイコン・ラベル
  elements.forEach((el, i) => {
    const { x, y } = positions[i];
    const iconSize = iconSizeGlobal;
    const ux = (x - centerX) / radius;
    const uy = (y - centerY) / radius;
    
    // オフセットを調整
    const circleOffset = -size * 0.05;
    const iconOffset = circleRadius + size * 0.04;
    const labelOffset = size * 0.11;

    const circleX = x + ux * circleOffset;
    const circleY = y + uy * circleOffset;
    let iconX = x + ux * iconOffset - iconSize / 2;
    let iconY = y + uy * iconOffset - iconSize / 2;

    // アイコンの位置調整
    if (el.label === '水') {
      iconX -= size * 0.05; // 左に5%移動
    }
    else if (el.label === '木') {
      iconX += size * 0.01; // 微調整
      iconY -= size * 0.03; // 上に3%移動
    }
    else if (el.label === '火') {
      iconX += size * 0.05; // 右に5%移動
    }

    // アイコンの配置
    const symbolId = {
      木: 'iconWood',
      火: 'iconFire',
      土: 'iconEarth',
      金: 'iconMetal',
      水: 'iconWater',
    }[el.label];

    svg += `
      <use href="#${symbolId}" 
           x="${iconX.toFixed(2)}" 
           y="${iconY.toFixed(2)}" 
           width="${iconSize}" 
           height="${iconSize}" />
      <circle cx="${circleX.toFixed(2)}" 
              cy="${circleY.toFixed(2)}" 
              r="${circleRadius}" 
              fill="${el.color}" />
      <text x="${circleX.toFixed(2)}" 
            y="${(circleY + 4).toFixed(2)}" 
            text-anchor="middle" 
            dominant-baseline="middle" 
            font-size="${(size * 0.05625).toFixed(2)}" 
            font-weight="900" 
            fill="#fff">${el.label}</text>`;

    // 星名リスト
    el.starNames.forEach((name, idx) => {
      const lineHeight = size * 0.033;
      
      // 位置調整のロジックを改善
      let anchor = 'middle';
      let offset = labelOffset * 2.5; // 基本オフセットを2.5倍に
      let angleOffset = 0;

      // 要素ごとの位置調整
      switch(el.label) {
        case '木': // 上
          anchor = 'middle';
          angleOffset = -90;
          break;
        case '火': // 右上
          anchor = 'start';
          angleOffset = -20; // より上向きに（15度から-35度に変更）
          offset = labelOffset * 1.9; // オフセットを調整して右に
          break;
        case '土': // 右下
          anchor = 'start';
          angleOffset = 45;
          break;
        case '金': // 下
          anchor = 'end'; // 左寄せに変更
          angleOffset = 125; // 角度を調整して左に
          offset = labelOffset * 2.3; // オフセットを増加
          break;
        case '水': // 左
          anchor = 'end';
          angleOffset = 199;
          offset = labelOffset * 1.8; // オフセットを増加して左側により大きなスペースを確保
          break;
      }

      // 角度に基づいて位置を計算
      const rad = (angleOffset * Math.PI) / 180;
      const nameX = x + Math.cos(rad) * offset;
      const verticalSpacing = lineHeight * 1.3;
      const verticalOffset = (idx - (el.starNames.length - 1) / 2) * verticalSpacing;
      const nameY = y + Math.sin(rad) * offset + verticalOffset;
      
      svg += `
        <text x="${nameX.toFixed(2)}" 
              y="${nameY.toFixed(2)}" 
              text-anchor="${anchor}" 
              font-size="${(size * 0.04).toFixed(2)}"
              font-weight="bold" 
              fill="#000">${name}</text>`;
    });
  });

  // 相剋のテキスト追加
  // 木→土の相剋テキスト
  const woodEarthStartAngle = -Math.PI / 2.1; // 木の位置（上）から開始
  const woodEarthAngle = woodEarthStartAngle + (Math.PI / 8); // 木により近い位置に
  const woodEarthRadius = radius * 0.55; // より内側に
  const woodEarthX = centerX + Math.cos(woodEarthAngle) * woodEarthRadius;
  const woodEarthY = centerY + Math.sin(woodEarthAngle) * woodEarthRadius;
  const controlFontSize = size * 0.025; // 相生と同じサイズ

  // 土→水の相剋テキスト
  const earthWaterStartAngle = Math.PI / 3.2; // 土の位置から
  const earthWaterAngle = earthWaterStartAngle + (Math.PI / 8); // 土により近い位置に
  const earthWaterRadius = radius * 0.6; // 木→土と同じ距離
  const earthWaterX = centerX + Math.cos(earthWaterAngle) * earthWaterRadius;
  const earthWaterY = centerY + Math.sin(earthWaterAngle) * earthWaterRadius;

  // 水→火の相剋テキスト
  const waterFireStartAngle = Math.PI; // 水の位置から
  const waterFireAngle = waterFireStartAngle + (Math.PI / 4.5); // 水により近い位置に
  const waterFireRadius = radius * 0.55; // 土→水と同じ距離
  const waterFireX = centerX + Math.cos(waterFireAngle) * waterFireRadius;
  const waterFireY = centerY + Math.sin(waterFireAngle) * waterFireRadius;

  // 火→金の相剋テキスト
  const fireMetalStartAngle = -Math.PI / 6; // 火の位置から
  const fireMetalAngle = fireMetalStartAngle + (Math.PI / 5); // 火により近い位置に
  const fireMetalRadius = radius * 0.55; // 他と同じ距離
  const fireMetalX = centerX + Math.cos(fireMetalAngle) * fireMetalRadius;
  const fireMetalY = centerY + Math.sin(fireMetalAngle) * fireMetalRadius;

  // 金→木の相剋テキスト
  const metalWoodStartAngle = Math.PI * 0.5; // 金の位置から
  const metalWoodAngle = metalWoodStartAngle + (Math.PI / 3.2); // 金により近い位置に
  const metalWoodRadius = radius * 0.6; // 他と同じ距離
  const metalWoodX = centerX + Math.cos(metalWoodAngle) * metalWoodRadius;
  const metalWoodY = centerY + Math.sin(metalWoodAngle) * metalWoodRadius;

  svg += `
    <text x="${woodEarthX.toFixed(2)}" y="${woodEarthY.toFixed(2)}"
        text-anchor="middle" 
        font-size="${controlFontSize}"
        fill="#333333"
        dominant-baseline="middle"
        style="filter: drop-shadow(0px 0px 2px white)">
      <tspan x="${woodEarthX.toFixed(2)}" dy="-1.4em">木が土から</tspan>
      <tspan x="${woodEarthX.toFixed(2)}" dy="1.4em">養分を</tspan>
      <tspan x="${woodEarthX.toFixed(2)}" dy="1.4em">奪い取る</tspan>
    </text>
    <text x="${earthWaterX.toFixed(2)}" y="${earthWaterY.toFixed(2)}"
        text-anchor="middle" 
        font-size="${controlFontSize}"
        fill="#333333"
        dominant-baseline="middle"
        style="filter: drop-shadow(0px 0px 2px white)">
      <tspan x="${earthWaterX.toFixed(2)}" dy="-1.4em">土が</tspan>
      <tspan x="${earthWaterX.toFixed(2)}" dy="1.4em">水の流れを</tspan>
      <tspan x="${earthWaterX.toFixed(2)}" dy="1.4em">せき止める</tspan>
    </text>
    <text x="${waterFireX.toFixed(2)}" y="${waterFireY.toFixed(2)}"
        text-anchor="middle" 
        font-size="${controlFontSize}"
        fill="#333333"
        dominant-baseline="middle"
        style="filter: drop-shadow(0px 0px 2px white)">
      <tspan x="${waterFireX.toFixed(2)}" dy="-1.4em">水が</tspan>
      <tspan x="${waterFireX.toFixed(2)}" dy="1.4em">燃える火を</tspan>
      <tspan x="${waterFireX.toFixed(2)}" dy="1.4em">消し去る</tspan>
    </text>
    <text x="${fireMetalX.toFixed(2)}" y="${fireMetalY.toFixed(2)}"
        text-anchor="middle" 
        font-size="${controlFontSize}"
        fill="#333333"
        dominant-baseline="middle"
        style="filter: drop-shadow(0px 0px 2px white)">
      <tspan x="${fireMetalX.toFixed(2)}" dy="-1.4em">火が</tspan>
      <tspan x="${fireMetalX.toFixed(2)}" dy="1.4em">金属を</tspan>
      <tspan x="${fireMetalX.toFixed(2)}" dy="1.4em">溶かす</tspan>
    </text>
    <text x="${metalWoodX.toFixed(2)}" y="${metalWoodY.toFixed(2)}"
        text-anchor="middle" 
        font-size="${controlFontSize}"
        fill="#333333"
        dominant-baseline="middle"
        style="filter: drop-shadow(0px 0px 2px white)">
      <tspan x="${metalWoodX.toFixed(2)}" dy="-1.4em">金属が</tspan>
      <tspan x="${metalWoodX.toFixed(2)}" dy="1.4em">木材を</tspan>
      <tspan x="${metalWoodX.toFixed(2)}" dy="1.4em">切り倒す</tspan>
    </text>`;

  svg += '</svg>';
  return svg;
};