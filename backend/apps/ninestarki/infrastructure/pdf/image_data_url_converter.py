import os
import base64
from typing import Optional
from core.utils.logger import get_logger

logger = get_logger(__name__)

class ImageDataUrlConverter:
    """
    PDF 생성에 필요한 이미지 파일을 데이터 URL 형식으로 변환하는 클래스.
    """
    
    def __init__(self, base_dir: str):
        """
        [수정]
        생성자를 통해 프로젝트의 루트 경로(base_dir)를 주입받습니다.
        """
        self.base_dir = base_dir
        # 이미지 파일이 위치한 static 폴더의 절대 경로를 미리 만들어 둡니다.
        self.static_dir = os.path.join(self.base_dir, "apps", "ninestarki", "static")

    def _convert_image_to_data_url(self, file_path: str, image_type: str) -> str:
        """파일 경로를 받아 데이터 URL로 변환하고, 파일이 없을 경우 경고를 로깅합니다."""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"이미지 파일을 찾을 수 없습니다: {file_path}")
                return ""
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/{image_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"이미지 변환 중 오류 발생 {file_path}: {e}")
            return ""

    def get_svg_data_url(self, star_number: int, use_simple: bool = False) -> str:
        """SVG 이미지를 데이터 URL 형식으로 변환합니다."""
        subfolder = "simple" if use_simple else ""
        file_path = os.path.join(self.static_dir, "images", "main_star", subfolder, f"{star_number}.svg")
        return self._convert_image_to_data_url(file_path, "svg+xml")

    def get_svg_png_data_url(self, star_number: int, use_simple: bool = False, size: Optional[int] = 600) -> str:
        """사전 생성된 PNG를 데이터 URL 형식으로 변환합니다 (PDF用)."""
        subfolder = "simple" if use_simple else ""
        png_path = os.path.join(self.static_dir, "images", "main_star_png", subfolder, f"{star_number}.png")
        if not os.path.exists(png_path):
            # PNG가 없으면 SVG로 폴백 (개발 중 안전장치)
            logger.warning(f"PNG 파일을 찾을 수 없습니다(폴백 SVG): {png_path}")
            return self.get_svg_data_url(star_number, use_simple)
        try:
            with open(png_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            logger.error(f"PNG 변환 중 오류 발생 {png_path}: {e}")
            return ""

    def get_direction_image_data_url(self, image_name: str) -> str:
        """방위 이미지를 데이터 URL 형식으로 변환합니다."""
        file_path = os.path.join(self.static_dir, "images", "directions", image_name)
        image_ext = os.path.splitext(image_name)[1].lstrip('.')
        return self._convert_image_to_data_url(file_path, image_ext)

    def get_five_elements_image_data_url(self) -> str:
        """오행 상생도 이미지를 데이터 URL 형식으로 변환합니다."""
        file_path = os.path.join(self.static_dir, "images", "five_elements", "five_elements.png")
        return self._convert_image_to_data_url(file_path, "png")

    def get_background_image_data_url(self, background_id: int) -> str:
        """배경 이미지를 데이터 URL 형식으로 변환합니다."""
        background_image = f'certificate_template{background_id}.png'
        file_path = os.path.join(self.static_dir, "images", "background", background_image)
        return self._convert_image_to_data_url(file_path, "png")