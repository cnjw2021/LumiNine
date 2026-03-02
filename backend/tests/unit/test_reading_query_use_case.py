import pytest

from apps.ninestarki.use_cases.reading_query_use_case import ReadingQueryUseCase


class StubReadingRepo:
    def __init__(self):
        self.monthly = {
            1: {'id': 101, 'star_number': 1, 'title': 't1', 'description': 'd1', 'keywords': 'k1', 'extra': 'x'},
        }
        self.daily = {
            2: {'id': 202, 'star_number': 2, 'title': 't2', 'description': 'd2', 'keywords': 'k2', 'advice': 'hidden'},
        }

    # interface methods
    def get_monthly_star_reading(self, star_number):
        return self.monthly.get(star_number)

    def get_daily_star_reading(self, star_number):
        return self.daily.get(star_number)

    def list_monthly_star_readings(self):
        return list(self.monthly.values())

    def list_daily_star_readings(self):
        return list(self.daily.values())


@pytest.fixture
def uc():
    return ReadingQueryUseCase(reading_repo=StubReadingRepo())


def test_get_monthly_star_reading_shapes_and_fields(uc):
    data = uc.get_monthly_star_reading(1)
    assert data == {
        'id': 101,
        'star_number': 1,
        'title': 't1',
        'keywords': 'k1',
        'description': 'd1',
    }


def test_get_monthly_star_reading_not_found_returns_none(uc):
    assert uc.get_monthly_star_reading(9) is None


def test_list_monthly_star_readings_filters_extras(uc):
    items = uc.list_monthly_star_readings()
    assert isinstance(items, list)
    assert items[0].keys() == {'id', 'star_number', 'title', 'keywords', 'description'}


def test_get_daily_star_reading_filters_advice(uc):
    data = uc.get_daily_star_reading(2)
    assert data == {
        'id': 202,
        'star_number': 2,
        'title': 't2',
        'keywords': 'k2',
        'description': 'd2',
    }


def test_list_daily_star_readings_filters_advice(uc):
    items = uc.list_daily_star_readings()
    assert isinstance(items, list)
    assert items[0].keys() == {'id', 'star_number', 'title', 'keywords', 'description'}
