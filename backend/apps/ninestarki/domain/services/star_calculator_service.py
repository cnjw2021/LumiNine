from datetime import datetime
from typing import Optional
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from core.services.solar_calendar_service import SolarCalendarService
from apps.ninestarki.domain.constants import ETO_LIST, ETO_TO_KYUSEI

class StarCalculatorService:
    """
    九星気学の星の番号を計算する純粋なビジネスロジックを担当します。
    """
    @staticmethod
    def get_day_kyusei_by_eto(eto: str) -> Optional[str]:
        """干支を入力して日命星（九星）を返す
        
        Args:
            eto: 干支
            
        Returns:
            Optional[str]: 日命星（九星）
        """
        try:
            index = ETO_LIST.index(eto)
            return ETO_TO_KYUSEI[index]
        except ValueError:
            return None

    @staticmethod
    def _calculate_star_number_from_year(year: int) -> int:
        """単純に年から星の番号を計算する内部ヘルパーメソッド
        
        Args:
            year: 対象年
            
        Returns:
            int: 星の番号
        """
        base_number = 11
        star_number = (base_number - (year % 9)) % 9
        return 9 if star_number == 0 else star_number

    @staticmethod
    def calculate_main_star_number(target_datetime: datetime, solar_terms_repo: ISolarTermsRepository) -> int:
        """
        立春日を考慮して本命星の番号を計算します。
        
        Args:
            target_datetime: 対象日
            
        Returns:
            int: 本命星の番号
        """
        year = target_datetime.year
        spring_term = solar_terms_repo.get_spring_start(year)
        if spring_term is None:
            # 春節が未登録の場合は従来ロジックで年を採用
            calculation_year = year
        else:
            spring_dt = datetime.combine(
                spring_term.solar_terms_date,
                (spring_term.solar_terms_time or datetime.min.time()),
            )
            calculation_year = year - 1 if target_datetime < spring_dt else year
        return StarCalculatorService._calculate_star_number_from_year(calculation_year)

    @staticmethod
    def get_solar_month(target_date: datetime, solar_terms_repo: ISolarTermsRepository) -> int:
        year = target_date.year
        calendar_month = target_date.month
        
        # 当月の節入り情報をポートから取得
        current_month_term = solar_terms_repo.get_term_by_month(year, calendar_month)
        
        if not current_month_term:
            return calendar_month
            
        current_term_datetime = datetime.combine(
            current_month_term.solar_terms_date,
            (current_month_term.solar_terms_time or datetime.min.time())
        )
        
        # 対象日が節入り日以前であれば、前の月を返す
        if target_date < current_term_datetime:
            return (calendar_month - 2 + 12) % 12 + 1
        
        return calendar_month

    @staticmethod
    def calculate_month_star_number(birth_datetime: datetime, main_star_number: int, solar_terms_repo: ISolarTermsRepository) -> Optional[int]:
        """
        節入り日を考慮して月命星の番号を計算します。
        
        Args:
            birth_datetime: 誕生日
            main_star_number: 本命星の番号
            
        Returns:
            Optional[int]: 月命星の番号
        """
        # get_solar_monthを使用して、九星気学の月を最初に取得します。
        season_month = StarCalculatorService.get_solar_month(birth_datetime, solar_terms_repo)
        
        tsukimeisei_table = {
            2: [8, 2, 5], 3: [7, 1, 4], 4: [6, 9, 3], 5: [5, 8, 2], 
            6: [4, 7, 1], 7: [3, 6, 9], 8: [2, 5, 8], 9: [1, 4, 7], 
            10: [9, 3, 6], 11: [8, 2, 5], 12: [7, 1, 4], 1: [6, 9, 3]
        }
        main_star_to_col = {
            1: 0, 4: 0, 7: 0, 2: 1, 5: 1, 8: 1, 3: 2, 6: 2, 9: 2
        }
        
        col_index = main_star_to_col.get(main_star_number)
        if col_index is None:
            return None
            
        try:
            return tsukimeisei_table.get(season_month)[col_index]
        except (TypeError, IndexError):
            return None