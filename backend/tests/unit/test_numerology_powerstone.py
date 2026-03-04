"""수비술 파워스톤 카탈로그 · 리포지토리 · 엔진 유닛 테스트."""
import pytest

from apps.ninestarki.domain.value_objects.numerology_powerstone import (
    NumerologyPowerStoneResult,
    NumerologyStone,
    NumerologyStoneRecommendation,
)
from apps.ninestarki.infrastructure.persistence.numerology_powerstone_repository import (
    NumerologyPowerStoneRepository,
)
from apps.ninestarki.domain.services.numerology_powerstone_engine import (
    NumerologyPowerStoneEngine,
)


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


# ══════════════════════════════════════════════════════════
# Repository Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyPowerStoneRepository:
    def test_all_numbers_loaded(self, repo: NumerologyPowerStoneRepository):
        """1~9 모든 숫자가 카탈로그에 존재하는지 검증."""
        for n in range(1, 10):
            mapping = repo.get_mapping(n)
            assert "planet" in mapping
            for layer in ("overall", "health", "wealth", "love"):
                assert layer in mapping
                assert "primary" in mapping[layer]
                assert "secondary" in mapping[layer]

    def test_get_stone_exists(self, repo: NumerologyPowerStoneRepository):
        stone = repo.get_stone("ruby")
        assert isinstance(stone, NumerologyStone)
        assert stone.id == "ruby"
        assert "ja" in stone.names

    def test_get_stone_nonexistent_raises(self, repo: NumerologyPowerStoneRepository):
        with pytest.raises(ValueError, match="존재하지 않는"):
            repo.get_stone("nonexistent_stone")

    def test_get_mapping_invalid_number_raises(self, repo: NumerologyPowerStoneRepository):
        with pytest.raises(ValueError, match="유효하지 않은"):
            repo.get_mapping(0)
        with pytest.raises(ValueError, match="유효하지 않은"):
            repo.get_mapping(10)

    @pytest.mark.parametrize("number", range(1, 10))
    def test_mapping_stone_refs_valid(self, repo: NumerologyPowerStoneRepository, number: int):
        """매핑에 참조된 모든 stone_id 가 실제 존재하는지 검증."""
        mapping = repo.get_mapping(number)
        for layer in ("overall", "health", "wealth", "love"):
            for role in ("primary", "secondary"):
                stone_id = mapping[layer][role]
                stone = repo.get_stone(stone_id)
                assert stone.id == stone_id


# ══════════════════════════════════════════════════════════
# Engine Tests
# ══════════════════════════════════════════════════════════

class TestNumerologyPowerStoneEngine:
    @pytest.mark.parametrize("number", range(1, 10))
    def test_recommend_all_numbers(self, engine: NumerologyPowerStoneEngine, number: int):
        """1~9 모든 숫자에 대해 recommend() 가 정상 동작하는지 검증."""
        result = engine.recommend(number)
        assert isinstance(result, NumerologyPowerStoneResult)
        assert result.life_path_number == number
        assert result.planet  # 빈 문자열이 아닌지
        for layer in (result.overall, result.health, result.wealth, result.love):
            assert isinstance(layer, NumerologyStoneRecommendation)
            assert isinstance(layer.primary, NumerologyStone)
            assert isinstance(layer.secondary, NumerologyStone)

    def test_recommend_number_1_details(self, engine: NumerologyPowerStoneEngine):
        """숫자 1(태양)의 추천 디테일 검증."""
        result = engine.recommend(1)
        assert result.planet == "sun"
        assert result.overall.primary.id == "ruby"
        assert result.overall.secondary.id == "garnet"
        assert result.health.primary.id == "sunstone"
        assert result.wealth.primary.id == "yellow_sapphire"
        assert result.love.primary.id == "diamond"

    def test_recommend_invalid_number_raises(self, engine: NumerologyPowerStoneEngine):
        with pytest.raises(ValueError):
            engine.recommend(0)
        with pytest.raises(ValueError):
            engine.recommend(10)

    @pytest.mark.parametrize("locale", ["ja", "ko", "en"])
    def test_recommend_as_dict_locales(self, engine: NumerologyPowerStoneEngine, locale: str):
        """각 locale에서 dict 직렬화가 정상 동작하는지 검증."""
        result = engine.recommend_as_dict(1, locale=locale)
        assert result["life_path_number"] == 1
        assert result["planet"] == "sun"
        for layer_key in ("overall", "health", "wealth", "love"):
            layer = result[layer_key]
            assert "primary" in layer
            assert "secondary" in layer
            assert layer["primary"]["stone_name"]  # 빈 문자열이 아닌지
            assert layer["primary"]["description"]

    def test_recommend_as_dict_structure(self, engine: NumerologyPowerStoneEngine):
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
