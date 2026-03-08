"""PowerStoneRepository 단위 테스트.

커버리지:
  - 전체 20종 스톤 로드 확인
  - 오행별 주석(1), 부석(3) 분류 정확성
  - get_base_stone_for_star 1~9 전체 확인
  - 범위 밖 입력 → PowerStoneMatchingError 발생 확인
"""
from __future__ import annotations

import pytest

from apps.fortunetelling.shared.domain.exceptions import PowerStoneMatchingError
from apps.fortunetelling.ninestarki.domain.value_objects.gogyo import Gogyo
from apps.fortunetelling.powerstone.domain.value_objects.powerstone import PowerStone
from apps.fortunetelling.powerstone.infrastructure.persistence.powerstone_repository import (
    PowerStoneRepository,
)


@pytest.fixture
def repo() -> PowerStoneRepository:
    return PowerStoneRepository()


# ══════════════════════════════════════════════════════
# 전체 카탈로그 로드
# ══════════════════════════════════════════════════════

class TestCatalogLoad:
    def test_total_stone_count(self, repo: PowerStoneRepository):
        """카탈로그에 20종 스톤이 로드되어야 한다."""
        primary_count = len(list(Gogyo))
        secondary_count = sum(len(repo.get_secondaries_by_gogyo(g)) for g in Gogyo)
        assert primary_count + secondary_count == 20

    def test_all_five_gogyo_have_primary(self, repo: PowerStoneRepository):
        """모든 5개 오행에 주석이 할당되어야 한다."""
        for gogyo in Gogyo:
            stone = repo.get_primary_by_gogyo(gogyo)
            assert stone.is_primary is True
            assert stone.gogyo == gogyo

    def test_each_gogyo_has_three_secondaries(self, repo: PowerStoneRepository):
        """각 오행에 부석 3개씩 존재해야 한다."""
        for gogyo in Gogyo:
            secs = repo.get_secondaries_by_gogyo(gogyo)
            assert len(secs) == 3
            for s in secs:
                assert s.gogyo == gogyo
                assert s.is_primary is False


# ══════════════════════════════════════════════════════
# get_primary_by_gogyo
# ══════════════════════════════════════════════════════

class TestGetPrimaryByGogyo:
    @pytest.mark.parametrize("gogyo, expected_id", [
        (Gogyo.WATER, "aquamarine"),
        (Gogyo.WOOD, "emerald"),
        (Gogyo.FIRE, "garnet"),
        (Gogyo.EARTH, "citrine"),
        (Gogyo.METAL, "clear_quartz"),
    ])
    def test_primary_stone_ids(self, repo: PowerStoneRepository, gogyo: Gogyo, expected_id: str):
        stone = repo.get_primary_by_gogyo(gogyo)
        assert stone.id == expected_id

    def test_primary_stone_has_names(self, repo: PowerStoneRepository):
        """주석은 3개 locale 의 이름을 보유해야 한다."""
        for gogyo in Gogyo:
            stone = repo.get_primary_by_gogyo(gogyo)
            assert "ja" in stone.names
            assert "ko" in stone.names
            assert "en" in stone.names


# ══════════════════════════════════════════════════════
# get_secondaries_by_gogyo
# ══════════════════════════════════════════════════════

class TestGetSecondariesByGogyo:
    def test_water_secondaries(self, repo: PowerStoneRepository):
        ids = [s.id for s in repo.get_secondaries_by_gogyo(Gogyo.WATER)]
        assert set(ids) == {"lapis_lazuli", "blue_topaz", "onyx"}

    def test_wood_secondaries(self, repo: PowerStoneRepository):
        ids = [s.id for s in repo.get_secondaries_by_gogyo(Gogyo.WOOD)]
        assert set(ids) == {"peridot", "aventurine", "jade"}

    def test_fire_secondaries(self, repo: PowerStoneRepository):
        ids = [s.id for s in repo.get_secondaries_by_gogyo(Gogyo.FIRE)]
        assert set(ids) == {"carnelian", "ruby", "amethyst"}

    def test_earth_secondaries(self, repo: PowerStoneRepository):
        ids = [s.id for s in repo.get_secondaries_by_gogyo(Gogyo.EARTH)]
        assert set(ids) == {"tigers_eye", "yellow_jasper", "smoky_quartz"}

    def test_metal_secondaries(self, repo: PowerStoneRepository):
        ids = [s.id for s in repo.get_secondaries_by_gogyo(Gogyo.METAL)]
        assert set(ids) == {"moonstone", "rose_quartz", "pearl"}

    def test_returns_new_list(self, repo: PowerStoneRepository):
        """반환된 리스트 수정이 내부 상태에 영향 없어야 한다."""
        secs = repo.get_secondaries_by_gogyo(Gogyo.WATER)
        secs.clear()
        assert len(repo.get_secondaries_by_gogyo(Gogyo.WATER)) == 3


# ══════════════════════════════════════════════════════
# get_base_stone_for_star
# ══════════════════════════════════════════════════════

class TestGetBaseStoneForStar:
    @pytest.mark.parametrize("star, expected_id", [
        (1, "aquamarine"),
        (2, "citrine"),
        (3, "emerald"),
        (4, "peridot"),
        (5, "tigers_eye"),
        (6, "clear_quartz"),
        (7, "rose_quartz"),
        (8, "smoky_quartz"),
        (9, "garnet"),
    ])
    def test_star_to_base_stone(self, repo: PowerStoneRepository, star: int, expected_id: str):
        stone = repo.get_base_stone_for_star(star)
        assert stone.id == expected_id

    @pytest.mark.parametrize("invalid_star", [0, 10, -1, 100])
    def test_invalid_star_raises(self, repo: PowerStoneRepository, invalid_star: int):
        with pytest.raises(PowerStoneMatchingError) as exc_info:
            repo.get_base_stone_for_star(invalid_star)
        assert exc_info.value.code == "INVALID_STAR_NUMBER"
        assert exc_info.value.status == 422

    def test_base_stone_is_powerstone(self, repo: PowerStoneRepository):
        """반환 타입이 PowerStone 이어야 한다."""
        for star in range(1, 10):
            stone = repo.get_base_stone_for_star(star)
            assert isinstance(stone, PowerStone)
