"""Star Life Guidance service module."""

from injector import inject
from core.utils.logger import get_logger
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from apps.ninestarki.domain.entities.star_life_guidance import CategoryEnum
import traceback

logger = get_logger(__name__)

class StarLifeGuidanceService:
    """Service class for Star Life Guidance."""
    
    @inject
    def __init__(self, repository: IStarLifeGuidanceRepository):
        """コンストラクタを通じてUseCaseを注入します"""
        self.repository = repository
    
    def get_star_life_guidance(self, main_star, month_star) -> dict:
        """本命星（と月命星）に基づいた適職情報を取得する

        Args:
            main_star (int): 本命星番号
            month_star (int): 月命星番号

        Returns:
            dict: {'job': str|None, 'lucky_item': str|None}
        """
        try:
            logger.info(f"Fetching star life guidance for main_star: {main_star}")
            
            # main_star/month_starを整数に
            try:
                main_star_num = int(main_star)
                month_star_num = int(month_star)
            except (TypeError, ValueError):
                logger.warning(f"Invalid star number. main_star: {main_star}, month_star: {month_star}")
                return {'job': None, 'lucky_item': None}
            
            # レポジトリから複数行を取得
            rows = self.repository.find_by_stars(main_star_num, month_star_num)
            if not rows:
                logger.warning(f"No guidance found for main_star: {main_star_num}, month_star: {month_star_num}")
                return {'job': None, 'lucky_item': None}
            
            result = {'job': None, 'lucky_item': None}
            for r in rows:
                try:
                    if r.category == CategoryEnum.job and not result['job']:
                        result['job'] = r.content
                    elif r.category == CategoryEnum.lucky_item and not result['lucky_item']:
                        result['lucky_item'] = r.content
                except Exception:
                    # カテゴリ値が文字列で保存されている場合のフォールバック
                    cat_value = getattr(r.category, 'value', r.category)
                    if cat_value == 'job' and not result['job']:
                        result['job'] = r.content
                    elif cat_value == 'lucky_item' and not result['lucky_item']:
                        result['lucky_item'] = r.content
            
            return result
            
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error fetching star life guidance: {str(e)}\n{error_detail}")
            return {'job': None, 'lucky_item': None}
