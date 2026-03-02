from __future__ import annotations
from typing import Dict, Any, List, Optional

from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService
from apps.ninestarki.domain.services.interfaces.astrology_data_reader_interface import IAstrologyDataReader
from apps.ninestarki.domain.services.interfaces.compatibility_service_interface import ICompatibilityService
from apps.ninestarki.utils.direction_utils import convert_directions_to_japanese
from core.utils.logger import get_logger
from injector import inject
from apps.ninestarki.domain.services.direction_rule_engine import DirectionRuleEngine


logger = get_logger(__name__)


class AuspiciousDatesDomainService(IAuspiciousDatesService):
    """引越し吉日/お水取り吉日を算出するドメインサービス（単一の契約 dict を返す）"""

    @inject
    def __init__(self, reader: IAstrologyDataReader, compat: ICompatibilityService, rule_engine: DirectionRuleEngine | None = None) -> None:
        self.reader = reader
        self.compat = compat
        self.rule_engine: DirectionRuleEngine | None = rule_engine

    def execute(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        logger.info(f"AuspiciousDatesDomainService.execute start: year={target_year}")
        self._validate_inputs(main_star, month_star, target_year)

        yearly_info = self.reader.get_yearly_chart_info(target_year)
        if not yearly_info:
            logger.warning(f"No yearly_info for {target_year}")
            return self._format_response([], [])

        if not self.rule_engine:
            raise RuntimeError("DirectionRuleEngine is not injected. Please bind and inject before use.")
        yearly_fortune = self.rule_engine.get_yearly_fortune_directions(
            grid_pattern=yearly_info["grid_pattern"],
            main_star=main_star,
            month_star=month_star,
            year_star=yearly_info["year_star_number"],
            zodiac=yearly_info["zodiac"],
        )
        base_auspicious_directions = self.rule_engine.filter_auspicious_directions(yearly_fortune)
        base_auspicious_directions = self.rule_engine.filter_out_inauspicious_directions(
            base_auspicious_directions, yearly_info["year_star_number"], yearly_info["zodiac"]
        )
        if not base_auspicious_directions:
            return self._format_response([], [])

        comp_stars_raw = self.compat.get_best_common_and_main_compatible_stars(main_star, month_star)
        compatible_stars = [
            star for star in (comp_stars_raw.get("common_best", []) + comp_stars_raw.get("main_only_good", []))
            if star not in [main_star, month_star]
        ]

        candidate_dates = self.reader.get_dates_with_same_center_star(target_year)
        if not candidate_dates:
            return self._format_response([], [])

        auspicious_moving_dates: List[Dict[str, Any]] = []
        for target_date in candidate_dates:
            # 日別データを取得（取得できない日は除外）
            daily_info = self.reader.get_daily_info(target_date)
            if not daily_info:
                logger.debug("exclude date=%s reason=no_daily_info", target_date)
                continue
            # 節入り当日は除外
            term_date = daily_info["month_term"].solar_terms_date
            if daily_info["date"] == term_date.strftime("%Y-%m-%d"):
                logger.debug("exclude date=%s reason=solar_term_boundary", daily_info.get("date"))
                continue

            # 相性星が一致する方位がない日は除外
            valid_directions = self.rule_engine.get_directions_with_compatible_stars(
                daily_info["day_pattern"], base_auspicious_directions, compatible_stars
            )
            if not valid_directions:
                logger.debug("exclude date=%s reason=no_valid_directions", daily_info.get("date"))
                continue
            # 本命殺/的殺・月命殺/的殺の方位を除外
            day_fortune = self.rule_engine.get_yearly_fortune_directions(
                grid_pattern=daily_info["day_pattern"],
                main_star=main_star,
                month_star=month_star,
                year_star=daily_info["day_astrology"].star_number,
                zodiac=daily_info["day_astrology"].zodiac,
            )
            invalid_marks = {"main_star", "month_star", "main_star_opposite", "month_star_opposite"}
            valid_directions = [
                direction for direction in valid_directions
                if not (set(day_fortune.get(direction, {}).get("marks", [])) & invalid_marks)
            ]
            if not valid_directions:
                logger.debug("exclude date=%s reason=main_month_marks", daily_info.get("date"))
                continue

            # 月/日/時間の凶方位チェックを通過した日だけ残す（方向は絞り込み）
            filtered_result = self._filter_directions_and_get_data(daily_info, valid_directions)
            if filtered_result is None:
                logger.debug("exclude date=%s reason=inauspicious_marks", daily_info.get("date"))
                continue
            filtered_directions, safe_hourly_info = filtered_result

            # すべて通過した日のみ吉日候補として追加
            auspicious_moving_dates.append({
                "daily_info": daily_info,
                "auspicious_directions": filtered_directions,
                "auspicious_times_data": safe_hourly_info,
            })

        auspicious_water_drawing_dates = self._filter_water_drawing_dates(
            auspicious_moving_dates, yearly_info["year_star_number"]
        )

        return self._format_response(auspicious_moving_dates, auspicious_water_drawing_dates)

    def _validate_inputs(self, main_star: int, month_star: int, year: int):
        if not (1 <= main_star <= 9 and 1 <= month_star <= 9):
            raise ValueError("本命星と月命星は1-9の間の値でなければなりません。")
        if not (1900 <= year <= 2100):
            raise ValueError("年は1900-2100の間の値でなければなりません。")

    def _filter_directions_and_get_data(
        self, daily_info: Dict, directions: List[str]
    ) -> Optional[tuple[List[str], List[Dict]]]:
        filtered_directions = self.rule_engine.filter_out_inauspicious_directions(
            directions, daily_info["month_term"].star_number, daily_info["month_term"].zodiac
        )
        if not filtered_directions:
            return None
        filtered_directions = self.rule_engine.filter_out_inauspicious_directions(
            filtered_directions, daily_info["day_astrology"].star_number, daily_info["day_astrology"].zodiac
        )
        if not filtered_directions:
            return None

        hourly_info = daily_info['hourly_zodiacs']
        is_hour_safe = self.rule_engine.check_hour_zodiac_marks(filtered_directions, hourly_info)
        if not is_hour_safe:
            return None
        return filtered_directions, hourly_info

    def _filter_water_drawing_dates(self, moving_dates: List[Dict], year_star_num: int) -> List[Dict]:
        water_drawing_dates: List[Dict] = []
        for item in moving_dates:
            daily_info = item["daily_info"]
            month_star_num = daily_info["month_term"].star_number
            day_star_num = daily_info["day_astrology"].star_number
            # お水取り吉日は時間帯が1つだけのケースに限定
            if year_star_num == month_star_num == day_star_num and len(item.get("auspicious_times_data", [])) == 1:
                water_drawing_dates.append(item)
        return water_drawing_dates

    def _format_response(self, moving_dates: List[Dict], water_drawing_dates: List[Dict]) -> Dict[str, Any]:
        direction_order = {
            "east": 0,
            "north": 1,
            "south": 2,
            "west": 3,
            "southwest": 4,
            "northwest": 5,
            "northeast": 6,
            "southeast": 7,
            "center": 8,
        }

        def format_moving(date_list: List[Dict]) -> List[Dict]:
            formatted: List[Dict[str, Any]] = []
            for item in date_list:
                ordered = sorted(item["auspicious_directions"], key=lambda d: direction_order.get(d, 99))
                formatted.append({
                    "date": item["daily_info"]["date"],
                    "auspicious_directions": convert_directions_to_japanese(ordered),
                })
            return sorted(formatted, key=lambda x: x['date'])

        def format_water(date_list: List[Dict]) -> List[Dict]:
            enriched: List[Dict[str, Any]] = []
            for item in date_list:
                ordered = sorted(item["auspicious_directions"], key=lambda d: direction_order.get(d, 99))
                time_slots = []
                for hour_info in item.get("auspicious_times_data", []):
                    time_slots.append({
                        "zodiac": hour_info['zodiac'],
                        "time": f"{hour_info['start_hour']:02d}時〜{hour_info['end_hour']:02d}時",
                    })
                enriched.append({
                    "date": item["daily_info"]["date"],
                    "auspicious_directions": convert_directions_to_japanese(ordered),
                    "auspicious_times": time_slots,
                })
            return sorted(enriched, key=lambda x: x['date'])

        moving_formatted = format_moving(moving_dates)
        water_formatted = format_water(water_drawing_dates)

        return {
            "moving_dates": moving_formatted,
            "water_drawing_dates": water_formatted,
        }


