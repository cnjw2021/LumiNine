import os
from datetime import datetime
from typing import Dict, Any, List
from flask import render_template
from core.utils.logger import get_logger
from apps.ninestarki.constants.template_styles import TEMPLATE_STYLES
from apps.ninestarki.infrastructure.pdf.image_data_url_converter import ImageDataUrlConverter
from apps.ninestarki.infrastructure.pdf.pdf_styling_service import PdfStylingService
from apps.ninestarki.use_cases.dto.report_dtos import ReportContextDTO

logger = get_logger(__name__)

class NineStarKiHtmlRenderer:
    """
    受け取ったデータ(context)を使用してHTMLをレンダリングするだけの役割を担います。
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.image_converter = ImageDataUrlConverter(base_dir=self.base_dir)
        self.styling_service = PdfStylingService(base_dir=self.base_dir)

    def render(self, context: ReportContextDTO) -> str:
        """
        UseCaseからすべての計算を完了したデータ(context)を受け取り、最終的なHTMLをレンダリングします。
        """
        logger.info(f"HTML rendering started for {context['user_info'].get('full_name')}")

        auspicious_day_result = context.get("auspicious_day_result")
        if isinstance(auspicious_day_result, dict):
            moving_table = auspicious_day_result.get('moving_table') or []
            water_drawing_table = auspicious_day_result.get('water_drawing_table') or []
        else:
            logger.warning("auspicious_day_result は dict 形式ではありません。")
            moving_table = []
            water_drawing_table = []

        direction_images = {
            'achikochi_map': self.image_converter.get_direction_image_data_url('achikochi_map.png'),
            'ninestarki_30_60': self.image_converter.get_direction_image_data_url('ninestarki_30_60.png'),
        }

        # 五行情報
        five_elements_image = self.image_converter.get_five_elements_image_data_url()

        # ユーザー情報
        user_info = context.get('user_info', {})
        full_name = user_info.get('full_name', '')
        birthdate = user_info.get('birthdate', '')

        # テンプレートに渡す最終データオブジェクト(final_context)を完成させる
        final_context = {
            **context, # UseCaseから受け取ったすべてのデータをそのまま渡す
            "result": context.get("ninestar_info", {}),
            "target_year": user_info.get('target_year', datetime.now().year),
            "full_name": full_name,
            "birthdate": birthdate,
            "moving_table": moving_table,
            "water_drawing_table": water_drawing_table,
            "style": TEMPLATE_STYLES.get(context.get('template_id', 1)),
            "css_content": self.styling_service.load_fortune_styles_css(),
            "static_base_url": "/static",
            "image_path": self.image_converter.get_background_image_data_url(context.get('background_id', 1)),
            "direction_images": direction_images,
            "five_elements_image": five_elements_image,
        }
        
        try:
            use_pdf_svg = context.get('use_pdf_svg', False)
            use_simple = context.get('use_simple', False)
            if use_pdf_svg:
                # PDF向け: 元SVGをPNG化して埋め込み（フィルタ/グラデ対応）
                final_context["svg_by_center"] = {
                    i: self.image_converter.get_svg_png_data_url(i, use_simple) for i in range(1, 10)
                }
            else:
                final_context["svg_by_center"] = {
                    i: self.image_converter.get_svg_data_url(i, use_simple) for i in range(1, 10)
                }
        except Exception:
            final_context["svg_by_center"] = {}
        
        return render_template('ninestarkey_report/base.html', **final_context)
    