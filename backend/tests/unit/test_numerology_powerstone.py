"""수비술 파워스톤 카탈로그 · 리포지토리 · 엔진 유닛 테스트.

Issue #128: DRY 개선 — 레이어 상수, assertion 헬퍼, master number 상수 추출
"""
import pytest

from apps.reading.powerstone.domain.value_objects.numerology_powerstone import (
    NumerologyPowerStoneResult,
    NumerologyStone,
    NumerologyStoneRecommendation,
)
from apps.reading.powerstone.infrastructure.persistence.numerology_powerstone_repository import (
    NumerologyPowerStoneRepository,
)
from apps.reading.powerstone.domain.services.numerology_powerstone_engine import (
    NumerologyPowerStoneEngine,
)


# ── 상수 (DRY: 7+ 반복 방지) ────────────────────────────

STANDARD_LAYERS = ("overall", "health", "wealth", "love")
ALL_LAYERS = (*STANDARD_LAYERS, "yearly")
MASTER_NUMBERS = (11, 22, 33)
MASTER_BASE_PAIRS = ((11, 2), (22, 4), (33, 6))


# ── assertion 헬퍼 (DRY: 동일 검증 패턴 4+ 반복 방지) ────

def assert_valid_recommendation(result: NumerologyPowerStoneResult) -> None:
    """NumerologyPowerStoneResult의 기본 구조를 검증."""
    assert result.planet
    for layer in (result.overall, result.health, result.wealth, result.love):
        assert isinstance(layer, NumerologyStoneRecommendation)
        assert isinstance(layer.primary, NumerologyStone)
        assert isinstance(layer.secondary, NumerologyStone)


def assert_mapping_has_layers(mapping: dict, layers: tuple) -> None:
    """매핑 dict에 지정된 레이어와 primary/secondary가 존재하는지 검증."""
    assert "planet" in mapping
    for layer in layers:
        assert layer in mapping
        assert "primary" in mapping[layer]
        assert "secondary" in mapping[layer]


def assert_mapping_stone_refs_valid(
    repo: NumerologyPowerStoneRepository, mapping: dict, layers: tuple,
) -> None:
    """매핑에 참조된 모든 stone_id가 실제 카탈로그에 존재하는지 검증."""
    for layer in layers:
        for role in ("primary", "secondary"):
            stone_id = mapping[layer][role]
            stone = repo.get_stone(stone_id)
            assert stone.id == stone_id


# ══════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def repo() -> NumerologyPowerStoneRepository:
    """실제 JSON 카탈로그를 로드하는 리포지토리."""
    return NumerologyPowerStoneRepository()


@pytest.fixture(scope="module")
def engine(repo: NumerologyPowerStoneRepository) -> NumerologyPowerStoneEngine:
    """엔진 인스턴스."""
    return NumerologyPowerStoneEngine(repo)


# ══════════════════════════════════════════════════════════
# NumerologyStone VO Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyStone:
    def test_get_name_ja(self):
        stone = NumerologyStone(id="ruby", names={"ja": "ルビー", "ko": "루비"}, description={"ja": "情熱の石"})
        assert stone.get_name("ja") == "ルビー"

    def test_get_name_fallback_to_ja(self):
        stone = NumerologyStone(id="ruby", names={"ja": "ルビー"}, description={"ja": "情熱の石"})
        assert stone.get_name("zh") == "ルビー"  # 존재하지 않는 locale → ja fallback

    def test_get_name_fallback_to_first(self):
        stone = NumerologyStone(id="ruby", names={"ko": "루비"}, description={"ko": "열정의 돌"})
        assert stone.get_name("zh") == "루비"  # ja도 없으면 첫 번째 값

    def test_get_description(self):
        stone = NumerologyStone(id="ruby", names={"ja": "ルビー"}, description={"ja": "情熱の石", "ko": "열정의 돌"})
        assert stone.get_description("ko") == "열정의 돌"

    def test_empty_names_raises(self):
        with pytest.raises(ValueError, match="최소 1개"):
            NumerologyStone(id="x", names={}, description={"ja": "test"})

    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="최소 1개"):
            NumerologyStone(id="x", names={"ja": "テスト"}, description={})


# ══════════════════════════════════════════════════════════
# Repository Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyPowerStoneRepository:
    def test_all_numbers_loaded(self, repo):
        """1~9 모든 숫자가 카탈로그에 존재하는지 검증."""
        for n in range(1, 10):
            assert_mapping_has_layers(repo.get_mapping(n), STANDARD_LAYERS)

    def test_master_numbers_loaded(self, repo):
        """마스터넘버(11/22/33)가 카탈로그에 존재하는지 검증."""
        for n in MASTER_NUMBERS:
            assert_mapping_has_layers(repo.get_mapping(n), ALL_LAYERS)

    def test_get_stone_exists(self, repo):
        stone = repo.get_stone("ruby")
        assert isinstance(stone, NumerologyStone)
        assert stone.id == "ruby"
        assert "ja" in stone.names

    def test_get_stone_nonexistent_raises(self, repo):
        with pytest.raises(ValueError, match="존재하지 않는"):
            repo.get_stone("nonexistent_stone")

    def test_get_mapping_invalid_number_raises(self, repo):
        with pytest.raises(ValueError, match="유효하지 않은"):
            repo.get_mapping(0)
        with pytest.raises(ValueError, match="유효하지 않은"):
            repo.get_mapping(10)

    @pytest.mark.parametrize("number", range(1, 10))
    def test_mapping_stone_refs_valid(self, repo, number):
        """매핑에 참조된 모든 stone_id 가 실제 존재하는지 검증."""
        assert_mapping_stone_refs_valid(repo, repo.get_mapping(number), STANDARD_LAYERS)

    @pytest.mark.parametrize("number", MASTER_NUMBERS)
    def test_master_mapping_stone_refs_valid(self, repo, number):
        """마스터넘버 매핑에 참조된 모든 stone_id 가 실제 존재하는지 검증."""
        assert_mapping_stone_refs_valid(repo, repo.get_mapping(number), ALL_LAYERS)

    @pytest.mark.parametrize("stone_id", ["labradorite", "fluorite", "clear_quartz", "smoky_quartz"])
    def test_new_stones_exist(self, repo, stone_id):
        """신규 추가 스톤이 카탈로그에 존재하는지 검증."""
        stone = repo.get_stone(stone_id)
        assert stone.id == stone_id
        assert stone.get_name("ja")
        assert stone.get_name("ko")
        assert stone.get_name("en")


# ══════════════════════════════════════════════════════════
# Engine Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyPowerStoneEngine:
    @pytest.mark.parametrize("number", range(1, 10))
    def test_recommend_all_numbers(self, engine, number):
        """1~9 모든 숫자에 대해 recommend() 가 정상 동작하는지 검증."""
        result = engine.recommend(number)
        assert isinstance(result, NumerologyPowerStoneResult)
        assert result.life_path_number == number
        assert_valid_recommendation(result)

    def test_recommend_number_1_details(self, engine):
        """숫자 1(태양)의 추천 디테일 검증."""
        result = engine.recommend(1)
        assert result.planet == "sun"
        assert result.overall.primary.id == "ruby"
        assert result.overall.secondary.id == "garnet"
        assert result.health.primary.id == "sunstone"
        assert result.wealth.primary.id == "yellow_sapphire"
        assert result.love.primary.id == "diamond"

    def test_recommend_invalid_number_raises(self, engine):
        with pytest.raises(ValueError):
            engine.recommend(0)
        with pytest.raises(ValueError):
            engine.recommend(10)

    @pytest.mark.parametrize("locale", ["ja", "ko", "en"])
    def test_recommend_as_dict_locales(self, engine, locale):
        """각 locale에서 dict 직렬화가 정상 동작하는지 검증."""
        result = engine.recommend_as_dict(1, locale=locale)
        assert result["life_path_number"] == 1
        assert result["planet"] == "sun"
        for layer_key in STANDARD_LAYERS:
            layer = result[layer_key]
            assert "primary" in layer
            assert "secondary" in layer
            assert layer["primary"]["stone_name"]
            assert layer["primary"]["description"]

    def test_recommend_as_dict_structure(self, engine):
        """dict 직렬화 구조 검증."""
        result = engine.recommend_as_dict(5, locale="ko")
        assert result["life_path_number"] == 5
        assert result["planet"] == "mercury"
        overall = result["overall"]
        assert overall["layer"] == "overall"
        assert overall["primary"]["stone_id"] == "emerald"
        assert overall["primary"]["stone_name"] == "에메랄드"
        assert "description" in overall["primary"]
        assert overall["secondary"]["stone_id"] == "peridot"


# ══════════════════════════════════════════════════════════
# Yearly Layer Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyPowerStoneEngineYearly:
    """Personal Year Number 기반 yearly 레이어 테스트."""

    @pytest.mark.parametrize("number", range(1, 10))
    def test_recommend_with_yearly_layer(self, engine, number):
        """1~9 모든 PYN에 대해 yearly 레이어가 포함되는지 검증."""
        result = engine.recommend(number, personal_year_number=number)
        assert result.yearly is not None
        assert isinstance(result.yearly, NumerologyStoneRecommendation)
        assert result.yearly.layer == "yearly"
        assert isinstance(result.yearly.primary, NumerologyStone)
        assert isinstance(result.yearly.secondary, NumerologyStone)
        assert result.personal_year_number == number

    def test_recommend_without_pyn_no_yearly(self, engine):
        """PYN 미제공 시 yearly 레이어 없음."""
        result = engine.recommend(1)
        assert result.yearly is None
        assert result.personal_year_number is None

    def test_recommend_as_dict_with_yearly(self, engine):
        """dict 직렬화에서 yearly + personal_year_number 포함 검증."""
        result = engine.recommend_as_dict(3, locale="ja", personal_year_number=5)
        assert "yearly" in result
        assert result["yearly"]["layer"] == "yearly"
        assert result["yearly"]["primary"]["stone_id"]
        assert result["yearly"]["secondary"]["stone_id"]
        assert result["personal_year_number"] == 5

    def test_pyn_out_of_range_raises(self, engine):
        """PYN 범위(1~9, 11/22/33) 벗어나면 ValueError."""
        with pytest.raises(ValueError, match="1~9"):
            engine.recommend(1, personal_year_number=0)
        with pytest.raises(ValueError, match="1~9"):
            engine.recommend(1, personal_year_number=10)

    def test_pyn_invalid_type_raises(self, engine):
        """PYN 타입 오류 시 ValueError."""
        with pytest.raises(ValueError, match="1~9"):
            engine.recommend(1, personal_year_number="3")  # type: ignore
        with pytest.raises(ValueError, match="1~9"):
            engine.recommend(1, personal_year_number=3.5)  # type: ignore


# ══════════════════════════════════════════════════════════
# Master Number Tests (전용 매핑)
# ══════════════════════════════════════════════════════════

class TestMasterNumberSupport:
    """Master Number (11/22/33) 전용 매핑 테스트."""

    @pytest.mark.parametrize("master", MASTER_NUMBERS)
    def test_recommend_master_number_returns_result(self, engine, master):
        """Master Number가 정상적으로 추천 결과를 반환하는지 검증."""
        result = engine.recommend(master)
        assert isinstance(result, NumerologyPowerStoneResult)
        assert result.life_path_number == master
        assert_valid_recommendation(result)

    @pytest.mark.parametrize("master,base", MASTER_BASE_PAIRS)
    def test_recommend_master_number_has_unique_stones(self, engine, master, base):
        """Master Number가 base number와 다른 고유한 스톤을 반환하는지 검증."""
        master_result = engine.recommend(master)
        base_result = engine.recommend(base)

        assert master_result.life_path_number == master

        differences = [
            f"{name}.{role}"
            for name in STANDARD_LAYERS
            for role in ("primary", "secondary")
            if getattr(getattr(master_result, name), role).id
            != getattr(getattr(base_result, name), role).id
        ]
        assert len(differences) > 0, (
            f"Master {master} 는 base {base} 와 전용 매핑이 달라야 합니다"
        )

    def test_master_11_details(self, engine):
        """Master Number 11 (직관의 빛) 전용 스톤 검증."""
        result = engine.recommend(11)
        assert result.planet == "neptune"
        assert result.overall.primary.id == "amethyst"
        assert result.overall.secondary.id == "moonstone"
        assert result.health.primary.id == "clear_quartz"
        assert result.health.secondary.id == "labradorite"

    def test_master_22_details(self, engine):
        """Master Number 22 (마스터 빌더) 전용 스톤 검증."""
        result = engine.recommend(22)
        assert result.planet == "uranus"
        assert result.overall.primary.id == "clear_quartz"
        assert result.overall.secondary.id == "citrine"
        assert result.health.primary.id == "smoky_quartz"

    def test_master_33_details(self, engine):
        """Master Number 33 (마스터 티처) 전용 스톤 검증."""
        result = engine.recommend(33)
        assert result.planet == "neptune"
        assert result.overall.primary.id == "rose_quartz"
        assert result.overall.secondary.id == "amethyst"
        assert result.health.primary.id == "amethyst"

    @pytest.mark.parametrize("master", MASTER_NUMBERS)
    def test_recommend_as_dict_master_number(self, engine, master):
        """Master Number dict 직렬화 정상 동작."""
        result = engine.recommend_as_dict(master, locale="ja")
        assert result["life_path_number"] == master
        assert result["planet"]
        for layer_key in STANDARD_LAYERS:
            assert layer_key in result

    @pytest.mark.parametrize("master", MASTER_NUMBERS)
    def test_pyn_master_number_yearly(self, engine, master):
        """Master Number PYN도 전용 yearly 레이어 정상 동작."""
        result = engine.recommend(1, personal_year_number=master)
        assert result.yearly is not None
        assert result.personal_year_number == master
        assert isinstance(result.yearly.primary, NumerologyStone)
        assert isinstance(result.yearly.secondary, NumerologyStone)

    @pytest.mark.parametrize("master,base", MASTER_BASE_PAIRS)
    def test_pyn_master_number_has_unique_yearly(self, engine, master, base):
        """Master Number PYN이 base number PYN과 다른 yearly 스톤을 반환하는지 검증."""
        master_result = engine.recommend(1, personal_year_number=master)
        base_result = engine.recommend(1, personal_year_number=base)
        assert master_result.yearly is not None
        assert base_result.yearly is not None
        has_diff = (
            master_result.yearly.primary.id != base_result.yearly.primary.id
            or master_result.yearly.secondary.id != base_result.yearly.secondary.id
        )
        assert has_diff, (
            f"Master PYN {master} 의 yearly 가 base PYN {base} 와 달라야 합니다"
        )
