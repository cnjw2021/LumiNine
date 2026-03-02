from typing import Any, Dict
from datetime import date, datetime
from apps.ninestarki.utils.formatters.date_formatter import format_date_ja, now_string_ja
from apps.ninestarki.use_cases.dto.report_dtos import ReportContextDTO

class ReportContextBuilder:
    """レンダラーへ渡す最終コンテキストを構築する責務を担うビルダー"""

    def _format_date(self, d: Any) -> str:
        return format_date_ja(d)

    def build(
        self,
        user_info: Dict[str, Any],
        ninestar_info: Dict[str, Any],
        auspicious_day_result: Any,
        year_fortune: Any,
        month_fortune: Any,
        main_star_attributes: Any,
        month_star_attributes: Any,
        life_guidance: Dict[str, Any],
        direction_fortune: Dict[str, Any],
        year_zodiac: Any,
        spring_start_date: Any,
        spring_end_date: Any,
        template_id: int,
        background_id: int,
        use_simple: bool,
        compatibility: Any,
    ) -> ReportContextDTO:
        return {
            "user_info": user_info,
            "ninestar_info": ninestar_info,
            "auspicious_day_result": auspicious_day_result,
            "year_fortune": year_fortune,
            "month_fortune": month_fortune,
            "main_star_attributes": {
                "star_name": ninestar_info.get('main_star', {}).get('name_jp'),
                "attributes": main_star_attributes,
            },
            "month_star_attributes": {
                "star_name": ninestar_info.get('month_star', {}).get('name_jp'),
                "attributes": month_star_attributes,
            },
            "guidance_data": life_guidance,
            "direction_fortune": direction_fortune,
            "year_zodiac": year_zodiac,
            "spring_start_date": self._format_date(spring_start_date),
            "spring_end_date": self._format_date(spring_end_date),
            "template_id": template_id,
            "background_id": background_id,
            "use_simple": use_simple,
            "compatibility": compatibility,
            "report_date": now_string_ja(),
        }
