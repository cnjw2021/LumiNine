"""PowerStoneRecommendationUseCase 단위 테스트.

커버리지:
  - 정상 흐름: directions → 3개 스톤 추천 결과 dict 반환
  - locale별 응답: ja / ko / en 에서 stone_name, reason 텍스트 확인
  - 에러 전파: NoAuspiciousDirectionError 상위 전달
"""
from __future__ import annotations

import pytest

from apps.ninestarki.domain.exceptions import (
    NoAuspiciousDirectionError,
)
from apps.ninestarki.domain.services.gogyo_service import GogyoService
from apps.ninestarki.domain.services.powerstone_matching_engine import (
    PowerStoneMatchingEngine,
)
from apps.ninestarki.infrastructure.persistence.powerstone_repository import (
    PowerStoneRepository,
)
from apps.ninestarki.infrastructure.services.message_catalog import MessageCatalog
from apps.ninestarki.use_cases.powerstone_recommendation_use_case import (
    PowerStoneRecommendationUseCase,
)


# ── 픽스처 ────────────────────────────────────────────

@pytest.fixture
def use_case() -> PowerStoneRecommendationUseCase:
    gogyo = GogyoService()
    repo = PowerStoneRepository()
    engine = PowerStoneMatchingEngine(gogyo_service=gogyo, stone_repo=repo)
    catalog = MessageCatalog()
    return PowerStoneRecommendationUseCase(
        matching_engine=engine,
        message_catalog=catalog,
    )


def _make_directions(
    auspicious: dict[str, bool] | None = None,
    marks: dict[str, list] | None = None,
) -> dict:
    """테스트용 directions 딕셔너리 생성 헬퍼."""
    all_dirs = [
        "north", "south", "east", "west",
        "northeast", "northwest", "southeast", "southwest",
    ]
    result = {}
    for d in all_dirs:
        result[d] = {
            "is_auspicious": (auspicious or {}).get(d, False),
            "marks": (marks or {}).get(d, []),
        }
    return result


# ══════════════════════════════════════════════════════
# 정상 흐름
# ══════════════════════════════════════════════════════

class TestExecuteHappyPath:
    def test_returns_three_stone_keys(self, use_case: PowerStoneRecommendationUseCase):
        """결과에 base_stone, monthly_stone, protection_stone 키가 존재한다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions)
        assert "base_stone" in result
        assert "monthly_stone" in result
        assert "protection_stone" in result

    def test_stone_has_required_fields(self, use_case: PowerStoneRecommendationUseCase):
        """각 스톤 dict에 stone_id, stone_name, layer, gogyo, reason 필드가 존재한다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions)
        for key in ("base_stone", "monthly_stone", "protection_stone"):
            stone = result[key]
            assert "stone_id" in stone
            assert "stone_name" in stone
            assert "layer" in stone
            assert "gogyo" in stone
            assert "reason" in stone

    def test_three_distinct_stone_ids(self, use_case: PowerStoneRecommendationUseCase):
        """3개 스톤은 서로 다른 stone_id를 갖는다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions)
        ids = {
            result["base_stone"]["stone_id"],
            result["monthly_stone"]["stone_id"],
            result["protection_stone"]["stone_id"],
        }
        assert len(ids) == 3


# ══════════════════════════════════════════════════════
# locale별 응답 텍스트
# ══════════════════════════════════════════════════════

class TestLocaleRendering:
    def test_ja_stone_name(self, use_case: PowerStoneRecommendationUseCase):
        """locale=ja 에서 일본어 스톤 이름이 반환된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions, locale="ja")
        # aquamarine → アクアマリン
        assert result["base_stone"]["stone_name"] == "アクアマリン"

    def test_ko_stone_name(self, use_case: PowerStoneRecommendationUseCase):
        """locale=ko 에서 한국어 스톤 이름이 반환된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions, locale="ko")
        assert result["base_stone"]["stone_name"] == "아쿠아마린"

    def test_en_stone_name(self, use_case: PowerStoneRecommendationUseCase):
        """locale=en 에서 영어 스톤 이름이 반환된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions, locale="en")
        assert result["base_stone"]["stone_name"] == "Aquamarine"

    def test_ja_layer_name(self, use_case: PowerStoneRecommendationUseCase):
        """locale=ja 에서 layer 이름이 일본어로 렌더링된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions, locale="ja")
        assert result["base_stone"]["layer"] == "基本石"
        assert result["monthly_stone"]["layer"] == "月運石"
        assert result["protection_stone"]["layer"] == "護身石"

    def test_ko_layer_name(self, use_case: PowerStoneRecommendationUseCase):
        """locale=ko 에서 layer 이름이 한국어로 렌더링된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions, locale="ko")
        assert result["base_stone"]["layer"] == "기본석"
        assert result["monthly_stone"]["layer"] == "월운석"
        assert result["protection_stone"]["layer"] == "호신석"

    def test_reason_contains_no_placeholder(self, use_case: PowerStoneRecommendationUseCase):
        """reason 텍스트에 치환되지 않은 {placeholder}가 남지 않는다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        for loc in ("ja", "ko", "en"):
            result = use_case.execute(main_star=1, directions=directions, locale=loc)
            for key in ("base_stone", "monthly_stone", "protection_stone"):
                reason = result[key]["reason"]
                # 치환되지 않은 플레이스홀더가 없어야 함
                assert "{" not in reason, f"locale={loc}, key={key}: unresolved placeholder in '{reason}'"

    def test_gogyo_locale_display(self, use_case: PowerStoneRecommendationUseCase):
        """오행 표시명이 locale에 따라 적절히 변환된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result_ja = use_case.execute(main_star=1, directions=directions, locale="ja")
        result_ko = use_case.execute(main_star=1, directions=directions, locale="ko")
        # star=1 → 水, ja:"水" ko:"수"
        assert result_ja["base_stone"]["gogyo"] == "水"
        assert result_ko["base_stone"]["gogyo"] == "수"


# ══════════════════════════════════════════════════════
# 에러 전파
# ══════════════════════════════════════════════════════

class TestNoAuspiciousDirection:
    def test_no_auspicious_returns_none_monthly(self, use_case: PowerStoneRecommendationUseCase):
        """길방위가 없으면 monthly_stone=None, protection_stone은 정상 반환."""
        directions = _make_directions(
            auspicious={},  # 모두 False
            marks={"north": ["five_yellow"]},
        )
        result = use_case.execute(main_star=1, directions=directions)
        assert result["monthly_stone"] is None
        assert result["protection_stone"] is not None
        assert "stone_id" in result["protection_stone"]
