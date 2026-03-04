"""PowerStoneRepository — JSON 기반 정적 스톤 데이터 구현체.

SSoT: data/powerstone_catalog.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from apps.ninestarki.domain.exceptions import PowerStoneMatchingError
from apps.ninestarki.domain.repositories.powerstone_repository_interface import (
    IPowerStoneRepository,
)
from apps.ninestarki.domain.value_objects.gogyo import Gogyo
from apps.ninestarki.domain.value_objects.powerstone import PowerStone


# ── 데이터 파일 경로 ─────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_CATALOG_PATH = _DATA_DIR / "powerstone_catalog.json"


class PowerStoneRepository(IPowerStoneRepository):
    """JSON 기반 파워스톤 리포지토리.

    인스턴스 생성 시 powerstone_catalog.json 을 로드하여 메모리에 캐시한다.
    """

    def __init__(self, catalog_path: Path | None = None) -> None:
        path = catalog_path or _CATALOG_PATH
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        # ── 스톤 파싱 ────────────────────────────────────
        self._stones: Dict[str, PowerStone] = {}
        self._primary_by_gogyo: Dict[Gogyo, PowerStone] = {}
        self._secondaries_by_gogyo: Dict[Gogyo, List[PowerStone]] = {g: [] for g in Gogyo}

        for entry in raw["stones"]:
            gogyo = Gogyo(entry["gogyo"])
            stone = PowerStone(
                id=entry["id"],
                names=entry["names"],
                gogyo=gogyo,
                is_primary=entry["is_primary"],
            )
            self._stones[stone.id] = stone

            if stone.is_primary:
                self._primary_by_gogyo[gogyo] = stone
            else:
                self._secondaries_by_gogyo[gogyo].append(stone)

        # ── 본명성-기본석 매핑 ───────────────────────────
        self._star_base_stones: Dict[int, List[str]] = {
            int(k): v for k, v in raw["star_base_stones"].items()
        }

    # ── 공개 메서드 ──────────────────────────────────────

    def get_primary_by_gogyo(self, gogyo: Gogyo) -> PowerStone:
        """지정 오행의 주석 반환."""
        stone = self._primary_by_gogyo.get(gogyo)
        if stone is None:
            raise PowerStoneMatchingError(
                f"해당 오행의 주석을 찾을 수 없습니다: {gogyo}",
                code="PRIMARY_STONE_NOT_FOUND",
                status=500,
            )
        return stone

    def get_secondaries_by_gogyo(self, gogyo: Gogyo) -> List[PowerStone]:
        """지정 오행의 부석 목록 반환."""
        return list(self._secondaries_by_gogyo.get(gogyo, []))

    def get_base_stones_for_star(self, star_number: int) -> List[PowerStone]:
        """본명성 번호(1~9) → 기본석 목록 반환."""
        stone_ids = self._star_base_stones.get(star_number)
        if stone_ids is None:
            raise PowerStoneMatchingError(
                f"유효하지 않은 본명성 번호입니다: {star_number} (1~9 범위)",
                code="INVALID_STAR_NUMBER",
                status=422,
            )
        stones: List[PowerStone] = []
        for stone_id in stone_ids:
            stone = self._stones.get(stone_id)
            if stone is None:
                raise PowerStoneMatchingError(
                    f"본명성 {star_number} 의 기본석 '{stone_id}' 을 카탈로그에서 찾을 수 없습니다.",
                    code="BASE_STONE_NOT_FOUND",
                    status=500,
                )
            stones.append(stone)
        return stones
