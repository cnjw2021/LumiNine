from __future__ import annotations

from datetime import date
import pytest

from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository


@pytest.mark.parametrize(
    "year, zodiac, star_number, starts_date",
    [
        (2025, '乙巳', 2, date(2025, 2, 4)),
        (2026, '丙午', 1, date(2026, 2, 4)),
        (2027, '丁未', 9, date(2027, 2, 4)),
    ],
)
def test_solar_starts_by_year(mocker, year, zodiac, star_number, starts_date):
    repo = mocker.create_autospec(ISolarStartsRepository, instance=True)

    class Row:
        pass

    row = Row()
    row.zodiac = zodiac
    row.star_number = star_number
    row.solar_starts_date = starts_date

    repo.get_by_year.return_value = row

    got = repo.get_by_year(year)
    assert got is not None
    assert got.zodiac == zodiac
    assert got.star_number == star_number
    assert got.solar_starts_date == starts_date

