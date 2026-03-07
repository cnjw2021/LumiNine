from typing import Any, Dict, Optional
from datetime import datetime, date, timedelta

from apps.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository

from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO, ReportContextDTO
from core.exceptions import ValidationError, DomainRuleViolation
from core.utils.logger import get_logger
from core.config import get_config

logger = get_logger(__name__)

class GenerateReportUseCase:
    """PDF レポートコンテキスト作成用UseCase (PDF生成自体はフロントエンドへ移行)"""
    
    def __init__(self,
     monthly_directions_use_case: MonthlyDirectionsUseCase,
     calculate_stars_use_case: CalculateStarsUseCase,
     solar_starts_repo: ISolarStartsRepository,
     solar_calendar_provider: ISolarCalendarProvider,
     report_context_builder: ReportContextBuilder,
     solar_terms_repo: ISolarTermsRepository | None = None,
     ):
        self._monthly_directions_uc = monthly_directions_use_case
        self._calc_stars_uc = calculate_stars_use_case
        self._solar_starts_repo: ISolarStartsRepository = solar_starts_repo
        self._solar_terms_repo: ISolarTermsRepository | None = solar_terms_repo
        self._context_builder = report_context_builder
        self._calendar = solar_calendar_provider

    def _prepare_context(self, report_data: ReportInputDTO) -> ReportContextDTO:
        logger.info(f"レポートデータ Context 생성開始: {report_data.get('full_name')}")
        
        # 1. 基本情報
        if not report_data.get('full_name') or not report_data.get('birthdate') or not report_data.get('gender'):
            raise ValidationError("Missing required user_info fields", fields=[
                k for k in ['full_name', 'birthdate', 'gender'] if not report_data.get(k)
            ])

        result_data = report_data.get('result_data', {})
        main_star_num = result_data.get('main_star', {}).get('star_number')
        month_star_num = result_data.get('month_star', {}).get('star_number')
        day_star_num = result_data.get('day_star', {}).get('star_number')
        target_year = report_data.get('target_year', datetime.now().year)

        # 1-1. リーディング補強
        month_fortune = self._build_month_fortune_for_report(main_star_num, month_star_num, target_year)
        
        direction_fortune = {}

        # 2-1. 干支と期間情報（DBのみから取得し、ハードコードはしない）
        year_zodiac = None
        spring_start_date = None
        spring_end_date = None
        try:
            if self._solar_terms_repo:
                spring_term = self._solar_terms_repo.get_spring_start(target_year)
                if spring_term:
                    spring_start_date = spring_term.solar_terms_date.strftime('%Y-%m-%d')
                    next_year_spring_term = self._solar_terms_repo.get_spring_start(target_year + 1)
                    if next_year_spring_term:
                        end_date = next_year_spring_term.solar_terms_date - timedelta(days=1)
                        spring_end_date = end_date.strftime('%Y-%m-%d')

            current_date = date.today()
            calc_year = self._calendar.get_calculation_year(datetime(target_year, current_date.month, current_date.day))
            starts_cur = self._solar_starts_repo.get_by_year(calc_year)
            starts_next = self._solar_starts_repo.get_by_year(calc_year + 1)
            if starts_cur:
                year_zodiac = getattr(starts_cur, 'zodiac', None)
                if spring_start_date is None:
                    spring_start_date = getattr(starts_cur, 'solar_starts_date', None)
                    if spring_start_date:
                        spring_start_date = spring_start_date.strftime('%Y-%m-%d')
            if starts_cur and starts_next and getattr(starts_next, 'solar_starts_date', None):
                if spring_end_date is None:
                    spring_end_date = (getattr(starts_next, 'solar_starts_date') - timedelta(days=1)).strftime('%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Failed to compute zodiac/spring period: {e}")

        # 3. 컨텍스트 구축
        user_info = {
            'full_name': report_data.get('full_name'),
            'birthdate': report_data.get('birthdate'),
            'gender': report_data.get('gender'),
            'target_year': target_year,
        }

        return self._context_builder.build(
            user_info=user_info,
            ninestar_info=result_data,
            auspicious_day_result={'results': []},
            year_fortune={},
            month_fortune=month_fortune,
            main_star_attributes={},
            month_star_attributes={},
            life_guidance={'job': '', 'lucky_item': ''},
            direction_fortune=direction_fortune,
            year_zodiac=year_zodiac,
            spring_start_date=spring_start_date,
            spring_end_date=spring_end_date,
            template_id=report_data.get('template_id', 1),
            background_id=report_data.get('background_id', 1),
            use_simple=report_data.get('use_simple', False),
            compatibility=None,
        )

    # ──────────────────────────────────────────────────────────────
    # Private: MonthlyDirectionsUseCase → レポートテンプレート形式変換
    # ──────────────────────────────────────────────────────────────

    # 節月インデックス(1=寅月) → カレンダー月 のマッピング
    _SETSU_TO_CALENDAR_MONTH = {
        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7,
        7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 1,
    }

    def _build_month_fortune_for_report(
        self, main_star: int, month_star: int, target_year: int
    ) -> Dict[str, Any]:
        """MonthlyDirectionsUseCase の結果をレポートテンプレート形式に変換する。

        レポートテンプレート (monthly_fortune_page.html) は以下の構造を期待する::

            month_fortune.directions["1"] = {
                "year": int,
                "month": int,            # カレンダー月
                "display_month": str,     # "2026年3月"
                "display_title": str,     # "2026年3月 卯"
                "display_period": str,    # "3/6 - 4/4"
                "zodiac": str,            # "卯" or "乙卯"
                "star_number": int,       # 中宮星
                "center_star": int,
                "directions": { ... },
            }
        """
        try:
            result = self._monthly_directions_uc.execute(
                main_star=main_star,
                month_star=month_star,
                target_year=target_year,
            )
        except Exception as e:
            logger.warning("月運データの取得に失敗しました: %s", e)
            return {"directions": {}}

        annual_directions: Dict[str, Any] = {}
        for key, board in result.get("monthly_boards", {}).items():
            setsu_idx = board.get("setsu_month_index", 0)
            cal_month = self._SETSU_TO_CALENDAR_MONTH.get(setsu_idx, setsu_idx)
            zodiac = board.get("month_zodiac", "")
            branch = board.get("month_branch", zodiac[-1] if zodiac else "")
            period_start = board.get("period_start", "")
            period_end = board.get("period_end", "")

            # display_period: "3/6 - 4/4" 形式 + display_year 補正
            display_period = ""
            display_year = target_year
            if period_start and period_end:
                try:
                    ps = date.fromisoformat(period_start)
                    pe = date.fromisoformat(period_end)
                    display_period = f"{ps.month}/{ps.day} - {pe.month}/{pe.day}"
                    display_year = ps.year
                except (ValueError, TypeError):
                    pass

            # PDF テンプレート用: is_main_star / title / details を directions に付与
            raw_directions = board.get("directions", {})
            for _dir_key, dir_info in raw_directions.items():
                if isinstance(dir_info, dict):
                    marks = dir_info.get("marks", [])
                    dir_info["is_main_star"] = "main_star" in marks
                    reason = dir_info.get("reason") or ""
                    fortune_level = dir_info.get("fortune_level", "neutral")
                    if fortune_level == "best_auspicious":
                        dir_info.setdefault("title", "最大吉方")
                    elif fortune_level == "auspicious":
                        dir_info.setdefault("title", "吉方")
                    elif fortune_level == "inauspicious":
                        dir_info.setdefault("title", reason or "凶")
                    else:
                        dir_info.setdefault("title", "")
                    dir_info.setdefault("details", reason)

            annual_directions[str(cal_month)] = {
                "year": display_year,
                "month": cal_month,
                "display_month": f"{display_year}年{cal_month}月",
                "display_title": f"{display_year}年{cal_month}月 {branch}",
                "display_period": display_period,
                "zodiac": zodiac,
                "star_number": board.get("center_star"),
                "center_star": board.get("center_star"),
                "directions": raw_directions,
                "period_start": period_start,
                "period_end": period_end,
            }

        return {"directions": annual_directions}

