from datetime import datetime
from injector import inject
from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from apps.ninestarki.domain.services.numerology_service import NumerologyService
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.numerology_reading_repository_interface import (
    INumerologyReadingRepository,
)
from apps.ninestarki.domain.value_objects.numerology import MASTER_TO_BASE
from core.models.daily_astrology import DailyAstrology
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CalculateStarsUseCase:
    """
    生年月日からすべての九星を計算する責任を持ちます。
    """
    @inject
    def __init__(
        self,
        nine_star_repo: INineStarRepository,
        solar_terms_repo: ISolarTermsRepository,
        numerology_reading_repo: INumerologyReadingRepository,
    ):
        """
        コンストラクタを通じてリポジトリの実装オブジェクトを自動的に注入します.
        """
        self.nine_star_repo = nine_star_repo
        self.solar_terms_repo = solar_terms_repo
        self.calculator = StarCalculatorService()
        self._numerology_reading_repo = numerology_reading_repo

    def execute(self, birth_datetime_str: str, gender: str, target_year: int, locale: str = "ja") -> dict:
        logger.info(f"Executing CalculateStarsUseCase for {birth_datetime_str}")
        birth_datetime = datetime.strptime(birth_datetime_str, "%Y-%m-%d %H:%M")

        main_star_num = self.calculator.calculate_main_star_number(birth_datetime, self.solar_terms_repo)
        main_star = self.nine_star_repo.find_by_star_number(main_star_num)
        if not main_star:
            raise ValueError("本命星の計算に失敗しました")

        # solar_terms_repoを渡して月命計算
        # 節入り考慮の月取得と月命星計算
        month_star_num = self.calculator.calculate_month_star_number(birth_datetime, main_star_num, self.solar_terms_repo)
        month_star = self.nine_star_repo.find_by_star_number(month_star_num)
        if not month_star:
            raise ValueError("月命星の計算に失敗しました")

        day_astro_info = DailyAstrology.find_day_astro_info(birth_datetime)
        if not day_astro_info:
            raise ValueError("日命星の計算に失敗しました")
        day_star = self.nine_star_repo.find_by_star_number(day_astro_info.star_number)
        if not day_star:
            raise ValueError(f"日命星番号 {day_astro_info.star_number} に対応する九星が見つかりません")

        target_date = datetime(target_year, datetime.now().month, datetime.now().day)
        year_star_num = self.calculator.calculate_main_star_number(target_date, self.solar_terms_repo)
        year_star = self.nine_star_repo.find_by_star_number(year_star_num)
        if not year_star:
            raise ValueError("年運の計算に失敗しました")

        # ── 수비술 Life Path Number 계산 ──────────
        numerology_num = NumerologyService.calculate_life_path_number(birth_datetime_str)
        # Reading 데이터는 1~9만 존재하므로 Master Number → base number 변환
        reading_number = MASTER_TO_BASE.get(numerology_num.number, numerology_num.number)
        reading = self._numerology_reading_repo.get_reading(
            reading_number, locale=locale,
        )

        is_master = numerology_num.number != reading_number

        return {
            "birth_datetime": birth_datetime_str,
            "gender": gender,
            "target_year": target_year,
            "main_star": main_star.to_dict(),
            "month_star": month_star.to_dict(),
            "day_star": day_star.to_dict(),
            "year_star": year_star.to_dict(),
            "numerology": {
                "life_path_number": numerology_num.number,
                "is_master_number": is_master,
                "planet": numerology_num.planet.value,
                "planet_name": numerology_num.get_planet_name(locale),
                "reading_number": reading_number,
                "keywords": reading.keywords,
                "description": reading.description,
                "strengths": reading.strengths,
                "weaknesses": reading.weaknesses,
            },
        }