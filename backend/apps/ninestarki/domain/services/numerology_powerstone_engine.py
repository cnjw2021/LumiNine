"""NumerologyPowerStoneEngine — 수비술 기반 파워스톤 매칭 엔진.

7-Layer 파워스톤 시스템 중 수비술 기반 4~5개 레이어를 담당한다:
  L1 — 전체운: 지배 행성 대표석 (Life Path Number 기반, 고정)
  L2 — 건강운: 숫자 × 태양(Sun) 보완석 (Life Path Number 기반, 고정)
  L3 — 재물운: 숫자 × 목성(Jupiter) 보완석 (Life Path Number 기반, 고정)
  L4 — 연애운: 숫자 × 금성(Venus) 보완석 (Life Path Number 기반, 고정)
  L5 — 연운석: Personal Year Number 기반 연간 보충석 (매년 변경)

나머지 2개 레이어(L6 월운석, L7 호신석)는 기존 PowerStoneMatchingEngine
(구성기학 기반)이 담당한다. 두 엔진은 독립적으로 동작하며,
API 레이어에서 결합된다.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

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

_LIFE_PATH_LAYERS = ("overall", "health", "wealth", "love")
_YEARLY_LAYER = "yearly"


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
        personal_year_number: Optional[int] = None,
    ) -> NumerologyPowerStoneResult:
        """수비술 파워스톤 추천 실행 (locale 비의존 VO 반환).

        Args:
            life_path_number: 사용자 Life Path Number (1~9)
            personal_year_number: Personal Year Number (1~9, optional)

        Returns:
            NumerologyPowerStoneResult (overall, health, wealth, love, [yearly])

        Raises:
            ValueError: 잘못된 Life Path Number
        """
        logger.info(
            "NumerologyPowerStoneEngine.recommend: lpn=%d, pyn=%s",
            life_path_number,
            personal_year_number,
        )

        mapping = self._repo.get_mapping(life_path_number)
        planet = mapping["planet"]

        # Life Path 기반 4개 레이어 (고정)
        recommendations: Dict[str, NumerologyStoneRecommendation] = {}
        for layer in _LIFE_PATH_LAYERS:
            layer_data = mapping[layer]
            primary = self._repo.get_stone(layer_data["primary"])
            secondary = self._repo.get_stone(layer_data["secondary"])
            recommendations[layer] = NumerologyStoneRecommendation(
                layer=layer,
                primary=primary,
                secondary=secondary,
                planet=planet,
            )

        # Personal Year 기반 연운석 (매년 변경)
        yearly_rec: Optional[NumerologyStoneRecommendation] = None
        if personal_year_number is not None:
            if not isinstance(personal_year_number, int) or not 1 <= personal_year_number <= 9:
                raise ValueError(
                    f"Personal Year Number 는 1~9 범위여야 합니다: {personal_year_number}"
                )
            yearly_mapping = self._repo.get_mapping(personal_year_number)
            yearly_planet = yearly_mapping["planet"]
            if _YEARLY_LAYER not in yearly_mapping:
                raise ValueError(
                    f"카탈로그에 'yearly' 레이어가 없습니다 (number={personal_year_number})"
                )
            yearly_layer_data = yearly_mapping[_YEARLY_LAYER]
            missing_keys = [k for k in ("primary", "secondary") if k not in yearly_layer_data]
            if missing_keys:
                missing_str = ", ".join(missing_keys)
                raise ValueError(
                    f"카탈로그 'yearly' 레이어에 필요한 키가 없습니다"
                    f" (number={personal_year_number}, missing={missing_str})"
                )
            primary = self._repo.get_stone(yearly_layer_data["primary"])
            secondary = self._repo.get_stone(yearly_layer_data["secondary"])
            yearly_rec = NumerologyStoneRecommendation(
                layer=_YEARLY_LAYER,
                primary=primary,
                secondary=secondary,
                planet=yearly_planet,
            )

        return NumerologyPowerStoneResult(
            life_path_number=life_path_number,
            planet=planet,
            overall=recommendations["overall"],
            health=recommendations["health"],
            wealth=recommendations["wealth"],
            love=recommendations["love"],
            yearly=yearly_rec,
            personal_year_number=personal_year_number,
        )

    def recommend_as_dict(
        self,
        life_path_number: int,
        locale: str = "ja",
        personal_year_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """4~5-Layer 추천을 API 응답용 dict 로 직렬화.

        Args:
            life_path_number: 사용자 Life Path Number (1~9)
            locale: 응답 언어 코드
            personal_year_number: Personal Year Number (1~9, optional)

        Returns:
            API 응답용 dict
        """
        result = self.recommend(life_path_number, personal_year_number)

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

        resp: Dict[str, Any] = {
            "life_path_number": result.life_path_number,
            "planet": result.planet,
            "overall": _render(result.overall),
            "health": _render(result.health),
            "wealth": _render(result.wealth),
            "love": _render(result.love),
        }
        if result.yearly is not None:
            resp["yearly"] = _render(result.yearly)
            resp["personal_year_number"] = result.personal_year_number
        return resp
