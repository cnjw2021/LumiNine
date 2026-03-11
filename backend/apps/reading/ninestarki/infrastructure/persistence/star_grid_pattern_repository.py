from __future__ import annotations

from typing import Optional

from apps.reading.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.reading.ninestarki.domain.value_objects.star_grid_pattern_vo import StarGridPatternVO
from core.models.star_grid_pattern import StarGridPattern
from core.database import read_only_session


class StarGridPatternRepository(IStarGridPatternRepository):
    def get_by_center_star(self, center_star: int) -> Optional[StarGridPatternVO]:
        with read_only_session() as s:
            row = s.query(StarGridPattern).filter_by(center_star=center_star).first()
            if row is None:
                return None
            return StarGridPatternVO(
                center_star=row.center_star,
                north=row.north,
                northeast=row.northeast,
                east=row.east,
                southeast=row.southeast,
                south=row.south,
                southwest=row.southwest,
                west=row.west,
                northwest=row.northwest,
            )


