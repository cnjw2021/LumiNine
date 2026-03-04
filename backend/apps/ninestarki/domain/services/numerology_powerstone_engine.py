"""NumerologyPowerStoneEngine — 수비술 기반 파워스톤 매칭 엔진.

6-Layer 파워스톤 시스템 중 수비술 기반 4개 레이어를 담당한다:
  L1 — 전체운: 지배 행성 대표석
  L2 — 건강운: 숫자 × 태양(Sun) 보완석
  L3 — 재물운: 숫자 × 목성(Jupiter) 보완석
  L4 — 연애운: 숫자 × 금성(Venus) 보완석

나머지 2개 레이어(L5 월운석, L6 호신석)는 기존 PowerStoneMatchingEngine
(구성기학 기반)이 담당한다. 두 엔진은 독립적으로 동작하며,
API 레이어에서 결합된다.
"""
from __future__ import annotations

from typing import Any, Dict

from injector import inject

from apps.ninestarki.domain.repositories.numerology_powerstone_repository_interface import (
    INumerologyPowerStoneRepository,
)
from apps.ninestarki.domain.value_objects.numerology_powerstone import (
    NumerologyPowerStoneResult,
    NumerologyStoneRecommendation,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)

_LAYER_NAMES = ("overall", "health", "wealth", "love")


class NumerologyPowerStoneEngine:
    """수비술 기반 4-Layer 파워스톤 매칭 엔진.

    DI 를 통해 INumerologyPowerStoneRepository 를 주입받는다.
    """

    @inject
    def __init__(self, repo: INumerologyPowerStoneRepository) -> None:
        self._repo = repo

    def recommend(
        self,
        life_path_number: int,
    ) -> NumerologyPowerStoneResult:
        """수비술 파워스톤 추천 실행 (locale 비의존 VO 반환).

        Args:
            life_path_number: 사용자 Life Path Number (1~9)

        Returns:
            NumerologyPowerStoneResult (overall, health, wealth, love)

        Raises:
            ValueError: 잘못된 Life Path Number
        """
        logger.info(
            "NumerologyPowerStoneEngine.recommend: lpn=%d",
            life_path_number,
        )

        mapping = self._repo.get_mapping(life_path_number)
        planet = mapping["planet"]

        recommendations: Dict[str, NumerologyStoneRecommendation] = {}
        for layer in _LAYER_NAMES:
            layer_data = mapping[layer]
            primary = self._repo.get_stone(layer_data["primary"])
            secondary = self._repo.get_stone(layer_data["secondary"])
            recommendations[layer] = NumerologyStoneRecommendation(
                layer=layer,
                primary=primary,
                secondary=secondary,
                planet=planet,
            )

        return NumerologyPowerStoneResult(
            life_path_number=life_path_number,
            planet=planet,
            overall=recommendations["overall"],
            health=recommendations["health"],
            wealth=recommendations["wealth"],
            love=recommendations["love"],
        )

    def recommend_as_dict(
        self,
        life_path_number: int,
        locale: str = "ja",
    ) -> Dict[str, Any]:
        """4-Layer 추천을 API 응답용 dict 로 직렬화.

        Args:
            life_path_number: 사용자 Life Path Number (1~9)
            locale: 응답 언어 코드

        Returns:
            API 응답용 dict
        """
        result = self.recommend(life_path_number)

        def _render(rec: NumerologyStoneRecommendation) -> Dict[str, Any]:
            return {
                "layer": rec.layer,
                "primary": {
                    "stone_id": rec.primary.id,
                    "stone_name": rec.primary.get_name(locale),
                    "description": rec.primary.get_description(locale),
                },
                "secondary": {
                    "stone_id": rec.secondary.id,
                    "stone_name": rec.secondary.get_name(locale),
                    "description": rec.secondary.get_description(locale),
                },
            }

        return {
            "life_path_number": result.life_path_number,
            "planet": result.planet,
            "overall": _render(result.overall),
            "health": _render(result.health),
            "wealth": _render(result.wealth),
            "love": _render(result.love),
        }
