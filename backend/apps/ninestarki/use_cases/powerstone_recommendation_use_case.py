"""파워스톤 추천 유즈케이스 (PowerStone Recommendation Use Case).

처리 흐름:
1. MonthlyDirectionsUseCase 결과(directions dict) 수신
2. IPowerStoneMatchingEngine.recommend() → PowerStoneResult (3-Layer)
3. IMessageCatalog.resolve() → locale별 reason 텍스트 생성
4. API 응답용 dict 직렬화 반환
"""
from __future__ import annotations

from typing import Any, Dict

from injector import inject

from apps.ninestarki.domain.services.interfaces.powerstone_matching_engine_interface import (
    IPowerStoneMatchingEngine,
)
from apps.ninestarki.domain.value_objects.powerstone import (
    PowerStoneResult,
    StoneRecommendation,
)
from apps.ninestarki.use_cases.interfaces.message_catalog_interface import (
    IMessageCatalog,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)


class PowerStoneRecommendationUseCase:
    """파워스톤 3-Layer 추천 유즈케이스.

    MonthlyDirectionsUseCase 의 결과(directions dict)를 받아
    PowerStoneMatchingEngine 으로 3개 스톤을 결정하고,
    MessageCatalog 으로 locale별 텍스트를 렌더링한다.
    """

    @inject
    def __init__(
        self,
        matching_engine: IPowerStoneMatchingEngine,
        message_catalog: IMessageCatalog,
    ) -> None:
        self._engine = matching_engine
        self._catalog = message_catalog

    def execute(
        self,
        main_star: int,
        directions: Dict[str, Any],
        locale: str = "ja",
    ) -> Dict[str, Any]:
        """파워스톤 추천 실행.

        Args:
            main_star: 사용자 본명성 (1~9)
            directions: 방위별 길흉 판정 결과 dict
                (MonthlyDirectionsUseCase 결과의 각 월별 ``directions`` 필드)
            locale: 응답 언어 코드 (기본값: ``"ja"``)

        Returns:
            API 응답용 dict. 각 레이어별 stone_id, stone_name,
            layer, gogyo, reason 을 포함한다.

        Raises:
            NoAuspiciousDirectionError: 길방위가 없어 월운석 결정 불가
            PowerStoneMatchingError: 매칭 과정에서 오류 발생
        """
        logger.info(
            "PowerStoneRecommendationUseCase.execute: main_star=%d locale=%s",
            main_star, locale,
        )

        # ── 1. 3-Layer 매칭 엔진 실행 ─────────────────
        result: PowerStoneResult = self._engine.recommend(
            main_star=main_star,
            directions=directions,
        )

        # ── 2. 각 레이어를 locale별 dict 로 직렬화 ────
        return {
            "base_stone": self._render_recommendation(result.base_stone, locale),
            "monthly_stone": self._render_recommendation(result.monthly_stone, locale),
            "protection_stone": self._render_recommendation(result.protection_stone, locale),
        }

    # ──────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────

    def _render_recommendation(
        self,
        rec: StoneRecommendation,
        locale: str,
    ) -> Dict[str, Any]:
        """단일 StoneRecommendation → API 응답 dict 변환.

        reason_params 내 ``*_key`` 접미사 파라미터를 MessageCatalog 으로
        resolve하여 locale별 표시명으로 치환한 뒤, reason 템플릿을 렌더링한다.
        """
        # reason_params 내 *_key 값을 locale별 표시명으로 치환
        resolved_params: Dict[str, str] = {}
        for param_key, param_value in rec.reason_params.items():
            if param_key.endswith("_key"):
                # e.g. "direction_key" → "direction.south" → "南" (ja)
                display_key = param_key[: -len("_key")]  # "direction"
                resolved_params[display_key] = self._catalog.resolve(
                    param_value, locale,
                )
            else:
                resolved_params[param_key] = param_value

        # reason 텍스트 렌더링
        reason = self._catalog.resolve(rec.reason_key, locale, resolved_params)

        # layer 표시명
        layer_display = self._catalog.resolve(f"layer.{rec.layer}", locale)

        # 오행 표시명
        gogyo_display = self._catalog.resolve(f"gogyo.{rec.gogyo.value}", locale)

        return {
            "stone_id": rec.stone.id,
            "stone_name": rec.stone.get_name(locale),
            "layer": layer_display,
            "gogyo": gogyo_display,
            "reason": reason,
        }
