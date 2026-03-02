from __future__ import annotations

from datetime import datetime, date, time

import pytest

from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.entities.solar_term import SolarTerm

# --- テストケース ---

def _make_term(year: int, month: int, d: date) -> SolarTerm:
    return SolarTerm(
        year=year,
        month=month,
        solar_terms_date=d,
        solar_terms_time=time(0, 0),
        solar_terms_name="節入",
        zodiac="甲子",
        star_number=5,
    )


@pytest.mark.parametrize(
    "y,m,term_date,probe,expected_month",
    [
        # 当日→当月（CSV: 2025-03-05 17:07 啓蟄）
        (2025, 3, date(2025, 3, 5), datetime(2025, 3, 5, 18, 0), 3),
        # 前日→前月（CSV: 2025-03-05 の前日 3/04 は 2 月扱い、2月節入は 2025-02-03）
        (2025, 3, date(2025, 3, 5), datetime(2025, 3, 4, 12, 0), 2),
        # 年跨ぎ（1 月節入前日は前年 12 月）
        (2026, 1, date(2026, 1, 4), datetime(2026, 1, 3, 12, 0), 12),
    ],
)
def test_solar_month_parametrize(mocker, y, m, term_date, probe, expected_month):
    repo = mocker.create_autospec(ISolarTermsRepository, instance=True)

    def by_month(yy, mm):
        if (yy, mm) == (y, m):
            return _make_term(y, m, term_date)
        # 2025-03 ケースの前月（2月）
        if (y, m) == (2025, 3) and (yy, mm) == (2025, 2):
            return _make_term(2025, 2, date(2025, 2, 3))
        # 年跨ぎケースの前年 12 月
        if (y, m) == (2026, 1) and (yy, mm) == (2025, 12):
            return _make_term(2025, 12, date(2025, 12, 7))
        return None

    repo.get_term_by_month.side_effect = by_month
    assert StarCalculatorService.get_solar_month(probe, repo) == expected_month


