"""SixLayerPowerStoneUseCase 단위 테스트.

birth_date 유무에 따른 3-Layer / 6-Layer 분기와
응답 구조를 검증한다.
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

from apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case import (
    SixLayerPowerStoneUseCase,
)


# ── 공통 테스트 데이터 ─────────────────────────────────

def _make_gogyo_result() -> Dict[str, Any]:
    """구성기학 3-Layer 결과 mock."""
    return {
        "base_stone": {
            "stone_id": "citrine",
            "stone_name": "シトリン",
            "layer": "基本石",
            "gogyo": "土",
            "reason": "本命星が五黄土星です",
        },
        "monthly_stone": {
            "stone_id": "rose_quartz",
            "stone_name": "ローズクォーツ",
            "layer": "月運石",
            "gogyo": "火",
            "reason": "月の吉方位: 南",
        },
        "protection_stone": {
            "stone_id": "obsidian",
            "stone_name": "オブシディアン",
            "layer": "守護石",
            "gogyo": "水",
            "reason": "月命星の五行",
        },
    }


def _make_numerology_result() -> Dict[str, Any]:
    """수비술 4-Layer 결과 mock."""
    return {
        "life_path_number": 7,
        "planet": "ketu",
        "overall": {
            "layer": "overall",
            "primary": {
                "stone_id": "cats_eye",
                "stone_name": "キャッツアイ",
                "description": "直感を高める",
            },
            "secondary": {
                "stone_id": "amethyst",
                "stone_name": "アメシスト",
                "description": "精神の安定",
            },
        },
        "health": {
            "layer": "health",
            "primary": {
                "stone_id": "moonstone",
                "stone_name": "ムーンストーン",
                "description": "体のバランス",
            },
            "secondary": {
                "stone_id": "pearl",
                "stone_name": "パール",
                "description": "心身の浄化",
            },
        },
        "wealth": {
            "layer": "wealth",
            "primary": {
                "stone_id": "tigers_eye",
                "stone_name": "タイガーズアイ",
                "description": "金運アップ",
            },
            "secondary": {
                "stone_id": "pyrite",
                "stone_name": "パイライト",
                "description": "財運の安定",
            },
        },
        "love": {
            "layer": "love",
            "primary": {
                "stone_id": "rose_quartz",
                "stone_name": "ローズクォーツ",
                "description": "愛情運アップ",
            },
            "secondary": {
                "stone_id": "rhodonite",
                "stone_name": "ロードナイト",
                "description": "恋愛の安定",
            },
        },
    }


DUMMY_DIRECTIONS = {"north": {"is_auspicious": True}}


# ── 테스트 클래스 ──────────────────────────────────────

class TestSixLayerPowerStoneUseCase:
    """SixLayerPowerStoneUseCase 테스트."""

    def setup_method(self) -> None:
        self.mock_stone_uc = MagicMock()
        self.mock_stone_uc.execute.return_value = _make_gogyo_result()

        self.mock_engine = MagicMock()
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        self.use_case = SixLayerPowerStoneUseCase(
            stone_use_case=self.mock_stone_uc,
            numerology_engine=self.mock_engine,
        )

    # ── birth_date 없으면 기존 3-Layer ────────────────

    def test_no_birth_date_returns_3_layer(self) -> None:
        """birth_date 미제공 시 기존 3-Layer 응답 반환."""
        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date=None,
        )

        # 3-Layer 키 확인
        assert "base_stone" in result
        assert "monthly_stone" in result
        assert "protection_stone" in result

        # 6-Layer 전용 키 없음
        assert "overall_stone" not in result
        assert "life_path_number" not in result

        # 구성기학 유즈케이스만 호출됨
        self.mock_stone_uc.execute.assert_called_once()
        self.mock_engine.recommend_as_dict.assert_not_called()

    # ── birth_date 있으면 6-Layer ─────────────────────

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_with_birth_date_returns_6_layer(self, mock_calc: MagicMock) -> None:
        """birth_date 제공 시 6-Layer 응답 반환."""
        mock_calc.return_value = MagicMock(number=7)

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="1990-05-15",
        )

        # 6-Layer 필수 키 확인
        for key in ("overall_stone", "health_stone", "wealth_stone",
                     "love_stone", "monthly_stone", "protection_stone"):
            assert key in result, f"Missing key: {key}"

        # 메타 정보
        assert result["life_path_number"] == 7
        assert result["planet"] == "ketu"

        # 수비술 레이어 형식 확인
        overall = result["overall_stone"]
        assert "stone_id" in overall
        assert "stone_name" in overall
        assert "layer" in overall
        assert "description" in overall
        assert "secondary" in overall

        # 구성기학 레이어는 기존 형식 유지
        monthly = result["monthly_stone"]
        assert monthly["stone_id"] == "rose_quartz"
        assert monthly["layer"] == "月運石"

    # ── _format_numerology_layer 변환 검증 ─────────────

    def test_format_numerology_layer_structure(self) -> None:
        """수비술 레이어 데이터가 올바른 API 형식으로 변환되는지 검증."""
        layer_data = _make_numerology_result()["overall"]
        formatted = SixLayerPowerStoneUseCase.format_numerology_layer(
            layer_data,
        )

        assert formatted["stone_id"] == "cats_eye"
        assert formatted["stone_name"] == "キャッツアイ"
        assert formatted["layer"] == "overall"
        assert formatted["description"] == "直感を高める"
        assert formatted["secondary"]["stone_id"] == "amethyst"
        assert formatted["secondary"]["stone_name"] == "アメシスト"

    # ── 양 유즈케이스 모두 호출 확인 ─────────────────

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_personal_year_number"
    )
    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_both_engines_called(self, mock_calc: MagicMock, mock_pyn: MagicMock) -> None:
        """7-Layer 모드에서 구성기학 + 수비술 양쪽 모두 호출."""
        mock_calc.return_value = MagicMock(number=3)
        mock_pyn.return_value = MagicMock(number=2)
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ko",
            birth_date="1995-12-25",
            target_year=2026,
        )

        # 구성기학 호출
        self.mock_stone_uc.execute.assert_called_once_with(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ko",
        )

        # 수비술 호출
        mock_calc.assert_called_once_with("1995-12-25")
        mock_pyn.assert_called_once_with("1995-12-25", 2026)
        self.mock_engine.recommend_as_dict.assert_called_once_with(
            life_path_number=3,
            locale="ko",
            personal_year_number=2,
        )

    # ── base_stone 은 6-Layer 에서 제외 ───────────────

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_base_stone_excluded_in_6_layer(self, mock_calc: MagicMock) -> None:
        """6-Layer 모드에서 base_stone 은 포함되지 않음 (수비술 전체운으로 대체)."""
        mock_calc.return_value = MagicMock(number=1)
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="2000-01-01",
        )

        assert "base_stone" not in result
        assert "overall_stone" in result

    # ── merge_six_layer_partial: 길방위 없을 때 수비술만 반환 ──

    def test_merge_six_layer_partial_returns_numerology_only(self) -> None:
        """길방위 없을 때 수비술 4-Layer만 반환, 구성기학 2-Layer는 None."""
        numerology = _make_numerology_result()
        result = self.use_case.merge_six_layer_partial(numerology)

        # 수비술 4-Layer 존재
        for key in ("overall_stone", "health_stone", "wealth_stone", "love_stone"):
            assert key in result, f"Missing key: {key}"
            assert result[key] is not None, f"{key} should not be None"
            assert "stone_id" in result[key]
            assert "stone_name" in result[key]

        # 구성기학 2-Layer는 None
        assert result["monthly_stone"] is None
        assert result["protection_stone"] is None

        # 메타 정보
        assert result["life_path_number"] == 7
        assert result["planet"] == "ketu"

    # ── 7-Layer: yearly_stone 포함 검증 ─────────────

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_personal_year_number"
    )
    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_7_layer_includes_yearly_stone(self, mock_calc: MagicMock, mock_pyn: MagicMock) -> None:
        """7-Layer 모드에서 yearly_stone/personal_year_number 가 응답에 포함."""
        mock_calc.return_value = MagicMock(number=3)
        mock_pyn.return_value = MagicMock(number=5)

        numerology_with_yearly = _make_numerology_result()
        numerology_with_yearly["yearly"] = {
            "layer": "yearly",
            "primary": {
                "stone_id": "citrine",
                "stone_name": "シトリン",
                "description": "年エネルギー石",
            },
            "secondary": {
                "stone_id": "garnet",
                "stone_name": "ガーネット",
                "description": "補助年運石",
            },
        }
        numerology_with_yearly["personal_year_number"] = 5
        self.mock_engine.recommend_as_dict.return_value = numerology_with_yearly

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="1990-03-15",
            target_year=2026,
        )

        # yearly_stone 포함 검증
        assert "yearly_stone" in result
        assert result["yearly_stone"]["stone_id"] == "citrine"
        assert result["personal_year_number"] == 5

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_6_layer_no_target_year_excludes_yearly(self, mock_calc: MagicMock) -> None:
        """target_year 미제공 시 yearly_stone 없는 6-Layer 응답."""
        mock_calc.return_value = MagicMock(number=3)
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="1990-03-15",
        )

        # yearly 관련 키 없어야 함
        assert "yearly_stone" not in result or result.get("yearly_stone") is None
        assert "personal_year_number" not in result or result.get("personal_year_number") is None

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".get_numerology_traits"
    )
    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_traits_included_in_response(
        self, mock_calc: MagicMock, mock_traits: MagicMock,
    ) -> None:
        """title + traits 가 execute() 응답에 포함되어야 한다."""
        mock_calc.return_value = MagicMock(number=1)
        mock_traits.return_value = {"title": "リーダー", "traits": "独立心が強い"}
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="1990-01-01",
        )

        assert result["title"] == "リーダー"
        assert result["traits"] == "独立心が強い"

    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".get_numerology_traits"
    )
    @patch(
        "apps.fortunetelling.powerstone.use_cases.six_layer_powerstone_use_case"
        ".NumerologyService.calculate_life_path_number"
    )
    def test_traits_absent_when_not_found(
        self, mock_calc: MagicMock, mock_traits: MagicMock,
    ) -> None:
        """traits 데이터가 없으면 title/traits 키가 없어야 한다."""
        mock_calc.return_value = MagicMock(number=1)
        mock_traits.return_value = None
        self.mock_engine.recommend_as_dict.return_value = _make_numerology_result()

        result = self.use_case.execute(
            main_star=5,
            directions=DUMMY_DIRECTIONS,
            locale="ja",
            birth_date="1990-01-01",
        )

        assert "title" not in result
        assert "traits" not in result
