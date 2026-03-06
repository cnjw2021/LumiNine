from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.infrastructure.persistence.numerology_reading_repository import NumerologyReadingRepository
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
import pytest


class PdfGenNoop(PdfGeneratorInterface):
    def __init__(self):
        self.html_renderer = type('R', (), {'render': lambda self, ctx: '<html></html>'})()
    def generate(self, report_data):
        return b"%PDF%"


class NoopPorts(IReadingQueryRepository, ISolarStartsRepository, ISolarCalendarProvider):
    def get_main_star_message(self, *a, **k): return None
    def get_by_year(self, *a, **k): return type('S', (), {'zodiac': '子', 'solar_starts_date': None, 'star_number': 5})()
    def get_calculation_year(self, dt): return dt.year


class MonthlyDirectionsUCFake:
    def execute(self, *a, **k):
        return {"monthly_boards": {}}


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
    noop = NoopPorts()
    uc = GenerateReportUseCase(
        pdf_generator=PdfGenNoop(),
        monthly_directions_use_case=MonthlyDirectionsUCFake(),
        calculate_stars_use_case=CalculateStarsUseCase(NineStarRepository(), SolarTermsRepoFake(), NumerologyReadingRepository()),
        reading_query_repo=noop,
        solar_starts_repo=noop,
        solar_calendar_provider=noop,
        report_context_builder=ReportContextBuilder(),
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
