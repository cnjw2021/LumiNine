"""Nine Star Ki PDF生成用のスタイリングサービス"""

import os
from core.utils.logger import get_logger

logger = get_logger(__name__)

class PdfStylingService:
    """Nine Star Ki PDF生成用のスタイリングを管理するクラス"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def get_base_css_string(self) -> str:
        """基本CSSスタイルを取得する
        
        Returns:
            str: 基本CSSスタイル
        """
        return """
            @page {
                size: 210mm 297mm;
                margin: 0;
                padding: 0;
            }
            
            @font-face {
                font-family: 'IPAexGothic';
                src: url('fonts/ipaexg.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            
            @font-face {
                font-family: 'IPAexMincho';
                src: url('fonts/ipaexm.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            
            body {
                font-family: 'IPAexGothic', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                margin: 0;
                padding: 0;
                background-color: white;
            }
            
            .content {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            
            h1 {
                color: #3490dc;
                text-align: center;
            }
            
            h2 {
                color: #333;
                margin-top: 20px;
            }
            
            /* 星の色 */
            .color-1 { color: #3490dc !important; }  /* 一白水星 - 鮮やかな青 */
            .color-2 { color: #2d3748 !important; }  /* 二黒土星 - 深い黒 */
            .color-3 { color: #38a169 !important; }  /* 三碧木星 - 爽やかな緑 */
            .color-4 { color: #319795 !important; }  /* 四緑木星 - ティール */
            .color-5 { color: #ecc94b !important; }  /* 五黄土星 - 黄金色 */
            .color-6 { color: #a0aec0 !important; }  /* 六白金星 - シルバー */
            .color-7 { color: #e53e3e !important; }  /* 七赤金星 - 情熱的な赤 */
            .color-8 { color: #805ad5 !important; }  /* 八白土星 - 神秘的な紫 */
            .color-9 { color: #ed64a6 !important; }  /* 九紫火星 - 鮮やかなピンク */

            /* 五行の色 */
            .element-金 { color: #d4af37 !important; }
            .element-木 { color: #228b22 !important; }
            .element-水 { color: #1e90ff !important; }
            .element-火 { color: #ff4500 !important; }
            .element-土 { color: #8b4513 !important; }
            
            /* SVG星のサイズ設定 */
            .star-svg {
                width: 150px;
                height: 150px;
                display: block;
                margin: 0 auto;
            }
        """
    
    def get_fortune_styles_css_path(self) -> str:
        """運気スタイルCSSファイルのパスを取得する
        
        Returns:
            str: CSSファイルのパス
        """
        return os.path.join(
            self.base_dir,
            'apps',
            'ninestarki',
            'templates',
            'ninestarkey_report',
            'css',
            'fortune_styles.css'
        )
    
    def load_fortune_styles_css(self) -> str:
        """運気スタイルCSSファイルの内容を読み込む
        
        Returns:
            str: CSSファイルの内容
        """
        css_file_path = self.get_fortune_styles_css_path()
        css_content = ''
        
        if os.path.exists(css_file_path):
            try:
                with open(css_file_path, 'r', encoding='utf-8') as css_file:
                    css_content = css_file.read()
                logger.info(f"CSS file content loaded: {len(css_content)} bytes")
            except Exception as e:
                logger.error(f"Error reading CSS file: {str(e)}")
        else:
            logger.warning(f"CSS file not found at: {css_file_path}")
        
        return css_content
