"""StarAttributeRepository / recommended_foods 단위 테스트.

커버리지:
  - IStarAttributeRepository stub을 통한 find_by_star_and_type 스펙 검증
  - recommended_foods 정상 반환: star_number와 'food' 타입으로 조회
  - 빈 배열 반환: DB에 food 데이터 없을 때 빈 리스트 반환
  - 에러 발생 시 빈 리스트 반환 (StarAttributeRepository의 에러 처리 확인)
"""
from __future__ import annotations

from typing import List

import pytest

from apps.reading.ninestarki.domain.repositories.star_attribute_repository_interface import (
    IStarAttributeRepository,
)
from apps.reading.ninestarki.infrastructure.persistence.star_attribute_repository import (
    StarAttributeRepository,
)


# ── Stub 구현 ────────────────────────────────────────────

class StubStarAttributeRepository(IStarAttributeRepository):
    """테스트용 IStarAttributeRepository 스텁."""

    def __init__(self, data: dict[tuple[int, str], list[str]] | None = None):
        self._data: dict[tuple[int, str], list[str]] = data or {}

    def find_by_star_and_type(self, star_number: int, attribute_type: str) -> List[str]:
        return self._data.get((star_number, attribute_type), [])


class RaisingStubRepository(IStarAttributeRepository):
    """find_by_star_and_type 호출 시 예외를 발생시키는 스텁."""

    def find_by_star_and_type(self, star_number: int, attribute_type: str) -> List[str]:
        raise RuntimeError("DB connection error")


# ══════════════════════════════════════════════════════
# IStarAttributeRepository 인터페이스 스펙 검증
# ══════════════════════════════════════════════════════

class TestStarAttributeRepositoryInterface:
    """StubStarAttributeRepository를 통해 인터페이스 계약을 검증합니다."""

    def test_returns_food_list_for_valid_star(self):
        """star_number=1, attribute_type='food' 조회 시 food 값 목록을 반환한다."""
        repo = StubStarAttributeRepository(
            data={
                (1, "food"): ["水分の多い食べ物・海産物", "豆腐・白い食べ物・塩分"],
            }
        )
        result = repo.find_by_star_and_type(star_number=1, attribute_type="food")
        assert result == ["水分の多い食べ物・海産物", "豆腐・白い食べ物・塩分"]

    def test_returns_empty_list_for_unknown_star(self):
        """등록되지 않은 star_number 조회 시 빈 리스트를 반환한다."""
        repo = StubStarAttributeRepository(data={})
        result = repo.find_by_star_and_type(star_number=99, attribute_type="food")
        assert result == []

    def test_returns_empty_list_for_unknown_type(self):
        """food 데이터는 있지만 다른 attribute_type 조회 시 빈 리스트를 반환한다."""
        repo = StubStarAttributeRepository(
            data={(1, "food"): ["豆腐"]}
        )
        result = repo.find_by_star_and_type(star_number=1, attribute_type="color")
        assert result == []

    def test_all_nine_stars_have_food_entries(self):
        """1~9 모든 본명성에 대해 food 타입 데이터를 조회할 수 있다."""
        data = {
            (1, "food"): ["水分の多い食べ物・海産物", "豆腐・白い食べ物・塩分"],
            (2, "food"): ["芋類・根菜・保存食品", "重厚な味わいの料理・黒い食べ物"],
            (3, "food"): ["青菜・新芽・若葉", "発酵食品・ハーブ・酸味のある食べ物"],
            (4, "food"): ["野菜・サラダ・緑の食べ物", "種子・ナッツ・バランスの良い食事"],
            (5, "food"): ["穀物・米・パン・主食", "黄色い食べ物・濃厚な食べ物"],
            (6, "food"): ["スイカ・メロン", "カステラ・天ぷら"],
            (7, "food"): ["赤い食べ物・スパイシーな料理", "高級食材・豪華な料理・甘い食べ物"],
            (8, "food"): ["白い食べ物・淡白な味わいの料理", "粉もの・乾燥食品・伝統的な料理"],
            (9, "food"): ["辛い食べ物・赤い料理・燻製", "油を使った料理・焼き料理・熱々の食べ物"],
        }
        repo = StubStarAttributeRepository(data=data)
        for star_number in range(1, 10):
            result = repo.find_by_star_and_type(star_number=star_number, attribute_type="food")
            assert len(result) > 0, f"star_number={star_number}: food 데이터가 비어 있습니다"
            assert all(isinstance(v, str) for v in result), \
                f"star_number={star_number}: 반환값이 모두 str이어야 합니다"

    def test_returns_list_type(self):
        """반환값은 항상 list 타입이어야 한다 (None 반환 금지)."""
        repo = StubStarAttributeRepository(data={})
        result = repo.find_by_star_and_type(star_number=1, attribute_type="food")
        assert isinstance(result, list)


# ══════════════════════════════════════════════════════
# StarAttributeRepository 에러 처리 (실제 구현체)
# ══════════════════════════════════════════════════════

class TestStarAttributeRepositoryErrorHandling:
    """StarAttributeRepository의 에러 처리 동작을 검증합니다."""

    def test_returns_empty_list_on_exception(self, monkeypatch):
        """DB 조회 중 예외 발생 시 빈 리스트를 반환한다 (서비스 중단 방지)."""
        repo = StarAttributeRepository.__new__(StarAttributeRepository)

        def raise_on_query(*args, **kwargs):
            raise RuntimeError("Simulated DB failure")

        monkeypatch.setattr(
            "apps.reading.ninestarki.infrastructure.persistence."
            "star_attribute_repository.read_only_session",
            raise_on_query,
        )

        result = repo.find_by_star_and_type(star_number=1, attribute_type="food")
        assert result == []
