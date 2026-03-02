# infrastructure/persistence/astrology_data_reader.py

from datetime import date, datetime
from typing import Dict, Optional, List

from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from core.models.star_grid_pattern import StarGridPattern
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from core.models.daily_astrology import DailyAstrology
from core.models.zodiac_group_member import ZodiacGroupMember
from core.models.hourly_star_zodiac import HourlyStarZodiac
from apps.ninestarki.services.pattern_switch_service import PatternSwitchService
from apps.ninestarki.domain.services.auspicious_calendar_service import AuspiciousCalendarService
from core.utils.logger import get_logger

logger = get_logger(__name__)

class AstrologyDataReader:
    """
    九星気学の計算に必要な基本データをDBから取得するか、計算する役割。
    """
    def __init__(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository):
        self._solar_terms_repo = solar_terms_repo
        self._solar_starts_repo = solar_starts_repo

    def get_yearly_chart_info(self, target_year: int) -> Optional[Dict]:
        """指定年の年運情報（中宮星/盤/干支）を取得（ポート経由）。"""
        try:
            spring_term = self._solar_terms_repo.get_spring_start(target_year)
            if not spring_term:
                return None
            # 立春の正確な日時を使用して年星を算出
            target_datetime = datetime.combine(
                spring_term.solar_terms_date,
                spring_term.solar_terms_time or datetime.min.time()
            )
            year_star_num = StarCalculatorService.calculate_main_star_number(
                target_datetime, self._solar_terms_repo
            )
            grid_pattern = StarGridPattern.get_by_center_star(year_star_num)
            if not grid_pattern:
                return None
            # 年干支は solar_terms ではなく solar_starts を参照する
            starts_row = self._solar_starts_repo.get_by_year(target_year)
            zodiac = starts_row.zodiac if starts_row else spring_term.zodiac
            return {
                "year": target_year,
                "year_star_number": year_star_num,
                "grid_pattern": grid_pattern,
                "zodiac": zodiac,
            }
        except Exception as e:
            logger.error(f"Error in get_yearly_chart_info: {e}")
            return None

    def get_daily_info(self, target_date: datetime) -> Optional[Dict]:
        """
        すべての日次情報を取得するとき、正しいpattern_typeでフィルタリングして時間干支を取得します。
        """
        try:
            day_astrology = DailyAstrology.find_day_astro_info(target_date)
            month_term = self._solar_terms_repo.get_term_by_date(target_date)
            if not day_astrology or not month_term: return None

            day_pattern = StarGridPattern.get_by_center_star(day_astrology.star_number)
            if not day_pattern: return None

            zodiac_branch = day_astrology.zodiac[-1]
            zg = ZodiacGroupMember.query.filter_by(zodiac=zodiac_branch).first()
            if not zg:
                hourly_zodiacs_data = []
            else:
                # 陽遁・陰遁のパターンを取得
                pattern_type = PatternSwitchService.get_pattern_by_date(target_date)
                
                # クエリでpattern_typeをフィルタ条件として追加
                hour_records = HourlyStarZodiac.query.filter_by(
                    pattern_type=pattern_type,
                    group_id=zg.group_id,
                    center_star=day_astrology.star_number
                ).all()

                hourly_zodiacs_data = [
                    {"zodiac": r.hour_zodiac, "start_hour": r.start_hour, "end_hour": r.end_hour} 
                    for r in hour_records
                ]
                
            return {
                "date": target_date.strftime('%Y-%m-%d'),
                "day_astrology": day_astrology,
                "month_term": month_term,
                "day_pattern": day_pattern,
                "hourly_zodiacs": hourly_zodiacs_data
            }
        except Exception as e:
            logger.error(f"Error in get_daily_info for {target_date}: {e}")
            return None

    def get_hourly_zodiacs(self, day_astrology: DailyAstrology, pattern_type: str) -> List[Dict]:
        """ 時盤の干支と'時間情報'が含まれるオブジェクトリストを取得します。 """
        try:
            zodiac_branch = day_astrology.zodiac[-1]
            zg = ZodiacGroupMember.query.filter_by(zodiac=zodiac_branch).first()
            if not zg: return []

            hour_records = HourlyStarZodiac.query.filter_by(
                pattern_type=pattern_type,
                group_id=zg.group_id,
                center_star=day_astrology.star_number
            ).all()
            
            # 時間情報が含まれる辞書リストを返します。
            return [
                {
                    "zodiac": r.hour_zodiac,
                    "start_hour": r.start_hour,
                    "end_hour": r.end_hour
                } for r in hour_records
            ]
        except Exception as e:
            logger.error(f"Error in get_hourly_zodiacs: {e}")
            return []
            
    def get_dates_with_same_center_star(self, year: int) -> List[datetime]:
        """月命/日命の中宮が一致する日付のリストを取得します。"""
        try:
            start_date, end_date = AuspiciousCalendarService.calculate_date_range(year, self._solar_terms_repo)
            term_records = AuspiciousCalendarService.get_solar_terms_for_year(year, self._solar_terms_repo)
            if not term_records: return []
            logger.debug("date_range: year=%s start=%s end=%s", year, start_date, end_date)
            logger.debug(
                "term_records span: first=%s last=%s count=%d",
                term_records[0].solar_terms_date,
                term_records[-1].solar_terms_date,
                len(term_records),
            )

            results = []
            for idx, term in enumerate(term_records):
                period_start, period_end = AuspiciousCalendarService.get_period_range(term_records, idx, end_date)
                center_star = term.star_number

                matches = DailyAstrology.query.filter(
                    DailyAstrology.date >= period_start,
                    DailyAstrology.date <= period_end,
                    DailyAstrology.star_number == center_star
                ).all()
                
                for match in matches:
                    results.append(datetime.combine(match.date, datetime.min.time()))
            date_list = [d.strftime("%Y-%m-%d") for d in results]
            # 念のため、取得範囲外の日付を除外してログに記録
            in_range = [d for d in results if start_date <= d.date() <= end_date]
            out_of_range = [d for d in results if d not in in_range]
            if out_of_range:
                out_list = [d.strftime("%Y-%m-%d") for d in out_of_range]
                logger.warning(
                    "out_of_range dates detected: year=%s count=%d",
                    year,
                    len(out_list),
                )
                logger.debug("excluded_dates:\n%s", "\n".join(out_list))

            date_list = [d.strftime("%Y-%m-%d") for d in in_range]
            logger.debug(
                "get_dates_with_same_center_star result: year=%s total=%d",
                year,
                len(date_list),
            )
            if date_list:
                logger.debug("included_dates:\n%s", "\n".join(date_list))
            return in_range
        except Exception as e:
            logger.error(f"Error in get_dates_with_same_center_star for year {year}: {e}")
            return []