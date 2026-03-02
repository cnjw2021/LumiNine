from typing import Any, Dict, Optional
from datetime import datetime, date, timedelta

# 必要なすべてのサービスとファインダーをインポートします。
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.domain.services.interfaces.year_fortune_service_interface import IYearFortuneService
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from apps.ninestarki.domain.services.interfaces.star_attribute_service_interface import IStarAttributeService
from apps.ninestarki.domain.services.star_life_guidance_service import StarLifeGuidanceService
from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.services.compatibility_service import CompatibilityService
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.infrastructure.persistence.reading_query_repository import ReadingQueryRepository
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO, ReportContextDTO
from apps.ninestarki.presentation.auspicious_dates_presenter import AuspiciousDatesPresenter
from core.exceptions import ValidationError, DomainRuleViolation
from core.utils.logger import get_logger
from core.config import get_config

logger = get_logger(__name__)

class GenerateReportUseCase:
    """PDF レポート生成を担当するUseCase"""
    
    def __init__(self,
     pdf_generator: PdfGeneratorInterface,
     auspicious_dates_use_case: IAuspiciousDatesService,
     year_fortune_service: IYearFortuneService,
     month_fortune_service: IMonthFortuneService,
     star_attribute_service: IStarAttributeService,
     star_life_guidance_service: StarLifeGuidanceService,
     calculate_stars_use_case: CalculateStarsUseCase,
     compatibility_service: CompatibilityService,
     reading_query_repo: IReadingQueryRepository,
     solar_starts_repo: ISolarStartsRepository,
     solar_calendar_provider: ISolarCalendarProvider,
     report_context_builder: ReportContextBuilder,
     direction_marks_service: Optional[DirectionMarksDomainService] = None,
     auspicious_dates_presenter: AuspiciousDatesPresenter | None = None,
     solar_terms_repo: ISolarTermsRepository | None = None,
     ):
        self.pdf_generator = pdf_generator
        self.auspicious_dates_service = auspicious_dates_use_case
        self._auspicious_dates_presenter = auspicious_dates_presenter or AuspiciousDatesPresenter()
        self.year_fortune_service = year_fortune_service
        self.month_fortune_service = month_fortune_service
        self.star_attribute_service = star_attribute_service
        self.star_life_guidance_service = star_life_guidance_service
        # Required DI
        self._calc_stars_uc = calculate_stars_use_case
        self._compat_service = compatibility_service
        self._reading_query: IReadingQueryRepository = reading_query_repo
        self._solar_starts_repo: ISolarStartsRepository = solar_starts_repo
        self._solar_terms_repo: ISolarTermsRepository | None = solar_terms_repo
        self._context_builder = report_context_builder
        self._calendar = solar_calendar_provider
        self._direction_marks = direction_marks_service

    def execute_pdf(self, report_data: ReportInputDTO) -> bytes:
        context = self._prepare_context(report_data)
        return self.pdf_generator.generate(context)

    def execute_html_preview(self, report_data: ReportInputDTO) -> str:
        context = self._prepare_context(report_data)
        return self.pdf_generator.html_renderer.render(context)

    def _prepare_context(self, report_data: ReportInputDTO) -> ReportContextDTO:
        logger.info(f"PDF 生成 UseCase 実行開始: {report_data.get('full_name')}")
        
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
        enriched_result = dict(result_data)
        try:
            msr_dict = self._reading_query.get_monthly_star_reading(month_star_num)
            if msr_dict:
                enriched_result['month_star_reading'] = msr_dict
            dsr_dict = self._reading_query.get_daily_star_reading(day_star_num)
            if dsr_dict:
                enriched_result['day_star_reading'] = dsr_dict
            mnr_dict = self._reading_query.get_main_star_message(main_star_num)
            if mnr_dict:
                enriched_result['main_star_reading'] = mnr_dict
        except Exception as e:
            logger.warning(f"Reading enrichment failed: {e}")

        # 2. サービスの検索
        if main_star_num is None or month_star_num is None:
            # サーバーの再計算が失敗したか、入力が不完全です
            raise DomainRuleViolation("Star numbers are not available for report generation")

        # 画面と同一ロジックで吉日を算出（/api/reports/auspicious-days と同一のサービス）
        auspicious_day_raw = self.auspicious_dates_service.execute(main_star_num, month_star_num, target_year)
        auspicious_day_data = self._auspicious_dates_presenter.enrich_response(auspicious_day_raw)
        year_fortune = self.year_fortune_service.get_year_fortune_for_report(main_star_num, month_star_num, target_year)
        month_fortune = self.month_fortune_service.get_month_fortune_for_report(main_star_num, month_star_num, target_year)
        main_star_attributes = self.star_attribute_service.get_star_attributes(main_star_num)
        month_star_attributes = self.star_attribute_service.get_star_attributes(month_star_num)
        life_guidance_raw = self.star_life_guidance_service.get_star_life_guidance(main_star_num, month_star_num)
        life_guidance = {
            'job': (life_guidance_raw or {}).get('job') or '',
            'lucky_item': (life_guidance_raw or {}).get('lucky_item') or ''
        }
        if self._direction_marks:
            direction_fortune = self._direction_marks.get_direction_fortune(main_star_num, month_star_num, target_year)
        else:
            direction_fortune = {}

        # 2-α. 相手(파트너) 정보가 있으면 서버에서 상성 재계산
        compatibility = None
        try:
            partner = report_data.get('partner') or {}
            if partner.get('birthdate') and partner.get('gender'):
                partner_birth_norm = str(partner['birthdate']).replace('/', '-')
                cfg = get_config()
                noon = getattr(cfg, 'DEFAULT_NOON_TIME', '12:00')
                partner_calc = self._calc_stars_uc.execute(f"{partner_birth_norm} {noon}", partner['gender'], target_year)

                main_star_for_compat = int(main_star_num) if main_star_num else None
                target_star_for_compat = int(partner_calc.get('main_star', {}).get('star_number')) if partner_calc else None
                if main_star_for_compat and target_star_for_compat:
                    main_birth_month = int(str(report_data.get('birthdate')).split('-')[1])
                    target_birth_month = int(str(partner_birth_norm).split('-')[1])
                    is_male = True if str(report_data.get('gender')).lower() == 'male' else False
                    compatibility = self._compat_service.get_compatibility(
                        main_star=main_star_for_compat,
                        target_star=target_star_for_compat,
                        main_birth_month=main_birth_month,
                        target_birth_month=target_birth_month,
                        is_male=is_male
                    )
        except Exception as e:
            logger.warning(f"Compatibility recompute skipped: {e}")

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
            ninestar_info=enriched_result,
            auspicious_day_result=auspicious_day_data,
            year_fortune=year_fortune,
            month_fortune=month_fortune,
            main_star_attributes=main_star_attributes,
            month_star_attributes=month_star_attributes,
            life_guidance=life_guidance,
            direction_fortune=direction_fortune,
            year_zodiac=year_zodiac,
            spring_start_date=spring_start_date,
            spring_end_date=spring_end_date,
            template_id=report_data.get('template_id', 1),
            background_id=report_data.get('background_id', 1),
            use_simple=report_data.get('use_simple', False),
            compatibility=compatibility,
        )
