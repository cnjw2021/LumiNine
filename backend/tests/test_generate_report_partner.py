from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.use_cases.dto.report_dtos import ReportInputDTO
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
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


class CalcUseCaseFake:
    def execute(self, birth_datetime_str: str, gender: str, target_year: int):
        return {
            'main_star': {'star_number': 3},
            'month_star': {'star_number': 5},
            'day_star': {'star_number': 9},
        }


def test_partner_compatibility_flow_does_not_error(monkeypatch):
    noop = NoopPorts()
    uc = GenerateReportUseCase(
        pdf_generator=PdfGenNoop(),
        monthly_directions_use_case=MonthlyDirectionsUCFake(),
        calculate_stars_use_case=CalcUseCaseFake(),
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
        },
        'partner': {
            'full_name': 'Hanako',
            'birthdate': '1991-02-02',
            'gender': 'female',
        }
    }

    pdf_bytes = uc.execute_pdf(payload)
    assert isinstance(pdf_bytes, (bytes, bytearray))
