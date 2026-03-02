from __future__ import annotations

from typing import Optional, List, Any

from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from core.models.monthly_directions import MonthlyDirections
from core.database import read_only_session


class MonthlyDirectionsRepository(IMonthlyDirectionsRepository):
    def get_by_group_and_month(self, group_id: int, month: int) -> Optional[Any]:
        with read_only_session() as s:
            return s.query(MonthlyDirections).filter_by(group_id=group_id, month=month).first()

    def list_by_group(self, group_id: int) -> List[Any]:
        with read_only_session() as s:
            return s.query(MonthlyDirections).filter_by(group_id=group_id).order_by(MonthlyDirections.month).all()

    def list_by_month(self, month: int) -> List[Any]:
        with read_only_session() as s:
            return s.query(MonthlyDirections).filter_by(month=month).order_by(MonthlyDirections.group_id).all()


