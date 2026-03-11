"""SixLayerPowerStoneUseCase 단위 테스트.

birth_date 유무에 따른 3-Layer / 6-Layer / 7-Layer 분기,
응답 구조, traits/yearly 포함 여부를 검증한다.

Issue #128: fixture → conftest.py, @patch 상수 DRY, pytest.fixture 패턴
"""
from unittest.mock import MagicMock, patch

import pytest

from apps.reading.powerstone.use_cases.six_layer_powerstone_use_case import (
    SixLayerPowerStoneUseCase,
)
from tests.unit.powerstone_test_fixtures import (
    DUMMY_DIRECTIONS,
    PATCH_LIFE_PATH,
    PATCH_PERSONAL_YEAR,
    PATCH_TRAITS,
    make_numerology_result,
)


# ── pytest fixture ────────────────────────────────────

@pytest.fixture
def use_case(mock_stone_uc, mock_engine) -> SixLayerPowerStoneUseCase:
    return SixLayerPowerStoneUseCase(
        stone_use_case=mock_stone_uc,
        numerology_engine=mock_engine,
    )


# ══════════════════════════════════════════════════════
# 3-Layer 분기 테스트
# ══════════════════════════════════════════════════════

class TestThreeLayerBranch:
    """birth_date 미제공 시 기존 3-Layer 응답 반환."""

    def test_no_birth_date_returns_3_layer(self, use_case, mock_stone_uc, mock_engine):
        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS, locale="ja", birth_date=None,
        )

        assert "base_stone" in result
        assert "monthly_stone" in result
        assert "protection_stone" in result
        assert "overall_stone" not in result
        assert "life_path_number" not in result

        mock_stone_uc.execute.assert_called_once()
        mock_engine.recommend_as_dict.assert_not_called()


# ══════════════════════════════════════════════════════
# 6-Layer 분기 테스트
# ══════════════════════════════════════════════════════

class TestSixLayerBranch:
    """birth_date 제공 시 6-Layer 응답 반환."""

    @patch(PATCH_LIFE_PATH)
    def test_with_birth_date_returns_6_layer(self, mock_calc, use_case):
        mock_calc.return_value = MagicMock(number=7)

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="1990-05-15",
        )

        for key in ("overall_stone", "health_stone", "wealth_stone",
                     "love_stone", "monthly_stone", "protection_stone"):
            assert key in result, f"Missing key: {key}"

        assert result["life_path_number"] == 7
        assert result["planet"] == "ketu"

        overall = result["overall_stone"]
        for field in ("stone_id", "stone_name", "layer", "description", "secondary"):
            assert field in overall

        monthly = result["monthly_stone"]
        assert monthly["stone_id"] == "rose_quartz"
        assert monthly["layer"] == "月運石"

    @patch(PATCH_LIFE_PATH)
    def test_base_stone_excluded_in_6_layer(self, mock_calc, use_case):
        mock_calc.return_value = MagicMock(number=1)

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="2000-01-01",
        )

        assert "base_stone" not in result
        assert "overall_stone" in result

    @patch(PATCH_LIFE_PATH)
    def test_6_layer_no_target_year_excludes_yearly(self, mock_calc, use_case):
        mock_calc.return_value = MagicMock(number=3)

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="1990-03-15",
        )

        assert "yearly_stone" not in result or result.get("yearly_stone") is None
        assert "personal_year_number" not in result or result.get("personal_year_number") is None


# ══════════════════════════════════════════════════════
# 7-Layer 분기 테스트
# ══════════════════════════════════════════════════════

class TestSevenLayerBranch:
    """target_year 제공 시 7-Layer 응답 (yearly_stone 포함)."""

    @patch(PATCH_PERSONAL_YEAR)
    @patch(PATCH_LIFE_PATH)
    def test_both_engines_called(self, mock_calc, mock_pyn, use_case, mock_stone_uc, mock_engine):
        mock_calc.return_value = MagicMock(number=3)
        mock_pyn.return_value = MagicMock(number=2)

        use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ko", birth_date="1995-12-25", target_year=2026,
        )

        # 구성기학 호출 검증
        mock_stone_uc.execute.assert_called_once_with(
            main_star=5, directions=DUMMY_DIRECTIONS, locale="ko",
        )

        # 수비술 호출 검증
        mock_calc.assert_called_once_with("1995-12-25")
        mock_pyn.assert_called_once_with("1995-12-25", 2026)
        mock_engine.recommend_as_dict.assert_called_once_with(
            life_path_number=3, locale="ko", personal_year_number=2,
        )

    @patch(PATCH_PERSONAL_YEAR)
    @patch(PATCH_LIFE_PATH)
    def test_7_layer_includes_yearly_stone(self, mock_calc, mock_pyn, use_case, mock_engine):
        mock_calc.return_value = MagicMock(number=3)
        mock_pyn.return_value = MagicMock(number=5)

        numerology_with_yearly = make_numerology_result()
        numerology_with_yearly["yearly"] = {
            "layer": "yearly",
            "primary": {
                "stone_id": "citrine", "stone_name": "シトリン",
                "description": "年エネルギー石",
            },
            "secondary": {
                "stone_id": "garnet", "stone_name": "ガーネット",
                "description": "補助年運石",
            },
        }
        numerology_with_yearly["personal_year_number"] = 5
        mock_engine.recommend_as_dict.return_value = numerology_with_yearly

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="1990-03-15", target_year=2026,
        )

        assert "yearly_stone" in result
        assert result["yearly_stone"]["stone_id"] == "citrine"
        assert result["personal_year_number"] == 5


# ══════════════════════════════════════════════════════
# Traits / Helper 테스트
# ══════════════════════════════════════════════════════

class TestTraitsAndHelpers:
    """traits 포함, format_numerology_layer, merge_six_layer_partial 검증."""

    def test_format_numerology_layer_structure(self):
        layer_data = make_numerology_result()["overall"]
        formatted = SixLayerPowerStoneUseCase.format_numerology_layer(layer_data)

        assert formatted["stone_id"] == "cats_eye"
        assert formatted["stone_name"] == "キャッツアイ"
        assert formatted["layer"] == "overall"
        assert formatted["description"] == "直感を高める"
        assert formatted["secondary"]["stone_id"] == "amethyst"
        assert formatted["secondary"]["stone_name"] == "アメシスト"
        assert formatted["secondary"]["description"] == "精神の安定"

    def test_merge_six_layer_partial_returns_numerology_only(self, use_case):
        numerology = make_numerology_result()
        result = use_case.merge_six_layer_partial(numerology)

        for key in ("overall_stone", "health_stone", "wealth_stone", "love_stone"):
            assert key in result and result[key] is not None

            layer_data = result[key]
            assert isinstance(layer_data, dict)
            assert "stone_id" in layer_data
            assert "stone_name" in layer_data
            assert "layer" in layer_data
            assert "description" in layer_data
            assert "secondary" in layer_data

            assert isinstance(layer_data["secondary"], dict)
            assert "stone_id" in layer_data["secondary"]

            expected_layer = key.replace("_stone", "")
            assert layer_data["layer"] == expected_layer

        assert result["monthly_stone"] is None
        assert result["protection_stone"] is None
        assert result["life_path_number"] == 7
        assert result["planet"] == "ketu"

    @patch(PATCH_TRAITS)
    @patch(PATCH_LIFE_PATH)
    def test_traits_included_in_response(self, mock_calc, mock_traits, use_case):
        mock_calc.return_value = MagicMock(number=1)
        mock_traits.return_value = {"title": "リーダー", "traits": "独立心が強い"}

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="1990-01-01",
        )

        assert result["title"] == "リーダー"
        assert result["traits"] == "独立心が強い"

    @patch(PATCH_TRAITS)
    @patch(PATCH_LIFE_PATH)
    def test_traits_absent_when_not_found(self, mock_calc, mock_traits, use_case):
        mock_calc.return_value = MagicMock(number=1)
        mock_traits.return_value = None

        result = use_case.execute(
            main_star=5, directions=DUMMY_DIRECTIONS,
            locale="ja", birth_date="1990-01-01",
        )

        assert "title" not in result
        assert "traits" not in result
