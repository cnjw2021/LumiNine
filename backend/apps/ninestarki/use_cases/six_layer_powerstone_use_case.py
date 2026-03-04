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

    Note:
        월별 반복 호출 시 ``compute_numerology_stones()`` 로 수비술 부분을
        1회만 계산하고, 구성기학(방위 기반) 부분만 월별로 재계산할 수 있다.
        ``base_stone`` 은 6-Layer 모드에서 사용하지 않지만, 현재
        ``PowerStoneRecommendationUseCase`` 가 3개를 일괄 계산하므로
        함께 반환된다. 향후 구성기학 엔진에 경량 경로(월운석+호신석만)를
        추가하면 불필요한 ``base_stone`` 계산을 제거할 수 있다.
    """

    @inject
    def __init__(
        self,
        stone_use_case: PowerStoneRecommendationUseCase,
        numerology_engine: NumerologyPowerStoneEngine,
    ) -> None:
        self._stone_use_case = stone_use_case
        self._numerology_engine = numerology_engine

    # ──────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────

    def compute_numerology_stones(
        self,
        birth_date: str,
        locale: str = "ja",
    ) -> Dict[str, Any]:
        """수비술 기반 4-Layer 파워스톤을 계산하여 반환.

        월에 독립적인 결과이므로 루프 밖에서 1회만 호출하고
        결과를 재사용할 수 있다.

        Args:
            birth_date: 생년월일 (``"YYYY-MM-DD"`` 또는 ``"YYYY-MM-DD HH:MM"``)
            locale: 응답 언어 코드

        Returns:
            수비술 4-Layer dict + life_path_number, planet 메타 정보.

        Raises:
            ValueError: birth_date 형식이 잘못된 경우 (그대로 전파)
        """
        numerology_number = NumerologyService.calculate_life_path_number(birth_date)
        life_path = numerology_number.number

        result = self._numerology_engine.recommend_as_dict(
            life_path_number=life_path,
            locale=locale,
        )
        result["life_path_number"] = life_path
        return result

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
            birth_date: 생년월일 (``"YYYY-MM-DD"`` 또는 ``"YYYY-MM-DD HH:MM"``). 없으면 3-Layer 반환.

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

        # ── 2. birth_date 가 실제로 제공되지 않은 경우(None) 기존 3-Layer 반환 ─
        if birth_date is None:
            logger.info("SixLayerPowerStoneUseCase: birth_date 미제공 → 3-Layer")
            return gogyo_result

        # ── 3. 수비술 계산 + 6-Layer 통합 ─────────────────
        logger.info("SixLayerPowerStoneUseCase: birth_date 제공 → 6-Layer")
        birth_date_normalized = birth_date.strip()
        numerology_result = self.compute_numerology_stones(
            birth_date_normalized,
            locale,
        )

        return self.merge_six_layer(gogyo_result, numerology_result)

    def merge_six_layer(
        self,
        gogyo_result: Dict[str, Any],
        numerology_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """구성기학 결과와 수비술 결과를 6-Layer 응답으로 합산.

        Args:
            gogyo_result: 구성기학 3-Layer 결과 (base/monthly/protection)
            numerology_result: ``compute_numerology_stones()`` 의 반환값

        Returns:
            6-Layer 통합 응답 dict.
        """
        base = self._build_numerology_base(numerology_result)
        base["monthly_stone"] = gogyo_result["monthly_stone"]
        base["protection_stone"] = gogyo_result["protection_stone"]
        return base

    def merge_six_layer_partial(
        self,
        numerology_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """수비술 4-Layer만으로 6-Layer 응답을 구성 (구성기학 2-Layer는 null).

        ``directions`` 자체가 비어 있어 구성기학 엔진을 실행할 수 없을 때
        사용한다. 수비술 기반 4개 스톤은 방위 정보와 무관하므로 항상 반환 가능하다.

        Args:
            numerology_result: ``compute_numerology_stones()`` 의 반환값

        Returns:
            6-Layer 응답 dict (monthly_stone, protection_stone = None)
        """
        base = self._build_numerology_base(numerology_result)
        base["monthly_stone"] = None
        base["protection_stone"] = None
        return base

    def _build_numerology_base(
        self,
        numerology_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """수비술 4-Layer + 메타정보를 공통으로 조립하는 헬퍼.

        ``merge_six_layer()`` 과 ``merge_six_layer_partial()`` 에서
        공유하여 사용한다.
        """
        return {
            "overall_stone": self.format_numerology_layer(
                numerology_result["overall"],
            ),
            "health_stone": self.format_numerology_layer(
                numerology_result["health"],
            ),
            "wealth_stone": self.format_numerology_layer(
                numerology_result["wealth"],
            ),
            "love_stone": self.format_numerology_layer(
                numerology_result["love"],
            ),
            "life_path_number": numerology_result["life_path_number"],
            "planet": numerology_result["planet"],
        }

    # ──────────────────────────────────────────────────
    # Serialization helpers (public — 라우트에서도 사용)
    # ──────────────────────────────────────────────────

    @staticmethod
    def format_numerology_layer(
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
