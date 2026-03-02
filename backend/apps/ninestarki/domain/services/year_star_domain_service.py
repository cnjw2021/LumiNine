from datetime import datetime, date, timedelta
from typing import List, Optional

from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from core.utils.logger import get_logger

logger = get_logger(__name__)

class YearStarDomainService:
    """
    年の中宮(九星盤の中央の星)とそれに関連する情報を扱うドメインサービス.
    """
    def __init__(self, nine_star_repo: INineStarRepository, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository):
        """
        コンストラクタを通じてNineStarRepositoryのインスタンスを注入します.
        """
        self.nine_star_repo = nine_star_repo
        self.solar_terms_repo = solar_terms_repo
        self.solar_starts_repo = solar_starts_repo
        self.star_grid_repo = star_grid_repo

    def get_year_star_info(self, target_year: int) -> Optional[dict]:
        """
        指定された年の中宮情報を取得します.
        """
        try:
            # 春節開始日時を基準に、年の中宮を決定（ハードコーディング無し）
            spring_term = self.solar_terms_repo.get_spring_start(target_year)
            if not spring_term:
                return None
            target_date = spring_term.solar_terms_date
            target_time = spring_term.solar_terms_time or datetime.min.time()
            target_datetime = datetime.combine(target_date, target_time)
            # 上でtarget_datetimeを確定済み

            # 中宮を取得（SolarTermsポートを考慮して算出）
            target_year_star_number = StarCalculatorService.calculate_main_star_number(target_datetime, self.solar_terms_repo)

            # 注入されたリポジトリを使用してDBからデータを取得
            year_star = self.nine_star_repo.find_by_star_number(target_year_star_number)
            if not year_star:
                logger.error(f"中宮番号 {target_year_star_number}に対応する九星データが見つかりません.")
                return None

            # 九星盤パターンを取得（ポート経由）
            pattern = self.star_grid_repo.get_by_center_star(target_year_star_number)

            result = {
                'year': target_year,
                'year_star': year_star.to_dict(),
                'star_number': target_year_star_number,
                'grid_pattern': pattern.to_dict() if pattern else None
            }

            # 干支情報（ゴールデンマスター互換: SolarStartsポートで対象年の干支を取得）
            starts_row = self.solar_starts_repo.get_by_year(target_year)
            if starts_row:
                result['zodiac'] = starts_row.zodiac

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
            logger.error(f"中宮情報の取得中にエラーが発生しました: {e}", exc_info=True)
            return None