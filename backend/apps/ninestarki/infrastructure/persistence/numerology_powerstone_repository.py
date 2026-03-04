"""NumerologyPowerStoneRepository — JSON 기반 수비술 파워스톤 구현체.

SSoT: data/numerology_powerstone_catalog.json
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Dict

from apps.ninestarki.domain.repositories.numerology_powerstone_repository_interface import (
    INumerologyPowerStoneRepository,
)
from apps.ninestarki.domain.value_objects.numerology_powerstone import NumerologyStone


# ── 데이터 파일 경로 ─────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_CATALOG_PATH = _DATA_DIR / "numerology_powerstone_catalog.json"


class NumerologyPowerStoneRepository(INumerologyPowerStoneRepository):
    """JSON 기반 수비술 파워스톤 리포지토리.

    인스턴스 생성 시 numerology_powerstone_catalog.json 을 로드하여 메모리에 캐시한다.
    """

    def __init__(self, catalog_path: Path | None = None) -> None:
        path = catalog_path or _CATALOG_PATH
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        # ── 스톤 파싱 ────────────────────────────────────
        self._stones: Dict[str, NumerologyStone] = {}
        for stone_id, entry in raw["stones"].items():
            self._stones[stone_id] = NumerologyStone(
                id=stone_id,
                names=entry["names"],
                description=entry["description"],
            )

        # ── 숫자별 매핑 ─────────────────────────────────
        self._mappings: Dict[int, Dict] = {}
        for num_str, mapping in raw["number_mappings"].items():
            num = int(num_str)
            self._mappings[num] = mapping

            # planet 키 존재 및 타입 검증
            if "planet" not in mapping:
                raise ValueError(
                    f"숫자 {num} 의 매핑에 필수 키 'planet' 이 누락되었습니다."
                )
            if not isinstance(mapping["planet"], str) or not mapping["planet"]:
                raise ValueError(
                    f"숫자 {num} 의 'planet' 값이 비어있거나 문자열이 아닙니다: {mapping.get('planet')!r}"
                )

            # 매핑에 필수 키 존재 및 참조된 stone_id 검증
            for layer in ("overall", "health", "wealth", "love"):
                if layer not in mapping:
                    raise ValueError(
                        f"숫자 {num} 의 매핑에 필수 레이어 '{layer}' 가 누락되었습니다."
                    )
                for role in ("primary", "secondary"):
                    if role not in mapping[layer]:
                        raise ValueError(
                            f"숫자 {num} 의 {layer} 레이어에 필수 키 '{role}' 가 누락되었습니다."
                        )
                    sid = mapping[layer][role]
                    if sid not in self._stones:
                        raise ValueError(
                            f"숫자 {num} 의 {layer}.{role} 에 참조된 "
                            f"stone_id '{sid}' 가 카탈로그에 없습니다."
                        )

    # ── 공개 메서드 ──────────────────────────────────────

    def get_stone(self, stone_id: str) -> NumerologyStone:
        """스톤 ID로 단일 스톤 정보 반환."""
        stone = self._stones.get(stone_id)
        if stone is None:
            raise ValueError(f"존재하지 않는 stone_id: {stone_id}")
        return stone

    def get_mapping(self, number: int) -> Dict:
        """Life Path Number 에 대한 4-Layer 매핑 반환 (방어적 복사)."""
        mapping = self._mappings.get(number)
        if mapping is None:
            raise ValueError(
                f"유효하지 않은 Life Path Number: {number} (1~9 범위)"
            )
        # 싱글톤 상태 보호를 위해 방어적 복사 반환
        return copy.deepcopy(mapping)
