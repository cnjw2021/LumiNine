"""方位の吉凶マークに関するドメインロジックを扱うサービス"""

from typing import List, Dict, Any
from datetime import datetime, date
from core.utils.logger import get_logger
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from injector import inject

logger = get_logger(__name__)


class DirectionMarksDomainService:
    """方位の吉凶マーク（破、暗剣殺など）を扱うドメインサービス"""
    _COMPATIBILITY_MATRIX_POLICY = "neutral"  # "neutral" | "inauspicious"

    @inject
    def __init__(self, star_grid_repo: IStarGridPatternRepository) -> None:
        self.star_grid_repo = star_grid_repo

    def get_direction_fortune(self, main_star, month_star, target_year):
        """指定条件に基づいて方位の吉凶情報を取得する

        Args:
            main_star (int): 本命星(1-9)
            month_star (int): 月命星(1-9)
            target_year (int): 対象年

        Returns:
            dict | None: 方位ごとの吉凶情報
        """
        try:
            logger.debug(f"Getting direction fortune for main_star={main_star}, month_star={month_star}, year={target_year}")

            current_date = datetime.now().date()
            target_date = date(target_year, current_date.month, current_date.day)
            target_datetime = datetime.combine(target_date, datetime.min.time())

            # 年運星（対象年の本命星）を計算（SolarTerms未依存の年ベースに変更）
            target_year_star_number = StarCalculatorService._calculate_star_number_from_year(target_year)

            # 九星盤パターンを取得（対象年の年運星を中央の星として使用）
            pattern = self.star_grid_repo.get_by_center_star(target_year_star_number)
            if not pattern:
                logger.error(f"星番号 {target_year_star_number} の九星盤パターンが見つかりません")
                return None

            # 対象年の干支を計算（取得できない場合は空文字）
            # 干支は上位層で与えるべきだが、ここでは既存契約を維持
            zodiac = ""

            # 方位の吉凶情報を取得
            try:
                result = pattern.get_fortune_status({
                    'main_star': main_star,
                    'month_star': month_star,
                    'year_star': target_year_star_number,
                    'zodiac': zodiac
                })
                return self._apply_compatibility_matrix_policy(result)
            except ValueError as e:
                logger.error(f"Failed to get direction fortune status: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Error getting direction fortune data: {str(e)}")
            return None

    @staticmethod
    def get_auspicious_directions(fortune_status: Dict[str, Dict[str, Any]]) -> List[str]:
        """方位の吉凶判定結果から、吉となる方位のリストを抽出する"""
        auspicious_directions = []
        for direction, status in fortune_status.items():
            if status.get("is_auspicious", False):
                auspicious_directions.append(direction)
        return sorted(auspicious_directions)

    def get_direction_fortune_with_context(self, main_star: int, month_star: int, target_year: int, year_star_number: int, zodiac: str) -> Dict[str, Any] | None:
        """
        事前に算出済みの年星・干支をコンテキストとして受け取り、方位の吉凶を判定します。
        DIやアプリケーションコンテキストに依存しません。
        """
        try:
            pattern = self.star_grid_repo.get_by_center_star(year_star_number)
            if not pattern:
                logger.error(f"星番号 {year_star_number} の九星盤パターンが見つかりません")
                return None
            params = {
                'main_star': main_star,
                'month_star': month_star,
                'year_star': year_star_number,
                'zodiac': zodiac or "",
            }
            result = pattern.get_fortune_status(params)
            return self._apply_compatibility_matrix_policy(result)
        except Exception as e:
            logger.error(f"Error getting direction fortune with context: {e}")
            return None

    def _apply_compatibility_matrix_policy(self, fortune_status: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        if self._COMPATIBILITY_MATRIX_POLICY != "neutral":
            return fortune_status
        for status in fortune_status.values():
            marks = status.get("marks", [])
            if marks == ["compatibility_matrix"]:
                status["is_auspicious"] = None
                status["reason"] = None
        return fortune_status


