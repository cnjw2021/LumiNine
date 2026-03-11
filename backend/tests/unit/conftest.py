"""powerstone 테스트 공유 fixture / 상수.

test_six_layer_powerstone.py 등 여러 파워스톤 테스트 파일에서
공통으로 사용하는 모의(mock) 데이터와 fixture 함수를 집약한다.

Issue #128: 테스트 파일 리팩터링 — DRY 및 SSoT 준수
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from apps.reading.powerstone.use_cases.six_layer_powerstone_use_case import (
    SixLayerPowerStoneUseCase,
)


# ── @patch 대상 모듈 경로 (DRY: 7회 이상 반복 방지) ──────

_SIX_LAYER_MODULE = (
    "apps.reading.powerstone.use_cases.six_layer_powerstone_use_case"
)

PATCH_LIFE_PATH = f"{_SIX_LAYER_MODULE}.NumerologyService.calculate_life_path_number"
PATCH_PERSONAL_YEAR = f"{_SIX_LAYER_MODULE}.NumerologyService.calculate_personal_year_number"
PATCH_TRAITS = f"{_SIX_LAYER_MODULE}.get_numerology_traits"


# ── 공통 테스트 데이터 ────────────────────────────────────

DUMMY_DIRECTIONS: Dict[str, Any] = {"north": {"is_auspicious": True}}


def make_gogyo_result() -> Dict[str, Any]:
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


def make_numerology_result() -> Dict[str, Any]:
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


# ── pytest fixture ────────────────────────────────────

@pytest.fixture
def gogyo_result() -> Dict[str, Any]:
    return make_gogyo_result()


@pytest.fixture
def numerology_result() -> Dict[str, Any]:
    return make_numerology_result()


@pytest.fixture
def six_layer_uc() -> SixLayerPowerStoneUseCase:
    """SixLayerPowerStoneUseCase + mock 의존성을 자동 주입한 fixture."""
    mock_stone_uc = MagicMock()
    mock_stone_uc.execute.return_value = make_gogyo_result()

    mock_engine = MagicMock()
    mock_engine.recommend_as_dict.return_value = make_numerology_result()

    return SixLayerPowerStoneUseCase(
        stone_use_case=mock_stone_uc,
        numerology_engine=mock_engine,
    )
