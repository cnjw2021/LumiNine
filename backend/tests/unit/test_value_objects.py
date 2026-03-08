"""Value Objects 단위 테스트.

커버리지:
  - PowerStone.get_name(): locale별 반환 + fallback 체인
  - StoneRecommendation: 생성 및 frozen 검증
  - PowerStoneResult: 3개 필드 검증
  - Locale Enum: 값 검증
  - Gogyo / GogyoRelation Enum: 값 검증
"""
from __future__ import annotations

import pytest

from apps.fortunetelling.ninestarki.domain.value_objects.locale import Locale
from apps.fortunetelling.ninestarki.domain.value_objects.gogyo import Gogyo, GogyoRelation
from apps.fortunetelling.powerstone.domain.value_objects.powerstone import (
    PowerStone,
    StoneRecommendation,
    PowerStoneResult,
)


# ══════════════════════════════════════════════════════
# Locale Enum
# ══════════════════════════════════════════════════════

class TestLocaleEnum:
    def test_values(self):
        assert Locale.JA == "ja"
        assert Locale.KO == "ko"
        assert Locale.EN == "en"

    def test_membership(self):
        assert "ja" in [l.value for l in Locale]
        assert len(Locale) == 3


# ══════════════════════════════════════════════════════
# Gogyo / GogyoRelation Enum
# ══════════════════════════════════════════════════════

class TestGogyoEnum:
    def test_five_elements(self):
        assert len(Gogyo) == 5
        assert Gogyo.WOOD == "木"
        assert Gogyo.FIRE == "火"
        assert Gogyo.EARTH == "土"
        assert Gogyo.METAL == "金"
        assert Gogyo.WATER == "水"


class TestGogyoRelationEnum:
    def test_three_relations(self):
        assert len(GogyoRelation) == 3
        assert GogyoRelation.SOJO == "相生"
        assert GogyoRelation.SOKOKU == "相剋"
        assert GogyoRelation.HIWA == "比和"


# ══════════════════════════════════════════════════════
# PowerStone
# ══════════════════════════════════════════════════════

@pytest.fixture
def emerald() -> PowerStone:
    return PowerStone(
        id="emerald",
        names={"ja": "エメラルド", "ko": "에메랄드", "en": "Emerald"},
        gogyo=Gogyo.WOOD,
        is_primary=True,
    )


@pytest.fixture
def stone_ja_only() -> PowerStone:
    """ja のみ名前を持つ石."""
    return PowerStone(
        id="jade",
        names={"ja": "翡翠"},
        gogyo=Gogyo.EARTH,
        is_primary=False,
    )


class TestPowerStone:
    def test_get_name_exact_locale(self, emerald: PowerStone):
        assert emerald.get_name("ja") == "エメラルド"
        assert emerald.get_name("ko") == "에메랄드"
        assert emerald.get_name("en") == "Emerald"

    def test_get_name_fallback_to_ja(self, emerald: PowerStone):
        """존재하지 않는 locale → ja fallback."""
        assert emerald.get_name("zh") == "エメラルド"

    def test_get_name_default_is_ja(self, emerald: PowerStone):
        """인수 없이 호출하면 ja."""
        assert emerald.get_name() == "エメラルド"

    def test_get_name_ja_only_stone(self, stone_ja_only: PowerStone):
        """ja만 있는 경우 모든 locale에서 ja 반환."""
        assert stone_ja_only.get_name("ko") == "翡翠"
        assert stone_ja_only.get_name("en") == "翡翠"

    def test_frozen(self, emerald: PowerStone):
        """frozen dataclass → 속성 변경 불가."""
        with pytest.raises(AttributeError):
            emerald.id = "ruby"  # type: ignore[misc]

    def test_get_name_no_ja_fallback_to_first(self):
        """ja 키가 없으면 첫 번째 값으로 fallback."""
        stone = PowerStone(id="ruby", names={"en": "Ruby"}, gogyo=Gogyo.FIRE, is_primary=True)
        assert stone.get_name("ko") == "Ruby"   # ko 없고 ja 없으므로 첫 번째 값
        assert stone.get_name("ja") == "Ruby"    # ja 없으므로 첫 번째 값
        assert stone.get_name() == "Ruby"        # 기본값 ja도 없으므로 첫 번째 값

    def test_empty_names_raises(self):
        """names가 비어있으면 ValueError."""
        with pytest.raises(ValueError, match="최소 1개"):
            PowerStone(id="invalid", names={}, gogyo=Gogyo.WOOD, is_primary=False)


# ══════════════════════════════════════════════════════
# StoneRecommendation
# ══════════════════════════════════════════════════════

class TestStoneRecommendation:
    def test_creation(self, emerald: PowerStone):
        rec = StoneRecommendation(
            stone=emerald,
            layer="base",
            gogyo=Gogyo.WOOD,
            reason_key="reason.base",
        )
        assert rec.stone == emerald
        assert rec.layer == "base"
        assert rec.reason_params == {}
        assert rec.direction is None
        assert rec.threat_mark is None

    def test_with_optional_fields(self, emerald: PowerStone):
        rec = StoneRecommendation(
            stone=emerald,
            layer="monthly",
            gogyo=Gogyo.FIRE,
            reason_key="reason.monthly",
            reason_params={"direction": "south"},
            direction="south",
        )
        assert rec.direction == "south"
        assert rec.reason_params["direction"] == "south"

    def test_frozen(self, emerald: PowerStone):
        rec = StoneRecommendation(
            stone=emerald, layer="base", gogyo=Gogyo.WOOD, reason_key="reason.base",
        )
        with pytest.raises(AttributeError):
            rec.layer = "monthly"  # type: ignore[misc]


# ══════════════════════════════════════════════════════
# PowerStoneResult
# ══════════════════════════════════════════════════════

class TestPowerStoneResult:
    def test_three_layers(self, emerald: PowerStone):
        base = StoneRecommendation(stone=emerald, layer="base", gogyo=Gogyo.WOOD, reason_key="r.base")
        monthly = StoneRecommendation(stone=emerald, layer="monthly", gogyo=Gogyo.FIRE, reason_key="r.monthly")
        protection = StoneRecommendation(stone=emerald, layer="protection", gogyo=Gogyo.WATER, reason_key="r.protection")

        result = PowerStoneResult(
            base_stone=base,
            monthly_stone=monthly,
            protection_stone=protection,
        )
        assert result.base_stone.layer == "base"
        assert result.monthly_stone.layer == "monthly"
        assert result.protection_stone.layer == "protection"
