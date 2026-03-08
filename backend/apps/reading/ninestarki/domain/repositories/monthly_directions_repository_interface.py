"""Domain repository interface for MonthlyDirections access."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Any


class IMonthlyDirectionsRepository(ABC):
    @abstractmethod
    def get_by_group_and_month(self, group_id: int, month: int) -> Optional[Any]:
        raise NotImplementedError

    @abstractmethod
    def list_by_group(self, group_id: int) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def list_by_month(self, month: int) -> List[Any]:
        raise NotImplementedError


