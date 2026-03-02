import React from "react";
import { generateFiveElementsCycleSVG } from "@/utils/fiveElementsCycleSVG";

interface FiveElementsCycleProps {
  size?: number; // SVGサイズ
}

/**
 * 添付図のような五行生成サイクル図を描画するコンポーネント
 */
const FiveElementsCycle: React.FC<FiveElementsCycleProps> = ({ size = 600 }) => {
  const svgString = generateFiveElementsCycleSVG(size);
  const viewBoxSize = size + (size * 0.4); // パディングを含む実際のサイズ

  return (
    <div
      className="five-elements-cycle"
      style={{
        width: viewBoxSize,
        height: viewBoxSize,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 0,
        margin: 0
      }}
      dangerouslySetInnerHTML={{ __html: svgString }}
    />
  );
};

export default FiveElementsCycle; 