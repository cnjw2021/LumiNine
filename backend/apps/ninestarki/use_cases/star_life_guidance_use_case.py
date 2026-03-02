from typing import List, Dict, Any, Optional
from injector import inject
from apps.ninestarki.domain.entities.star_life_guidance import StarLifeGuidance, CategoryEnum
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from core.utils.logger import get_logger

logger = get_logger(__name__)

class StarLifeGuidanceUseCase:
    """星と人生のガイダンス情報のビジネスロジックを担当するユースケースクラス"""

    @inject
    def __init__(self, star_life_guidance_repo: IStarLifeGuidanceRepository):
        """
        コンストラクタを通じてリポジトリの実装オブジェクトを自動的に注入します
        """
        self.star_life_guidance_repo = star_life_guidance_repo

    def get_star_life_guidance(self, main_star: int, month_star: int) -> Dict[str, Any]:
        """本命星と月命星から星と人生のガイダンス情報を取得する"""
        logger.info(f"Getting star life guidance for main_star={main_star}, month_star={month_star}")
        
        try:
            # 本命星と月命星でガイダンス情報を取得
            guidance_list = self.star_life_guidance_repo.find_by_stars(main_star, month_star)
            
            if not guidance_list:
                logger.warning(f"No guidance found for main_star={main_star}, month_star={month_star}")
                return {
                    'main_star': main_star,
                    'month_star': month_star,
                    'guidance': []
                }
            
            # カテゴリ別に整理して従来の形式に変換
            result = {
                'main_star': main_star,
                'month_star': month_star,
                'job': None,
                'lucky_color': None,
                'lucky_item': None
            }
            
            # TODO: lucky_color, luckey_item は画面に表示してない。削除？？
            for guidance in guidance_list:
                category = guidance.category.value if guidance.category else 'unknown'
                if category == 'job':
                    result['job'] = guidance.content
                elif category == 'lucky_color':
                    result['lucky_color'] = guidance.content
                elif category == 'lucky_item':
                    result['lucky_item'] = guidance.content
            
            logger.info(f"Found {len(guidance_list)} guidance items for main_star={main_star}, month_star={month_star}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting star life guidance: {e}")
            raise Exception(f"星と人生のガイダンス情報の取得に失敗しました: {str(e)}")

    # TODO: category 使われてる？？？
    def get_guidance_by_category(self, main_star: int, month_star: int, category: str) -> Optional[Dict[str, Any]]:
        """特定のカテゴリのガイダンス情報を取得する"""
        logger.info(f"Getting guidance for category={category}, main_star={main_star}, month_star={month_star}")
        
        try:
            # カテゴリをEnumに変換
            try:
                category_enum = CategoryEnum(category)
            except ValueError:
                logger.error(f"Invalid category: {category}")
                return None
            
            guidance = self.star_life_guidance_repo.find_by_stars_and_category(main_star, month_star, category_enum)
            
            if not guidance:
                logger.warning(f"No guidance found for category={category}, main_star={main_star}, month_star={month_star}")
                return None
            
            return guidance.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting guidance by category: {e}")
            raise Exception(f"カテゴリ別ガイダンス情報の取得に失敗しました: {str(e)}")
