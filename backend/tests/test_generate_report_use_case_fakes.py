from typing import Any, Dict, Optional

from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.domain.services.interfaces.year_fortune_service_interface import IYearFortuneService
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from apps.ninestarki.domain.services.interfaces.star_attribute_service_interface import IStarAttributeService
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.domain.services.star_life_guidance_service import StarLifeGuidanceService
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.services.compatibility_service import CompatibilityService
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository


class PdfGenFake(PdfGeneratorInterface):
    def __init__(self):
        self.html_renderer = type('R', (), {'render': lambda self, ctx: '<html></html>'})()

    def generate(self, report_data: Dict[str, Any]) -> bytes:
        return b"%PDF-FAKE%"


class YearFortuneFake(IYearFortuneService):
    def get_year_fortune_for_report(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        return {'directions': {}}
    def get_year_fortune(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        return {'directions': {}}


class MonthFortuneFake(IMonthFortuneService):
    def get_month_fortune_for_report(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        return {'directions': {}}
    def get_month_fortune(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        return {'directions': {}}


class StarAttrFake(IStarAttributeService):
    def get_star_attributes(self, star_number: int) -> Dict[str, Any]:
        return {}


class ReadingQueryFake(IReadingQueryRepository):
    def get_monthly_star_reading(self, star_number: Optional[int]):
        return None
    def get_daily_star_reading(self, star_number: Optional[int]):
        return None
    def get_main_star_message(self, star_number: Optional[int]):
        return None


class SolarStartsRepoFake(ISolarStartsRepository):
    def get_by_year(self, year: int):
        class Obj: pass
        o = Obj()
        o.zodiac = '子'
        o.solar_starts_date = None
        o.star_number = 5
        return o


class CalendarProviderFake(ISolarCalendarProvider):
    def get_calculation_year(self, dt):
        return dt.year


class StarLifeGuidanceRepoFake(IStarLifeGuidanceRepository):
    def find_by_stars_and_category(self, *a, **k):
        return None
    def find_by_stars(self, *a, **k):
        class Obj: pass
        job = Obj(); job.category = 'job'; job.content = 'テスト職業'
        lucky = Obj(); lucky.category = 'lucky_item'; lucky.content = 'テスト開運アイテム'
        return [job, lucky]


class AuspiciousDatesServiceFake(IAuspiciousDatesService):
    def execute(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        # 최소 dict 계약으로 빈 결과 반환
        return {"moving_dates": [], "water_drawing_dates": []}


class SolarTermsRepoFake(ISolarTermsRepository):
    def get_yearly_terms(self, year: int):
        return []
    def get_term_by_month(self, year: int, month: int):
        return None
    def get_term_by_date(self, target_date):
        return None
    def get_spring_start(self, year: int):
        class T:
            zodiac = '子'
            solar_terms_date = None
            solar_terms_time = None
            star_number = 5
        return T()
    def get_by_id(self, term_id: int):
        return None
    def list_all(self):
        return []
    def update_term(self, term_id: int, data):
        return None


def test_generate_report_use_case_minimal_context(monkeypatch):
    # Appコンテキストの依存を除去: 方向マークの判定をno-opの結果にカット
    monkeypatch.setattr(
        DirectionMarksDomainService,
        "get_direction_fortune",
        staticmethod(lambda *args, **kwargs: {}),
    )

    uc = GenerateReportUseCase(
        pdf_generator=PdfGenFake(),
        auspicious_dates_use_case=AuspiciousDatesServiceFake(),
        year_fortune_service=YearFortuneFake(),
        month_fortune_service=MonthFortuneFake(),
        star_attribute_service=StarAttrFake(),
        star_life_guidance_service=StarLifeGuidanceService(StarLifeGuidanceRepoFake()),
        calculate_stars_use_case=CalculateStarsUseCase(NineStarRepository(), SolarTermsRepoFake()),
        compatibility_service=CompatibilityService(),
        reading_query_repo=ReadingQueryFake(),
        solar_starts_repo=SolarStartsRepoFake(),
        solar_calendar_provider=CalendarProviderFake(),
        report_context_builder=ReportContextBuilder(),
    )

    input_data: ReportInputDTO = {
        'full_name': 'Taro',
        'birthdate': '1990-01-01',
        'gender': 'male',
        'target_year': 2025,
        'result_data': {
            'main_star': {'star_number': 5},
            'month_star': {'star_number': 3},
            'day_star': {'star_number': 9},
        }
    }

    pdf_bytes = uc.execute_pdf(input_data)
    assert isinstance(pdf_bytes, (bytes, bytearray))
