from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.domain.services.interfaces.year_fortune_service_interface import IYearFortuneService
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from apps.ninestarki.domain.services.interfaces.star_attribute_service_interface import IStarAttributeService
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.domain.services.star_life_guidance_service import StarLifeGuidanceService
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
import pytest


class PdfGenNoop(PdfGeneratorInterface):
    def __init__(self):
        self.html_renderer = type('R', (), {'render': lambda self, ctx: '<html></html>'})()
    def generate(self, report_data):
        return b"%PDF%"


class NoopPorts(IYearFortuneService, IMonthFortuneService, IStarAttributeService, IReadingQueryRepository, ISolarStartsRepository, ISolarCalendarProvider):
    def get_year_fortune_for_report(self, *a, **k): return {'directions': {}}
    def get_year_fortune(self, *a, **k): return {'directions': {}}
    def get_month_fortune_for_report(self, *a, **k): return {'directions': {}}
    def get_month_fortune(self, *a, **k): return {'directions': {}}
    def get_star_attributes(self, *a, **k): return {}
    def get_monthly_star_reading(self, *a, **k): return None
    def get_daily_star_reading(self, *a, **k): return None
    def get_main_star_message(self, *a, **k): return None
    def get_by_year(self, *a, **k): return type('S', (), {'zodiac': '子', 'solar_starts_date': None, 'star_number': 5})()
    def get_calculation_year(self, dt): return dt.year


class StarLifeGuidanceRepoFake(IStarLifeGuidanceRepository):
    def find_by_stars_and_category(self, *a, **k):
        return None
    def find_by_stars(self, *a, **k):
        class Obj: pass
        job = Obj(); job.category = 'job'; job.content = 'テスト職業'
        lucky = Obj(); lucky.category = 'lucky_item'; lucky.content = 'テスト開運アイテム'
        return [job, lucky]


class AuspiciousDatesServiceFake(IAuspiciousDatesService):
    def execute(self, main_star: int, month_star: int, target_year: int):
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


def test_happy_flow_returns_pdf_bytes(monkeypatch):
    # Appコンテキストの依存を除去: 方向マークの判定をno-opの結果にカット
    monkeypatch.setattr(
        DirectionMarksDomainService,
        "get_direction_fortune",
        staticmethod(lambda *args, **kwargs: {"north": {"is_auspicious": True}}),
    )

    uc = GenerateReportUseCase(
        pdf_generator=PdfGenNoop(),
        auspicious_dates_use_case=AuspiciousDatesServiceFake(),
        year_fortune_service=NoopPorts(),
        month_fortune_service=NoopPorts(),
        star_attribute_service=NoopPorts(),
        star_life_guidance_service=StarLifeGuidanceService(StarLifeGuidanceRepoFake()),
        calculate_stars_use_case=CalculateStarsUseCase(NineStarRepository(), SolarTermsRepoFake()),
        reading_query_repo=NoopPorts(),
        solar_starts_repo=NoopPorts(),
        solar_calendar_provider=NoopPorts(),
        report_context_builder=ReportContextBuilder(),
        compatibility_service=type('Compat', (), {'get_compatibility': lambda *a, **k: {'readings': []}})(),
    )

    payload: ReportInputDTO = {
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

    pdf_bytes = uc.execute_pdf(payload)
    assert isinstance(pdf_bytes, (bytes, bytearray)) and len(pdf_bytes) > 0

