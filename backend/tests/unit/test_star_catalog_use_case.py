import pytest

from apps.ninestarki.use_cases.star_catalog_use_case import StarCatalogUseCase


class Star:
    def __init__(self, n):
        self._n = n
    def to_dict(self):
        return {'star_number': self._n, 'name': f's{self._n}'}


class StubNineRepo:
    def find_all(self):
        return [Star(1), Star(9)]
    def find_by_star_number(self, n):
        return Star(n) if n in (1, 9) else None


@pytest.fixture
def uc():
    return StarCatalogUseCase(nine_repo=StubNineRepo())


def test_list_stars_returns_dicts(uc):
    items = uc.list_stars()
    assert items == [
        {'star_number': 1, 'name': 's1'},
        {'star_number': 9, 'name': 's9'},
    ]


def test_get_star_found(uc):
    assert uc.get_star(1) == {'star_number': 1, 'name': 's1'}


def test_get_star_not_found_returns_none(uc):
    assert uc.get_star(5) is None
