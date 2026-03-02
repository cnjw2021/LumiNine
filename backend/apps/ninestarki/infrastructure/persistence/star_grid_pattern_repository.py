from __future__ import annotations

from typing import Optional, Any

from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from core.models.star_grid_pattern import StarGridPattern
from core.database import read_only_session


class StarGridPatternRepository(IStarGridPatternRepository):
    def get_by_center_star(self, center_star: int) -> Optional[Any]:
        with read_only_session() as s:
            return s.query(StarGridPattern).filter_by(center_star=center_star).first()


