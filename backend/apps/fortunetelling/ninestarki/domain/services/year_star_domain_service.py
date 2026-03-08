from datetime import timedelta
from typing import List, Optional
from injector import inject

from apps.fortunetelling.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.fortunetelling.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.fortunetelling.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.fortunetelling.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from core.utils.logger import get_logger

logger = get_logger(__name__)

class YearStarDomainService:
    """
    年の中宮(九星盤の中央の星)とそれに関連する情報を扱うドメインサービス.
    """
    @inject
    def __init__(self, nine_star_repo: INineStarRepository, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository):
        self.nine_star_repo = nine_star_repo
        self.solar_terms_repo = solar_terms_repo
        self.solar_starts_repo = solar_starts_repo
        self.star_grid_repo = star_grid_repo

    def get_year_star_info(self, target_year: int) -> Optional[dict]:
        """
        指定された年の中宮情報を取得します.

        solar_starts_data に star_number と zodiac が事前構築済みのため
        数式再計算なしに直接 DB 参照します.
        """
        try:
            # solar_starts_data から連番 中宮星 + 連干支を直接取得
            starts_row = self.solar_starts_repo.get_by_year(target_year)
            if not starts_row:
                logger.warning("solar_starts データなし: year=%d", target_year)
                return None

            target_year_star_number = starts_row.star_number   # ← 수식 계산 불필요

            # 九星データ取得
            year_star = self.nine_star_repo.find_by_star_number(target_year_star_number)
            if not year_star:
                logger.error("中宮番号 %d に対応する九星データが見つかりません.", target_year_star_number)
                return None

            # 九星盤パターン取得
            pattern = self.star_grid_repo.get_by_center_star(target_year_star_number)

            result = {
                'year': target_year,
                'year_star': year_star.to_dict(),
                'star_number': target_year_star_number,
                'zodiac': starts_row.zodiac,
                'grid_pattern': pattern.to_dict() if pattern else None,
            }

            # 立春情報
            spring_term = self.solar_terms_repo.get_spring_start(target_year)
            if spring_term:
                result['spring_start_date'] = spring_term.solar_terms_date.strftime('%Y-%m-%d')
                next_year_spring_term = self.solar_terms_repo.get_spring_start(target_year + 1)
                if next_year_spring_term:
                    end_date = next_year_spring_term.solar_terms_date - timedelta(days=1)
                    result['spring_end_date'] = end_date.strftime('%Y-%m-%d')

            return result

        except Exception as e:
            logger.error("中宮情報の取得中にエラーが発生しました: %s", e, exc_info=True)
            return None