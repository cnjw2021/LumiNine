"""PowerStoneMatchingEngine 단위 테스트.

커버리지:
  - L1: 본명성 1~9 → 올바른 기본석
  - L2: 길방위 없음 → NoAuspiciousDirectionError
  - L2: 상성 SOJO 방위 우선 선택
  - L2: 동순위 → 방위 고정 우선순위
  - L3: 五黄殺 > 暗剣殺 우선순위
  - 중복: L1=L2 동일 오행 → 부석 대체
  - 중복: 3개 전부 같은 오행 → 부석 순차 대체
  - 결과: 항상 3개의 서로 다른 stone id 반환
"""
from __future__ import annotations

import pytest

from apps.ninestarki.domain.exceptions import (
    NoAuspiciousDirectionError,
    PowerStoneMatchingError,
)
from apps.ninestarki.domain.services.gogyo_service import GogyoService
from apps.ninestarki.domain.services.powerstone_matching_engine import (
    PowerStoneMatchingEngine,
)
from apps.ninestarki.domain.value_objects.powerstone import PowerStoneResult
from apps.ninestarki.infrastructure.persistence.powerstone_repository import (
    PowerStoneRepository,
)


# ── 픽스처 ────────────────────────────────────────────

@pytest.fixture
def engine() -> PowerStoneMatchingEngine:
    return PowerStoneMatchingEngine(
        gogyo_service=GogyoService(),
        stone_repo=PowerStoneRepository(),
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
# recommend() 기본 동작
# ══════════════════════════════════════════════════════

class TestRecommendBasic:
    def test_returns_powerstone_result(self, engine: PowerStoneMatchingEngine):
        """recommend() 는 PowerStoneResult 를 반환한다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert isinstance(result, PowerStoneResult)

    def test_result_has_three_stones(self, engine: PowerStoneMatchingEngine):
        """결과에 base, monthly, protection 3개 스톤이 존재한다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert result.base_stone is not None
        assert result.monthly_stone is not None
        assert result.protection_stone is not None

    def test_three_distinct_stone_ids(self, engine: PowerStoneMatchingEngine):
        """결과의 3개 스톤은 항상 서로 다른 id를 갖는다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        ids = {result.base_stone.stone.id, result.monthly_stone.stone.id, result.protection_stone.stone.id}
        assert len(ids) == 3


# ══════════════════════════════════════════════════════
# Layer 1: 기본석
# ══════════════════════════════════════════════════════

class TestLayer1BaseStone:
    @pytest.mark.parametrize("star, expected_id", [
        (1, "aquamarine"), (2, "citrine"), (3, "emerald"),
        (4, "peridot"), (5, "tigers_eye"), (6, "clear_quartz"),
        (7, "rose_quartz"), (8, "smoky_quartz"), (9, "garnet"),
    ])
    def test_base_stone_by_star(
        self, engine: PowerStoneMatchingEngine, star: int, expected_id: str,
    ):
        """본명성 1~9 → 올바른 기본석."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=star, directions=directions)
        assert result.base_stone.stone.id == expected_id

    def test_base_stone_reason_key(self, engine: PowerStoneMatchingEngine):
        """기본석 reason_key 는 'reason.base' 이다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert result.base_stone.reason_key == "reason.base"


# ══════════════════════════════════════════════════════
# Layer 2: 월운석
# ══════════════════════════════════════════════════════

class TestLayer2MonthlyStone:
    def test_no_auspicious_raises(self, engine: PowerStoneMatchingEngine):
        """길방위가 없으면 NoAuspiciousDirectionError."""
        directions = _make_directions(
            auspicious={},  # 모두 False
            marks={"north": ["five_yellow"]},
        )
        with pytest.raises(NoAuspiciousDirectionError):
            engine.recommend(main_star=1, directions=directions)

    def test_sojo_direction_preferred(self, engine: PowerStoneMatchingEngine):
        """상생(SOJO) 방위가 비화(HIWA)보다 우선 선택된다."""
        # star=9 → 火, south=火(HIWA), east=木(SOJO: 木生火)
        directions = _make_directions(
            auspicious={"south": True, "east": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=9, directions=directions)
        assert result.monthly_stone.reason_params["direction_key"] == "direction.east"

    def test_direction_priority_tiebreak(self, engine: PowerStoneMatchingEngine):
        """동순위 상성일 때 방위 고정 우선순위로 선택."""
        # star=1 → 水
        # south=火(SOKOKU), east=木(SOJO: 水生木)
        # southeast=木(SOJO: 水生木) — east vs southeast = east 우선
        directions = _make_directions(
            auspicious={"east": True, "southeast": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert result.monthly_stone.reason_params["direction_key"] == "direction.east"

    def test_monthly_reason_params(self, engine: PowerStoneMatchingEngine):
        """월운석 reason_params 에 direction, element 포함."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert "direction_key" in result.monthly_stone.reason_params
        assert "element_key" in result.monthly_stone.reason_params


# ══════════════════════════════════════════════════════
# Layer 3: 호신석
# ══════════════════════════════════════════════════════

class TestLayer3ProtectionStone:
    def test_five_yellow_over_dark_sword(self, engine: PowerStoneMatchingEngine):
        """五黄殺이 暗剣殺보다 우선."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={
                "north": ["dark_sword"],
                "east": ["five_yellow"],
            },
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert result.protection_stone.reason_params["threat_key"] == "threat.five_yellow"
        assert result.protection_stone.reason_params["direction_key"] == "direction.east"

    def test_protection_uses_counter_gogyo(self, engine: PowerStoneMatchingEngine):
        """호신석은 흉살 방위의 상극 오행 스톤."""
        # east=木 → 상극은 金 → 주석은 clear_quartz
        directions = _make_directions(
            auspicious={"south": True},
            marks={"east": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        # 木의 상극은 金 (金剋木)
        assert result.protection_stone.stone.gogyo.value == "金"

    def test_protection_reason_params(self, engine: PowerStoneMatchingEngine):
        """호신석 reason_params 에 threat, direction, threat_element, counter_element 포함."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": ["five_yellow"]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        params = result.protection_stone.reason_params
        assert "threat_key" in params
        assert "direction_key" in params
        assert "threat_element_key" in params
        assert "counter_element_key" in params

    def test_no_threats_raises(self, engine: PowerStoneMatchingEngine):
        """흉살이 없으면 PowerStoneMatchingError."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={},  # 흉살 없음
        )
        with pytest.raises(PowerStoneMatchingError) as exc_info:
            engine.recommend(main_star=1, directions=directions)
        assert exc_info.value.code == "NO_THREAT_FOUND"

    @pytest.mark.parametrize("alias_code, canonical_code", [
        ("compatibility_matrix", "bad_star"),
        ("main_star_opposite", "main_opposite"),
        ("month_star_opposite", "month_opposite"),
    ])
    def test_direction_fortune_alias_codes(
        self,
        engine: PowerStoneMatchingEngine,
        alias_code: str,
        canonical_code: str,
    ):
        """direction-fortune 소스의 alias 코드가 canonical 코드로 정규화된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={"north": [alias_code]},
        )
        result = engine.recommend(main_star=1, directions=directions)
        # alias 코드는 엔진에서 canonical 코드로 정규화되어 threat.{canonical_code} 로 노출된다.
        assert result.protection_stone.reason_params["threat_key"] == f"threat.{canonical_code}"

    def test_alias_severity_ordering(self, engine: PowerStoneMatchingEngine):
        """five_yellow(1) > compatibility_matrix(7) 우선순위 정상 동작."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={
                "north": ["compatibility_matrix"],
                "east": ["five_yellow"],
            },
        )
        result = engine.recommend(main_star=1, directions=directions)
        assert result.protection_stone.reason_params["threat_key"] == "threat.five_yellow"

    def test_neutral_direction_excluded_from_l3(self, engine: PowerStoneMatchingEngine):
        """중립(is_auspicious=None) 방위는 L3 흉살 스캔에서 제외된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={
                "east": ["compatibility_matrix"],  # 이 방위를 neutral 으로 설정
                "north": ["dark_sword"],             # 이 방위는 False(=흉)
            },
        )
        # east 방위를 neutral(None)로 덮어쓰기
        directions["east"]["is_auspicious"] = None
        result = engine.recommend(main_star=1, directions=directions)
        # neutral 된 east 는 제외, north 의 dark_sword 가 선택됨
        assert result.protection_stone.reason_params["threat_key"] == "threat.dark_sword"
        assert result.protection_stone.reason_params["direction_key"] == "direction.north"

    def test_unknown_sentinel_mark_skipped(self, engine: PowerStoneMatchingEngine):
        """미등록 sentinel mark(no_dark_sword_center_five 등)는 무시된다."""
        directions = _make_directions(
            auspicious={"south": True},
            marks={
                "east": ["no_dark_sword_center_five"],  # 미등록 코드
                "north": ["dark_sword"],                 # 등록된 코드
            },
        )
        result = engine.recommend(main_star=1, directions=directions)
        # 미등록 east 는 무시, north 의 dark_sword 가 선택됨
        assert result.protection_stone.reason_params["threat_key"] == "threat.dark_sword"


# ══════════════════════════════════════════════════════
# 중복 회피
# ══════════════════════════════════════════════════════

class TestDuplicateAvoidance:
    def test_same_gogyo_l1_l2_uses_secondary(
        self, engine: PowerStoneMatchingEngine,
    ):
        """L1과 L2가 같은 오행이면 L2는 부석으로 대체."""
        # star=3 → 木(emerald), east=木 → L2도 木이면 부석 사용
        directions = _make_directions(
            auspicious={"east": True},
            marks={"south": ["five_yellow"]},
        )
        result = engine.recommend(main_star=3, directions=directions)
        # L1 = emerald(木 주석), L2 = 木 부석 중 하나
        assert result.base_stone.stone.id == "emerald"
        assert result.monthly_stone.stone.gogyo.value == "木"
        assert result.monthly_stone.stone.id != "emerald"
        assert result.monthly_stone.stone.is_primary is False

    def test_all_three_distinct(self, engine: PowerStoneMatchingEngine):
        """모든 경우에 3개 스톤의 id가 서로 다르다."""
        test_cases = [
            (1, {"south": True}, {"north": ["five_yellow"]}),
            (3, {"east": True}, {"south": ["five_yellow"]}),
            (9, {"south": True}, {"east": ["dark_sword"]}),
            (5, {"west": True}, {"north": ["main_star"]}),
        ]
        for star, ausp, marks in test_cases:
            directions = _make_directions(auspicious=ausp, marks=marks)
            result = engine.recommend(main_star=star, directions=directions)
            ids = {
                result.base_stone.stone.id,
                result.monthly_stone.stone.id,
                result.protection_stone.stone.id,
            }
            assert len(ids) == 3, f"star={star}: duplicate ids found: {ids}"
