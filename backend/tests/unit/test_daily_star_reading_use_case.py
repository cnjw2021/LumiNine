import pytest

from apps.ninestarki.use_cases.daily_star_reading_use_case import DailyStarReadingUseCase


class FakeDayAstro:
    def __init__(self, star_number):
        self.star_number = star_number
    def to_dict(self):
        return {'star_number': self.star_number, 'zodiac': '甲子'}


class FakeDailyAstrology:
    # Monkeypatch target
    @staticmethod
    def find_day_astro_info(birth_datetime):
        return FakeDayAstro(3)


class StubNineRepo:
    class _Star:
        def __init__(self, n):
            self.n = n
        def to_dict(self):
            return {'star_number': self.n, 'name': f's{self.n}'}

    def find_by_star_number(self, n):
        return self._Star(n)


class StubReadingRepo:
    def get_daily_star_reading(self, n):
        return {'id': 999, 'star_number': n, 'title': 't', 'keywords': 'k', 'description': 'd', 'advice': 'a'}


@pytest.fixture
def uc(monkeypatch):
    # Patch DailyAstrology in the module under test to deterministic fake
    import apps.ninestarki.use_cases.daily_star_reading_use_case as target
    target.DailyAstrology = FakeDailyAstrology
    return DailyStarReadingUseCase(nine_repo=StubNineRepo(), reading_repo=StubReadingRepo())


def test_execute_happy_path(uc):
    result = uc.execute('2025-01-02')
    assert result['day_astro']['star_number'] == 3
    assert result['day_star'] == {'star_number': 3, 'name': 's3'}
    assert result['day_reading'] == {
        'id': 999,
        'star_number': 3,
        'title': 't',
        'keywords': 'k',
        'description': 'd',
        'advice': 'a',
    }


def test_execute_invalid_date_raises(uc):
    with pytest.raises(ValueError):
        uc.execute('invalid-date')
