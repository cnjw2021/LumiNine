"""
九星盤SVG生成サービス
React版と同じ雰囲気の九星盤SVGを生成する
"""
import math
import os
from datetime import datetime
from typing import Dict, Any
from core.utils.logger import get_logger

logger = get_logger(__name__)


class SvgGeneratorService:
    """九星盤SVG生成サービス"""
    
    def __init__(self):
        # 九星ごとの正確な配置データ（React版と同じ）
        self.star_configurations = {
            "一白水星": {
                "center": {"name": "一白水星", "element": "水"},
                "positions": [
                    {"name": "四緑木星", "element": "木", "angle": 45},    # 北東
                    {"name": "八白土星", "element": "土", "angle": 90},    # 東
                    {"name": "九紫火星", "element": "火", "angle": 135},   # 南東
                    {"name": "五黄土星", "element": "土", "angle": 180},   # 南
                    {"name": "七赤金星", "element": "金", "angle": 225},   # 南西
                    {"name": "三碧木星", "element": "木", "angle": 270},   # 西
                    {"name": "二黒土星", "element": "土", "angle": 315},   # 北西
                    {"name": "六白金星", "element": "金", "angle": 0}      # 北
                ]
            },
            "二黒土星": {
                "center": {"name": "二黒土星", "element": "土"},
                "positions": [
                    {"name": "五黄土星", "element": "土", "angle": 45},    # 北東
                    {"name": "九紫火星", "element": "火", "angle": 90},    # 東
                    {"name": "一白水星", "element": "水", "angle": 135},   # 南東
                    {"name": "六白金星", "element": "金", "angle": 180},   # 南
                    {"name": "八白土星", "element": "土", "angle": 225},   # 南西
                    {"name": "四緑木星", "element": "木", "angle": 270},   # 西
                    {"name": "三碧木星", "element": "木", "angle": 315},   # 北西
                    {"name": "七赤金星", "element": "金", "angle": 0}      # 北
                ]
            },
            "三碧木星": {
                "center": {"name": "三碧木星", "element": "木"},
                "positions": [
                    {"name": "六白金星", "element": "金", "angle": 45},    # 北東
                    {"name": "一白水星", "element": "水", "angle": 90},    # 東
                    {"name": "二黒土星", "element": "土", "angle": 135},   # 南東
                    {"name": "七赤金星", "element": "金", "angle": 180},   # 南
                    {"name": "九紫火星", "element": "火", "angle": 225},   # 南西
                    {"name": "五黄土星", "element": "土", "angle": 270},   # 西
                    {"name": "四緑木星", "element": "木", "angle": 315},   # 北西
                    {"name": "八白土星", "element": "土", "angle": 0}      # 北
                ]
            },
            "四緑木星": {
                "center": {"name": "四緑木星", "element": "木"},
                "positions": [
                    {"name": "七赤金星", "element": "金", "angle": 45},    # 北東
                    {"name": "二黒土星", "element": "土", "angle": 90},    # 東
                    {"name": "三碧木星", "element": "木", "angle": 135},   # 南東
                    {"name": "八白土星", "element": "土", "angle": 180},   # 南
                    {"name": "一白水星", "element": "水", "angle": 225},   # 南西
                    {"name": "六白金星", "element": "金", "angle": 270},   # 西
                    {"name": "五黄土星", "element": "土", "angle": 315},   # 北西
                    {"name": "九紫火星", "element": "火", "angle": 0}      # 北
                ]
            },
            "五黄土星": {
                "center": {"name": "五黄土星", "element": "土"},
                "positions": [
                    {"name": "八白土星", "element": "土", "angle": 45},    # 北東
                    {"name": "三碧木星", "element": "木", "angle": 90},    # 東
                    {"name": "四緑木星", "element": "木", "angle": 135},   # 南東
                    {"name": "九紫火星", "element": "火", "angle": 180},   # 南
                    {"name": "二黒土星", "element": "土", "angle": 225},   # 南西
                    {"name": "七赤金星", "element": "金", "angle": 270},   # 西
                    {"name": "六白金星", "element": "金", "angle": 315},   # 北西
                    {"name": "一白水星", "element": "水", "angle": 0}      # 北
                ]
            },
            "六白金星": {
                "center": {"name": "六白金星", "element": "金"},
                "positions": [
                    {"name": "九紫火星", "element": "火", "angle": 45},    # 北東
                    {"name": "四緑木星", "element": "木", "angle": 90},    # 東
                    {"name": "五黄土星", "element": "土", "angle": 135},   # 南東
                    {"name": "一白水星", "element": "水", "angle": 180},   # 南
                    {"name": "三碧木星", "element": "木", "angle": 225},   # 南西
                    {"name": "八白土星", "element": "土", "angle": 270},   # 西
                    {"name": "七赤金星", "element": "金", "angle": 315},   # 北西
                    {"name": "二黒土星", "element": "土", "angle": 0}      # 北
                ]
            },
            "七赤金星": {
                "center": {"name": "七赤金星", "element": "金"},
                "positions": [
                    {"name": "一白水星", "element": "水", "angle": 45},    # 北東
                    {"name": "五黄土星", "element": "土", "angle": 90},    # 東
                    {"name": "六白金星", "element": "金", "angle": 135},   # 南東
                    {"name": "二黒土星", "element": "土", "angle": 180},   # 南
                    {"name": "四緑木星", "element": "木", "angle": 225},   # 南西
                    {"name": "九紫火星", "element": "火", "angle": 270},   # 西
                    {"name": "八白土星", "element": "土", "angle": 315},   # 北西
                    {"name": "三碧木星", "element": "木", "angle": 0}      # 北
                ]
            },
            "八白土星": {
                "center": {"name": "八白土星", "element": "土"},
                "positions": [
                    {"name": "二黒土星", "element": "土", "angle": 45},    # 北東
                    {"name": "六白金星", "element": "金", "angle": 90},    # 東
                    {"name": "七赤金星", "element": "金", "angle": 135},   # 南東
                    {"name": "三碧木星", "element": "木", "angle": 180},   # 南
                    {"name": "五黄土星", "element": "土", "angle": 225},   # 南西
                    {"name": "一白水星", "element": "水", "angle": 270},   # 西
                    {"name": "九紫火星", "element": "火", "angle": 315},   # 北西
                    {"name": "四緑木星", "element": "木", "angle": 0}      # 北
                ]
            },
            "九紫火星": {
                "center": {"name": "九紫火星", "element": "火"},
                "positions": [
                    {"name": "三碧木星", "element": "木", "angle": 45},    # 北東
                    {"name": "七赤金星", "element": "金", "angle": 90},    # 東
                    {"name": "八白土星", "element": "土", "angle": 135},   # 南東
                    {"name": "四緑木星", "element": "木", "angle": 180},   # 南
                    {"name": "六白金星", "element": "金", "angle": 225},   # 南西
                    {"name": "二黒土星", "element": "土", "angle": 270},   # 西
                    {"name": "一白水星", "element": "水", "angle": 315},   # 北西
                    {"name": "五黄土星", "element": "土", "angle": 0}      # 北
                ]
            }
        }
        
        # 固定の方位と干支データ（React版と同じ）
        self.fixed_directions = [
            {"direction": "北東", "zodiac": "寅・丑", "angle": 45},
            {"direction": "東", "zodiac": "卯", "angle": 90},
            {"direction": "南東", "zodiac": "辰・巳", "angle": 135},
            {"direction": "南", "zodiac": "午", "angle": 180},
            {"direction": "南西", "zodiac": "未・申", "angle": 225},
            {"direction": "西", "zodiac": "酉", "angle": 270},
            {"direction": "北西", "zodiac": "亥・戌", "angle": 315},
            {"direction": "北", "zodiac": "子", "angle": 0}
        ]
        
        # 五行カラーマッピング（React版と同じ）
        self.element_colors = {
            "木": "#22C55E",  # 緑
            "火": "#EF4444",  # 赤
            "土": "#F59E0B",  # 黄
            "金": "#D4AF37",  # 金
            "水": "#3B82F6"   # 青
        }
    
    def get_element_color(self, element: str) -> str:
        """五行に基づく色を取得"""
        return self.element_colors.get(element, '#D4AF37')
    

    
    def calculate_position(self, angle: float, radius: float) -> Dict[str, float]:
        """九星気学角度をSVG角度に変換: 九星0度(北) → SVG270度(上)"""
        svg_angle = (angle + 270) % 360
        radian = (svg_angle * math.pi) / 180
        x = math.cos(radian) * radius
        y = math.sin(radian) * radius
        return {"x": x, "y": y}
    
    def get_readable_rotation(self, angle: float) -> float:
        """読みやすい回転角度を計算（React版と同じロジック）"""
        if angle > 90 and angle <= 270:
            return angle + 180
        return angle

    def save_svg_file(self, svg_content: str, center_star: str, size: int = 600) -> Dict[str, Any]:
        """
        SVGファイルを保存する
        
        Args:
            svg_content: SVGコンテンツ文字列
            center_star: 中央星名
            size: SVGサイズ
            
        Returns:
            保存結果の辞書（ファイル名、パス等）
        """
        try:
            # 保存ディレクトリを作成
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_dir = os.path.join(base_dir, 'static', 'generated_svg')
            os.makedirs(save_dir, exist_ok=True)
            
            # ファイル名を生成（タイムスタンプ付き）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'kyusei_board_{center_star}_{timestamp}.svg'
            filepath = os.path.join(save_dir, filename)
            
            # SVGファイルを保存
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            logger.info(f"SVG saved successfully: {filepath}")
            
            # ファイルパスを相対パスに変換（フロントエンド用）
            relative_path = f'/static/generated_svg/{filename}'
            
            return {
                'success': True,
                'message': 'SVGが正常に保存されました',
                'filename': filename,
                'filepath': relative_path,
                'centerStar': center_star,
                'size': size
            }
            
        except Exception as e:
            logger.error(f"Error saving SVG file: {str(e)}")
            return {
                'success': False,
                'error': f'SVGファイルの保存に失敗しました: {str(e)}'
            }

    def process_svg_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        SVGリクエストを処理する（生成または保存）
        
        Args:
            request_data: リクエストデータ
            - mode: "save" | "generate" | "auto"
            - centerStar: 中央星名
            - svgContent: SVGコンテンツ（save/autoモード時）
            - size: SVGサイズ（generate時）
            - backgroundGradient: 背景グラデーション
            
        Returns:
            処理結果の辞書
        """
        try:
            # 必須パラメータの検証
            center_star = request_data.get('centerStar')
            if not center_star:
                return {'success': False, 'error': 'centerStar は必須です'}
            
            mode = request_data.get('mode', 'auto')
            size = request_data.get('size', 600)
            background_gradient = request_data.get('backgroundGradient', 'classic')
            svg_content = request_data.get('svgContent')
            
            # モード別処理
            if mode == "generate":
                # バックエンドでSVGを生成
                generated_svg = self.generate_kyusei_board_svg(center_star, size)
                save_result = self.save_svg_file(generated_svg, center_star, size)
                # SVGコンテンツも含めて返す
                save_result['svg_content'] = generated_svg
                return save_result
                
            elif mode == "save":
                # フロントエンドからのSVGを保存
                if not svg_content:
                    return {'success': False, 'error': 'SVGコンテンツが必要です'}
                return self.save_svg_file(svg_content, center_star, size)
                
            elif mode == "auto":
                # 自動判別：SVGコンテンツがあれば保存、なければ生成
                if svg_content:
                    return self.save_svg_file(svg_content, center_star, size)
                else:
                    generated_svg = self.generate_kyusei_board_svg(center_star, size)
                    return self.save_svg_file(generated_svg, center_star, size)
            else:
                return {'success': False, 'error': f'無効なモード: {mode}'}
                
        except Exception as e:
            logger.error(f"Error processing SVG request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_kyusei_board_svg(self, center_star: str = "一白水星", size: int = 600) -> str:
        """
        React版と同じ雰囲気の九星盤SVGを生成する
        
        Args:
            center_star: 中央に配置する九星名
            size: SVGのサイズ（正方形）
            
        Returns:
            生成されたSVGコンテンツ（文字列）
        """
        current_data = self.star_configurations.get(center_star, self.star_configurations["一白水星"])
        svg_size = size
        center_x = svg_size / 2
        center_y = svg_size / 2
        
        # SVGコンテンツの生成開始
        svg_content = f'''<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Noto Sans JP', 'Inter', sans-serif;">
  <defs>
    <!-- 背景のラジアルグラデーション -->
    <radialGradient id="backgroundRadialGradient" cx="50%" cy="50%" r="70%">
      <stop offset="0%" style="stop-color:#343481;stop-opacity:1"/>
      <stop offset="50%" style="stop-color:#24245f;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:1"/>
    </radialGradient>
    
    <!-- 中央星のグラデーション -->
    <linearGradient id="centerStarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{self.get_element_color(current_data['center']['element'])};stop-opacity:1"/>
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
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.48}" fill="url(#backgroundRadialGradient)" stroke="none"/>
  
  <!-- メインボード円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.42}" 
          fill="rgba(255, 255, 255, 0.05)" stroke="rgba(135, 206, 250, 0.3)" stroke-width="1" 
          filter="url(#dropShadow)"/>
  
  <!-- 内側の円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.21}" 
          fill="none" stroke="rgba(212, 175, 55, 0.3)" stroke-width="2"/>
'''
        
        # 光の線を追加（方位境界線）
        boundary_angles = [0, 15, 75, 105, 165, 195, 255, 285, 345]
        
        for angle in boundary_angles:
            radian = (angle * math.pi) / 180
            x1 = center_x + math.cos(radian) * svg_size * 0.48
            y1 = center_y + math.sin(radian) * svg_size * 0.48
            x2 = center_x
            y2 = center_y
            
            # メインライン
            svg_content += f'''
  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" 
        stroke="url(#lightLineGradient)" stroke-width="0.5" opacity="1" filter="url(#strongGlow)"/>'''
            
            # 光の先端効果
            tip_length = svg_size * 0.48 * 0.15
            tip_x1 = center_x + math.cos(radian) * svg_size * 0.48
            tip_y1 = center_y + math.sin(radian) * svg_size * 0.48
            tip_x2 = center_x + math.cos(radian) * (svg_size * 0.48 - tip_length)
            tip_y2 = center_y + math.sin(radian) * (svg_size * 0.48 - tip_length)
            
            svg_content += f'''
  <line x1="{tip_x1:.2f}" y1="{tip_y1:.2f}" x2="{tip_x2:.2f}" y2="{tip_y2:.2f}" 
        stroke="url(#lightLineTipGradient)" stroke-width="0.2" opacity="1" filter="url(#glowFilter)"/>'''
        
        # 中央の星
        svg_content += f'''
  <circle cx="{center_x}" cy="{center_y}" r="50" 
          fill="url(#centerStarGradient)" filter="url(#dropShadow)"/>
  <text x="{center_x}" y="{center_y + 4}" text-anchor="middle" 
        font-size="{svg_size * 0.035:.2f}" font-weight="700" fill="#FFFFFF" 
        font-family="'Noto Sans JP', 'Inter', sans-serif"
        text-shadow="0 2px 4px rgba(0, 0, 0, 0.5)">
    {current_data['center']['name']}
  </text>'''
        
        # 八方位の星、干支ラベル、方位ラベルを追加
        for index, star in enumerate(current_data['positions']):
            # 八方位の星
            radius = svg_size * 0.35
            position = self.calculate_position(star['angle'], radius)
            x = center_x + position['x']
            y = center_y + position['y']
            direction_info = self.fixed_directions[index]
            star_element_color = self.get_element_color(star['element'])
            
            svg_content += f'''
  <rect x="{x - svg_size * 0.08:.2f}" y="{y - svg_size * 0.05:.2f}" 
        width="{svg_size * 0.16:.2f}" height="{svg_size * 0.1:.2f}" 
        fill="{star_element_color}" stroke="#FFA500" stroke-width="2" 
        rx="{svg_size * 0.015:.2f}" ry="{svg_size * 0.015:.2f}" filter="url(#dropShadow)"/>
  <text x="{x:.2f}" y="{y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.028:.2f}" font-weight="600" fill="#FFFFFF" 
        font-family="'Noto Sans JP', 'Inter', sans-serif"
        text-shadow="0 1px 2px rgba(0, 0, 0, 0.5)">
    {star['name']}
  </text>'''
            
            # 干支ラベル
            zodiac_radius = svg_size * 0.25
            zodiac_position = self.calculate_position(star['angle'], zodiac_radius)
            zodiac_x = center_x + zodiac_position['x']
            zodiac_y = center_y + zodiac_position['y']
            
            svg_content += f'''
  <text x="{zodiac_x:.2f}" y="{zodiac_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.025:.2f}" font-weight="500" fill="#E5E7EB" 
        font-family="'Noto Sans JP', 'Inter', sans-serif">
    {direction_info['zodiac']}
  </text>'''
            
            # 外側の方位ラベル
            direction_radius = svg_size * 0.17
            direction_position = self.calculate_position(star['angle'], direction_radius)
            direction_x = center_x + direction_position['x']
            direction_y = center_y + direction_position['y']
            
            svg_content += f'''
  <text x="{direction_x:.2f}" y="{direction_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.027:.2f}" font-weight="600" fill="#F3F4F6" 
        font-family="'Noto Sans JP', 'Inter', sans-serif">
    {direction_info['direction']}
  </text>'''
        
        svg_content += '\n</svg>'
        return svg_content

    def generate_kyusei_board_svg_pdf(self, center_star: str = "一白水星", size: int = 600) -> str:
        """
        九星盤のSVGを生成する（PDF互換版）- Step6
        WeasyPrintに対応したシンプルで確実な九星盤SVG
        
        【特殊実装】2層レイヤー構造による3段階グラデーション効果
        - WeasyPrintは複雑なグラデーションの一部stopを無視する制限がある
        - 解決策：ベース円 + オーバーレイ円の2層構造で3段階効果を実現
        
        Args:
            center_star: 中央に配置する星名
            size: SVGのサイズ（px）
            
        Returns:
            PDF互換性の高いSVGコンテンツ文字列
            
        技術詳細:
            Layer1: centerGradientBase (明るい星色→濃い赤)
            Layer2: centerGradientOverlay (中心透明→外側黒、70%透明度)
        """
        try:
            # 現在の星配置データを取得
            current_data = self.star_configurations.get(center_star, self.star_configurations["一白水星"])
            center_x = size / 2
            center_y = size / 2
            
            # PDF互換性を重視したSVGヘッダー
            svg_content = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" style="font-family: Arial, sans-serif;">
  <defs>
    <!-- シンプルな背景グラデーション -->
    <radialGradient id="bgGradient" cx="50%" cy="50%" r="60%">
      <stop offset="0%" style="stop-color:#2C3E50;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#1A1A2E;stop-opacity:1"/>
    </radialGradient>
    
         <!-- 中央星グラデーション（グラデーション範囲を小さくして自然な3段階効果） -->
     <radialGradient id="centerGradient" cx="40%" cy="40%" r="45%">
       <stop offset="0%" style="stop-color:{self.get_element_color(current_data["center"]["element"])};stop-opacity:1"/>
       <stop offset="100%" style="stop-color:#2C3E50;stop-opacity:1"/>
     </radialGradient>
  </defs>
  
  <!-- 背景円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{size * 0.47}" 
          fill="url(#bgGradient)" 
          stroke="#D4AF37" 
          stroke-width="2"/>
  
  <!-- 外枠円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{size * 0.45}" 
          fill="none" 
          stroke="#B8860B" 
          stroke-width="1"/>'''
            
            # 八方位の星とラベルを配置
            for index, star in enumerate(current_data['positions']):
                direction_info = self.fixed_directions[index]
                star_color = self.get_element_color(star['element'])
                
                # 星の位置計算
                star_radius = size * 0.32
                star_position = self.calculate_position(star['angle'], star_radius)
                star_x = center_x + star_position['x']
                star_y = center_y + star_position['y']
                
                # 星のボックス
                box_width = size * 0.14
                box_height = size * 0.08
                svg_content += f'''
  
  <!-- {star['name']} -->
  <rect x="{star_x - box_width/2:.2f}" y="{star_y - box_height/2:.2f}" 
        width="{box_width:.2f}" height="{box_height:.2f}" 
        fill="{star_color}" 
        stroke="#FFA500" 
        stroke-width="1.5" 
        rx="4" ry="4"/>
  
  <text x="{star_x:.2f}" y="{star_y + size * 0.008:.2f}" 
        text-anchor="middle" 
        font-size="{size * 0.024:.2f}" 
        font-weight="bold" 
        fill="#FFFFFF">
    {star['name']}
  </text>'''
                
                # 干支ラベル（内側）
                zodiac_radius = size * 0.22
                zodiac_position = self.calculate_position(star['angle'], zodiac_radius)
                zodiac_x = center_x + zodiac_position['x']
                zodiac_y = center_y + zodiac_position['y']
                
                svg_content += f'''
  
  <text x="{zodiac_x:.2f}" y="{zodiac_y + size * 0.006:.2f}" 
        text-anchor="middle" 
        font-size="{size * 0.020:.2f}" 
        font-weight="normal" 
        fill="#E0E0E0">
    {direction_info['zodiac']}
  </text>'''
                
                # 方位ラベル（外側）
                direction_radius = size * 0.40
                direction_position = self.calculate_position(star['angle'], direction_radius)
                direction_x = center_x + direction_position['x']
                direction_y = center_y + direction_position['y']
                
                svg_content += f'''
  
  <text x="{direction_x:.2f}" y="{direction_y + size * 0.006:.2f}" 
        text-anchor="middle" 
        font-size="{size * 0.022:.2f}" 
        font-weight="bold" 
        fill="#F0F0F0">
    {direction_info['direction']}
  </text>'''
                
                # 方位線（シンプルなライン）
                line_start_radius = size * 0.12
                line_end_radius = size * 0.44
                line_start = self.calculate_position(star['angle'], line_start_radius)
                line_end = self.calculate_position(star['angle'], line_end_radius)
                
                svg_content += f'''
  
  <line x1="{center_x + line_start['x']:.2f}" y1="{center_y + line_start['y']:.2f}" 
        x2="{center_x + line_end['x']:.2f}" y2="{center_y + line_end['y']:.2f}" 
        stroke="#B8860B" 
        stroke-width="0.8" 
        opacity="0.6"/>'''
            
            # 中央星（最後に描画してオーバーレイ効果）
            svg_content += f'''
  
  <!-- 【特殊実装】2層レイヤー構造による3段階グラデーション効果 -->
  <!-- 理由: WeasyPrintは3段階グラデーションの一部stopを無視するため -->
  
  <!-- Layer 1: ベース円（明るい星色→濃い赤、WeasyPrint確実処理） -->
  <circle cx="{center_x}" cy="{center_y}" r="{size * 0.10}" 
          fill="url(#centerGradient)" 
          stroke="#FFA500" 
          stroke-width="2"/>
  
  <text x="{center_x}" y="{center_y + size * 0.008:.2f}" 
        text-anchor="middle" 
        font-size="{size * 0.028:.2f}" 
        font-weight="bold" 
        fill="#FFFFFF">
    {current_data['center']['name']}
  </text>
  
</svg>'''
            
            logger.info(f"Generated improved PDF-compatible SVG for {center_star}, size: {size}")
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generating improved PDF-compatible SVG: {str(e)}")
            # フォールバック用の最小限SVG
            return f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{size/2}" cy="{size/2}" r="{size * 0.4}" fill="#2C3E50" stroke="#D4AF37" stroke-width="2"/>
  <text x="{size/2}" y="{size/2}" text-anchor="middle" font-size="{size * 0.05}" fill="#FFFFFF">{center_star}</text>
</svg>'''

    def generate_kyusei_board_svg_enhanced_pdf(self, center_star: str = "一白水星", size: int = 600) -> str:
        """
        九星盤のSVGを生成する（強化PDF互換版）
        添付画像レベルの品質を保ちつつWeasyPrint対応
        """
        try:
            current_data = self.star_configurations.get(center_star, self.star_configurations["一白水星"])
            svg_size = size
            center_x = svg_size / 2
            center_y = svg_size / 2
            
            # WeasyPrint対応の美しいSVG（フィルターを除去、基本グラデーションは保持）
            svg_content = f'''<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg" style="font-family: Arial, sans-serif;">
  <defs>
    <!-- 背景のラジアルグラデーション（WeasyPrint対応） -->
    <radialGradient id="backgroundRadialGradient" cx="50%" cy="50%" r="70%">
      <stop offset="0%" style="stop-color:#343481;stop-opacity:1"/>
      <stop offset="50%" style="stop-color:#24245f;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:1"/>
    </radialGradient>
    
    <!-- 中央星のグラデーション -->
    <linearGradient id="centerStarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{self.get_element_color(current_data['center']['element'])};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#FFA500;stop-opacity:1"/>
    </linearGradient>
    
    <!-- 光の線のシンプルグラデーション -->
    <linearGradient id="lightLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
      <stop offset="20%" style="stop-color:rgba(212,175,55,0.3);stop-opacity:1"/>
      <stop offset="50%" style="stop-color:rgba(212,175,55,0.6);stop-opacity:1"/>
      <stop offset="80%" style="stop-color:rgba(212,175,55,0.3);stop-opacity:1"/>
      <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
    </linearGradient>
  </defs>
  
  <!-- 背景円（ラジアルグラデーション） -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.48}" fill="url(#backgroundRadialGradient)" stroke="none"/>
  
  <!-- メインボード円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.42}" 
          fill="rgba(255, 255, 255, 0.05)" stroke="rgba(135, 206, 250, 0.3)" stroke-width="1"/>
  
  <!-- 内側の円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.21}" 
          fill="none" stroke="rgba(212, 175, 55, 0.3)" stroke-width="2"/>'''
            
            # 光の線を追加（フィルター無しで方位境界線）
            boundary_angles = [0, 15, 75, 105, 165, 195, 255, 285, 345]
            
            for angle in boundary_angles:
                radian = (angle * math.pi) / 180
                x1 = center_x + math.cos(radian) * svg_size * 0.48
                y1 = center_y + math.sin(radian) * svg_size * 0.48
                x2 = center_x
                y2 = center_y
                
                svg_content += f'''
  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" 
        stroke="url(#lightLineGradient)" stroke-width="0.5" opacity="1"/>'''
            
            # 中央の星
            svg_content += f'''
  
  <!-- 中央星 -->
  <circle cx="{center_x}" cy="{center_y}" r="50" 
          fill="url(#centerStarGradient)" stroke="#FFA500" stroke-width="2"/>
  <text x="{center_x}" y="{center_y + 4}" text-anchor="middle" 
        font-size="{svg_size * 0.035:.2f}" font-weight="bold" fill="#FFFFFF">
    {current_data['center']['name']}
  </text>'''
            
            # 八方位の星、干支ラベル、方位ラベルを追加
            for index, star in enumerate(current_data['positions']):
                radius = svg_size * 0.35
                position = self.calculate_position(star['angle'], radius)
                x = center_x + position['x']
                y = center_y + position['y']
                direction_info = self.fixed_directions[index]
                star_element_color = self.get_element_color(star['element'])
                
                svg_content += f'''
  
  <!-- {star['name']} -->
  <rect x="{x - svg_size * 0.08:.2f}" y="{y - svg_size * 0.05:.2f}" 
        width="{svg_size * 0.16:.2f}" height="{svg_size * 0.1:.2f}" 
        fill="{star_element_color}" stroke="#FFA500" stroke-width="2" 
        rx="{svg_size * 0.015:.2f}" ry="{svg_size * 0.015:.2f}"/>
  <text x="{x:.2f}" y="{y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.028:.2f}" font-weight="bold" fill="#FFFFFF">
    {star['name']}
  </text>'''
                
                # 干支ラベル
                zodiac_radius = svg_size * 0.25
                zodiac_position = self.calculate_position(star['angle'], zodiac_radius)
                zodiac_x = center_x + zodiac_position['x']
                zodiac_y = center_y + zodiac_position['y']
                
                svg_content += f'''
  
  <text x="{zodiac_x:.2f}" y="{zodiac_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.025:.2f}" font-weight="normal" fill="#E5E7EB">
    {direction_info['zodiac']}
  </text>'''
                
                # 外側の方位ラベル
                direction_radius = svg_size * 0.17
                direction_position = self.calculate_position(star['angle'], direction_radius)
                direction_x = center_x + direction_position['x']
                direction_y = center_y + direction_position['y']
                
                svg_content += f'''
  
  <text x="{direction_x:.2f}" y="{direction_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.027:.2f}" font-weight="bold" fill="#F3F4F6">
    {direction_info['direction']}
  </text>'''
            
            svg_content += '\n</svg>'
            logger.info(f"Generated enhanced PDF-compatible SVG for {center_star}, size: {size}")
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced PDF-compatible SVG: {str(e)}")
            return self.generate_kyusei_board_svg_pdf(center_star, size)  # フォールバック 

    def generate_kyusei_board_svg_step9_pdf(self, center_star: str = "一白水星", size: int = 600) -> str:
        """
        九星盤のSVGを生成する（Step9: React版Step1ベース + PDF互換版）
        フロントエンドのReact版Step1の美しいデザインをそのまま移植し、PDF対応のみ適用
        
        【変更点】
        - ベース: フロントエンドReact版Step1の完全移植
        - PDF対応: フィルター除去、フォント変更のみ
        - 保持: 全ての配置、回転、グラデーション、光エフェクト
        
        Args:
            center_star: 中央に配置する星名
            size: SVGのサイズ（px）
            
        Returns:
            React版Step1品質 + PDF互換性のSVGコンテンツ文字列
        """
        try:
            current_data = self.star_configurations.get(center_star, self.star_configurations["一白水星"])
            svg_size = size
            center_x = svg_size / 2
            center_y = svg_size / 2
            
            # React版Step1の完全移植（フォント変更のみ）
            svg_content = f'''<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg" style="font-family: Arial, sans-serif;">
  <defs>
    <!-- 背景グラデーション（Step6成功手法: 45%範囲縮小） -->
    <radialGradient id="luxuryBackground" cx="50%" cy="50%" r="45%">
      <stop offset="0%" style="stop-color:#343481;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#1A1A2E;stop-opacity:1"/>
    </radialGradient>
    
    <!-- 中央星グラデーション（Step6成功手法: 45%範囲縮小で確実な3段階効果） -->
    <radialGradient id="centerStarGradient" cx="40%" cy="40%" r="45%">
      <stop offset="0%" style="stop-color:{self.get_element_color(current_data['center']['element'])};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#2C3E50;stop-opacity:1"/>
    </radialGradient>
    
    <!-- 光る境界線グラデーション（Step6成功手法: 45%範囲縮小） -->
    <radialGradient id="glowBorder" cx="50%" cy="50%" r="45%">
      <stop offset="0%" style="stop-color:rgba(135,206,250,0.8);stop-opacity:1"/>
      <stop offset="100%" style="stop-color:rgba(135,206,250,0.2);stop-opacity:1"/>
    </radialGradient>'''
            
            # 各五行の要素グラデーション定義（Step6成功手法: 45%範囲縮小）
            for element in ["木", "火", "土", "金", "水"]:
                element_color = self.get_element_color(element)
                svg_content += f'''
    
    <!-- {element}星用グラデーション（Step6成功手法: 矩形用に更に縮小） -->
    <radialGradient id="elementGradient{element}" cx="50%" cy="50%" r="30%">
      <stop offset="0%" style="stop-color:{element_color};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#2C3E50;stop-opacity:1"/>
    </radialGradient>'''
            
            svg_content += f'''
    
    <!-- 光の境界線用グラデーション（Step6成功手法: シンプル化） -->
    <linearGradient id="boundaryLightGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
      <stop offset="50%" style="stop-color:rgba(212,175,55,0.6);stop-opacity:1"/>
      <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
    </linearGradient>
    
    <!-- 光の外側エフェクト用グラデーション（Step6成功手法: シンプル化） -->
    <linearGradient id="outerGlowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
      <stop offset="50%" style="stop-color:rgba(135,206,250,0.1);stop-opacity:1"/>
      <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
    </linearGradient>
    
    <!-- PDF対応: フィルターは除去 -->
  </defs>

  <!-- メイン背景円 (React版のbackdrop-filter効果を再現) -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.45}" 
          fill="url(#luxuryBackground)" 
          stroke="url(#glowBorder)" 
          stroke-width="2"
          opacity="0.95"/>
  
  <!-- インナーリング (React版の方位リング) -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.35}" 
          fill="none" 
          stroke="rgba(212,175,55,0.4)" 
          stroke-width="1.5"
          opacity="0.7"/>'''
            
            # 光る方位境界線（React版と同じ）
            boundary_angles = [15, 75, 105, 165, 195, 255, 285, 345]
            for angle in boundary_angles:
                end_radius = svg_size * 0.45
                start_radius = svg_size * 0.08
                radian = (angle * math.pi) / 180
                start_x = center_x + math.cos(radian) * start_radius
                start_y = center_y + math.sin(radian) * start_radius
                end_x = center_x + math.cos(radian) * end_radius
                end_y = center_y + math.sin(radian) * end_radius
                
                svg_content += f'''
        
  <!-- 外側の薄い光 -->
  <line x1="{start_x:.2f}" y1="{start_y:.2f}" x2="{end_x:.2f}" y2="{end_y:.2f}" 
        stroke="url(#outerGlowGradient)" 
        stroke-width="2" 
        opacity="0.4"/>
        
  <!-- メインの光の線 -->
  <line x1="{start_x:.2f}" y1="{start_y:.2f}" x2="{end_x:.2f}" y2="{end_y:.2f}" 
        stroke="url(#boundaryLightGradient)" 
        stroke-width="1" 
        opacity="0.6"/>
        
  <!-- 中心の鋭い光 -->
  <line x1="{start_x:.2f}" y1="{start_y:.2f}" x2="{end_x:.2f}" y2="{end_y:.2f}" 
        stroke="rgba(212,175,55,0.7)" 
        stroke-width="0.3" 
        opacity="0.8"/>'''
            
            # 中央星（React版と同じ）
            svg_content += f'''

  <!-- 中央星 (React版の立体効果を再現) -->
  <circle cx="{center_x}" cy="{center_y}" r="{size * 0.08}" 
          fill="url(#centerStarGradient)" 
          stroke="rgba(255,255,255,0.3)" 
          stroke-width="2"/>
  
  <!-- 中央星のテキスト -->
  <text x="{center_x}" y="{center_y}" 
        text-anchor="middle" 
        dominant-baseline="middle" 
        font-size="{size * 0.0276:.2f}" 
        font-weight="bold" 
        fill="#1A1A3E"
        font-family="Arial, sans-serif">
    {current_data['center']['name']}
  </text>'''
            
            # React版と同じ方位計算ロジック
            def get_readable_rotation(angle: float) -> float:
                if angle > 90 and angle <= 270:
                    return angle + 180
                return angle
                
            # 八方位の星（React版の完全移植）
            for index, star in enumerate(current_data['positions']):
                radius = size * 0.35
                position = self.calculate_position(star['angle'], radius)
                star_x = center_x + position['x']
                star_y = center_y + position['y']
                readable_angle = get_readable_rotation(star['angle'])
                
                # 星の背景矩形
                rect_width = size * 0.14
                rect_height = size * 0.1
                
                # 東西方向（90度、270度）のみ縦書きにする
                is_east_west = star['angle'] == 90 or star['angle'] == 270
                
                svg_content += f'''
        
  <!-- 星のグループ (ボックスとテキストを一緒に回転) -->
  <g transform="translate({star_x:.2f}, {star_y:.2f}) rotate({readable_angle})">
    <!-- 星の背景 (React版のblur効果を再現) -->
    <rect x="{-rect_width/2:.2f}" y="{-rect_height/2:.2f}" 
          width="{rect_width:.2f}" height="{rect_height:.2f}" 
          rx="{size * 0.02:.2f}" 
          fill="url(#elementGradient{star['element']})"
          stroke="url(#glowBorder)" 
          stroke-width="1"
          opacity="0.9"/>'''
                
                if is_east_west:
                    # 縦書きテキスト（東西のみ）
                    svg_content += f'''
          
    <!-- 縦書きテキスト（東西のみ、回転を打ち消して常に上から下に読める） -->
    <g transform="rotate({-readable_angle})">
      <text text-anchor="middle" 
            font-size="{size * 0.0264:.2f}" 
            font-weight="600" 
            fill="#F9FAFB"
            font-family="Arial, sans-serif">'''
                    
                    for i, char in enumerate(star['name']):
                        y_pos = (i - 1.5) * size * 0.03 + size * 0.01
                        svg_content += f'''
        <tspan x="0" y="{y_pos:.2f}">{char}</tspan>'''
                    
                    svg_content += '''
      </text>
    </g>'''
                else:
                    # 横書きテキスト（その他の方向）
                    svg_content += f'''
          
    <!-- 横書きテキスト（その他の方向） -->
    <text x="0" y="{-size * 0.01:.2f}" 
          text-anchor="middle" 
          dominant-baseline="middle" 
          font-size="{size * 0.0264:.2f}" 
          font-weight="600" 
          fill="#F9FAFB"
          font-family="Arial, sans-serif">
      {star['name']}
    </text>'''
                
                svg_content += '''
  </g>'''
            
            # 方位・干支ラベル（React版と同じ）
            for index, star in enumerate(current_data['positions']):
                direction_radius = size * 0.17
                zodiac_radius = size * 0.25
                direction_pos = self.calculate_position(star['angle'], direction_radius)
                zodiac_pos = self.calculate_position(star['angle'], zodiac_radius)
                direction_info = self.fixed_directions[index]
                readable_angle = get_readable_rotation(star['angle'])
                
                # 東西方向（90度、270度）は回転させない
                should_rotate = star['angle'] != 90 and star['angle'] != 270
                rotation_transform = f'transform="rotate({readable_angle} {center_x + direction_pos["x"]:.2f} {center_y + direction_pos["y"]:.2f})"' if should_rotate else ''
                zodiac_rotation_transform = f'transform="rotate({readable_angle} {center_x + zodiac_pos["x"]:.2f} {center_y + zodiac_pos["y"]:.2f})"' if should_rotate else ''
                
                svg_content += f'''
        
  <!-- 方位ラベル -->
  <text x="{center_x + direction_pos['x']:.2f}" y="{center_y + direction_pos['y']:.2f}" 
        text-anchor="middle" 
        dominant-baseline="middle" 
        font-size="{size * 0.0276:.2f}" 
        font-weight="600" 
        fill="#F3F4F6"
        font-family="Arial, sans-serif"
        {rotation_transform}>
    {direction_info['direction']}
  </text>
  
  <!-- 干支ラベル -->
  <text x="{center_x + zodiac_pos['x']:.2f}" y="{center_y + zodiac_pos['y']:.2f}" 
        text-anchor="middle" 
        dominant-baseline="middle" 
        font-size="{size * 0.0216:.2f}" 
        font-weight="500" 
        fill="#E5E7EB"
        font-family="Arial, sans-serif"
        {zodiac_rotation_transform}>
    {direction_info['zodiac']}
  </text>'''
            
            svg_content += '''
</svg>'''
            
            logger.info(f"Generated Step9 (React Step1-based PDF-compatible) SVG for {center_star}, size: {size}")
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generating Step9 SVG: {str(e)}")
            return self.generate_kyusei_board_svg_pdf(center_star, size)  # フォールバック

    def generate_kyusei_board_svg_enhanced_pdf(self, center_star: str = "一白水星", size: int = 600) -> str:
        """
        九星盤のSVGを生成する（強化PDF互換版）
        添付画像レベルの品質を保ちつつWeasyPrint対応
        """
        try:
            current_data = self.star_configurations.get(center_star, self.star_configurations["一白水星"])
            svg_size = size
            center_x = svg_size / 2
            center_y = svg_size / 2
            
            # WeasyPrint対応の美しいSVG（フィルターを除去、基本グラデーションは保持）
            svg_content = f'''<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg" style="font-family: Arial, sans-serif;">
  <defs>
    <!-- 背景のラジアルグラデーション（WeasyPrint対応） -->
    <radialGradient id="backgroundRadialGradient" cx="50%" cy="50%" r="70%">
      <stop offset="0%" style="stop-color:#343481;stop-opacity:1"/>
      <stop offset="50%" style="stop-color:#24245f;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#2D1B69;stop-opacity:1"/>
    </radialGradient>
    
    <!-- 中央星のグラデーション -->
    <linearGradient id="centerStarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{self.get_element_color(current_data['center']['element'])};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#FFA500;stop-opacity:1"/>
    </linearGradient>
    
    <!-- 光の線のシンプルグラデーション -->
    <linearGradient id="lightLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:transparent;stop-opacity:0"/>
      <stop offset="20%" style="stop-color:rgba(212,175,55,0.3);stop-opacity:1"/>
      <stop offset="50%" style="stop-color:rgba(212,175,55,0.6);stop-opacity:1"/>
      <stop offset="80%" style="stop-color:rgba(212,175,55,0.3);stop-opacity:1"/>
      <stop offset="100%" style="stop-color:transparent;stop-opacity:0"/>
    </linearGradient>
  </defs>
  
  <!-- 背景円（ラジアルグラデーション） -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.48}" fill="url(#backgroundRadialGradient)" stroke="none"/>
  
  <!-- メインボード円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.42}" 
          fill="rgba(255, 255, 255, 0.05)" stroke="rgba(135, 206, 250, 0.3)" stroke-width="1"/>
  
  <!-- 内側の円 -->
  <circle cx="{center_x}" cy="{center_y}" r="{svg_size * 0.21}" 
          fill="none" stroke="rgba(212, 175, 55, 0.3)" stroke-width="2"/>'''
            
            # 光の線を追加（フィルター無しで方位境界線）
            boundary_angles = [0, 15, 75, 105, 165, 195, 255, 285, 345]
            
            for angle in boundary_angles:
                radian = (angle * math.pi) / 180
                x1 = center_x + math.cos(radian) * svg_size * 0.48
                y1 = center_y + math.sin(radian) * svg_size * 0.48
                x2 = center_x
                y2 = center_y
                
                svg_content += f'''
  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" 
        stroke="url(#lightLineGradient)" stroke-width="0.5" opacity="1"/>'''
            
            # 中央の星
            svg_content += f'''
  
  <!-- 中央星 -->
  <circle cx="{center_x}" cy="{center_y}" r="50" 
          fill="url(#centerStarGradient)" stroke="#FFA500" stroke-width="2"/>
  <text x="{center_x}" y="{center_y + 4}" text-anchor="middle" 
        font-size="{svg_size * 0.035:.2f}" font-weight="bold" fill="#FFFFFF">
    {current_data['center']['name']}
  </text>'''
            
            # 八方位の星、干支ラベル、方位ラベルを追加
            for index, star in enumerate(current_data['positions']):
                radius = svg_size * 0.35
                position = self.calculate_position(star['angle'], radius)
                x = center_x + position['x']
                y = center_y + position['y']
                direction_info = self.fixed_directions[index]
                star_element_color = self.get_element_color(star['element'])
                
                svg_content += f'''
  
  <!-- {star['name']} -->
  <rect x="{x - svg_size * 0.08:.2f}" y="{y - svg_size * 0.05:.2f}" 
        width="{svg_size * 0.16:.2f}" height="{svg_size * 0.1:.2f}" 
        fill="{star_element_color}" stroke="#FFA500" stroke-width="2" 
        rx="{svg_size * 0.015:.2f}" ry="{svg_size * 0.015:.2f}"/>
  <text x="{x:.2f}" y="{y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.028:.2f}" font-weight="bold" fill="#FFFFFF">
    {star['name']}
  </text>'''
                
                # 干支ラベル
                zodiac_radius = svg_size * 0.25
                zodiac_position = self.calculate_position(star['angle'], zodiac_radius)
                zodiac_x = center_x + zodiac_position['x']
                zodiac_y = center_y + zodiac_position['y']
                
                svg_content += f'''
  
  <text x="{zodiac_x:.2f}" y="{zodiac_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.025:.2f}" font-weight="normal" fill="#E5E7EB">
    {direction_info['zodiac']}
  </text>'''
                
                # 外側の方位ラベル
                direction_radius = svg_size * 0.17
                direction_position = self.calculate_position(star['angle'], direction_radius)
                direction_x = center_x + direction_position['x']
                direction_y = center_y + direction_position['y']
                
                svg_content += f'''
  
  <text x="{direction_x:.2f}" y="{direction_y + 4:.2f}" text-anchor="middle" 
        font-size="{svg_size * 0.027:.2f}" font-weight="bold" fill="#F3F4F6">
    {direction_info['direction']}
  </text>'''
            
            svg_content += '\n</svg>'
            logger.info(f"Generated enhanced PDF-compatible SVG for {center_star}, size: {size}")
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generating enhanced PDF-compatible SVG: {str(e)}")
            return self.generate_kyusei_board_svg_pdf(center_star, size)  # フォールバック 