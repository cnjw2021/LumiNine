"""powerstone 테스트 공용 상수 · 팩토리 · @patch 경로.

conftest.py 와 분리하여, pytest의 conftest 특별 취급으로 인한
이중 import 문제를 방지한다.

Issue #128: Copilot 리뷰 반영 — conftest에서 비-fixture 코드 분리
"""
from __future__ import annotations

from typing import Any, Dict


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
