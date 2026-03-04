"""SixLayerPowerStoneUseCase — 6-Layer 파워스톤 통합 유즈케이스.

구성기학 기반 2개 레이어 (월운석, 호신석) + 수비술 기반 4개 레이어
(전체운, 건강운, 재물운, 연애운) 를 하나의 API 응답으로 통합한다.

birth_date 가 제공되지 않은 경우 기존 3-Layer 응답을 유지하여
하위 호환성을 보장한다.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from injector import inject

from apps.ninestarki.domain.services.numerology_powerstone_engine import (
    NumerologyPowerStoneEngine,
)
from apps.ninestarki.domain.services.numerology_service import NumerologyService
from apps.ninestarki.use_cases.powerstone_recommendation_use_case import (
    PowerStoneRecommendationUseCase,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)


class SixLayerPowerStoneUseCase:
    """6-Layer 파워스톤 통합 유즈케이스.

    - birth_date 가 없으면 기존 3-Layer (base/monthly/protection) 반환
    - birth_date 가 있으면 6-Layer (수비술 4 + 구성기학 2) 반환
    """

    @inject
    def __init__(
        self,
        stone_use_case: PowerStoneRecommendationUseCase,
        numerology_engine: NumerologyPowerStoneEngine,
    ) -> None:
        self._stone_use_case = stone_use_case
        self._numerology_engine = numerology_engine

    def execute(
        self,
        main_star: int,
        directions: Dict[str, Any],
        locale: str = "ja",
        birth_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """6-Layer 파워스톤 추천 실행.

        Args:
            main_star: 사용자 본명성 (1~9)
            directions: 방위별 길흉 판정 결과 dict
            locale: 응답 언어 코드 (기본값: ``"ja"``)
            birth_date: 생년월일 (``"YYYY-MM-DD"``). 없으면 3-Layer 반환.

        Returns:
            API 응답용 dict.
            - birth_date 미제공: 3-Layer (base_stone, monthly_stone, protection_stone)
            - birth_date 제공: 6-Layer (overall + health + wealth + love + monthly + protection)
        """
        # ── 1. 구성기학 기반 2-Layer (월운석 + 호신석) ─────
        gogyo_result = self._stone_use_case.execute(
            main_star=main_star,
            directions=directions,
            locale=locale,
        )

        # ── 2. birth_date 없으면 기존 3-Layer 반환 ─────────
        if not birth_date:
            logger.info("SixLayerPowerStoneUseCase: birth_date 미제공 → 3-Layer")
            return gogyo_result

        # ── 3. 수비술 Life Path Number 계산 ────────────────
        logger.info("SixLayerPowerStoneUseCase: birth_date 제공 → 6-Layer")
        numerology_number = NumerologyService.calculate_life_path_number(birth_date)
        life_path = numerology_number.number

        # ── 4. 수비술 기반 4-Layer 추천 ────────────────────
        numerology_result = self._numerology_engine.recommend_as_dict(
            life_path_number=life_path,
            locale=locale,
        )

        # ── 5. 6-Layer 통합 응답 구성 ─────────────────────
        return {
            "overall_stone": self._format_numerology_layer(
                numerology_result["overall"],
            ),
            "health_stone": self._format_numerology_layer(
                numerology_result["health"],
            ),
            "wealth_stone": self._format_numerology_layer(
                numerology_result["wealth"],
            ),
            "love_stone": self._format_numerology_layer(
                numerology_result["love"],
            ),
            "monthly_stone": gogyo_result["monthly_stone"],
            "protection_stone": gogyo_result["protection_stone"],
            "life_path_number": life_path,
            "planet": numerology_result["planet"],
        }

    # ──────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────

    @staticmethod
    def _format_numerology_layer(
        layer_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """수비술 레이어 데이터를 API 응답 형식으로 변환."""
        primary = layer_data["primary"]
        return {
            "stone_id": primary["stone_id"],
            "stone_name": primary["stone_name"],
            "layer": layer_data["layer"],
            "description": primary["description"],
            "secondary": {
                "stone_id": layer_data["secondary"]["stone_id"],
                "stone_name": layer_data["secondary"]["stone_name"],
                "description": layer_data["secondary"]["description"],
            },
        }
