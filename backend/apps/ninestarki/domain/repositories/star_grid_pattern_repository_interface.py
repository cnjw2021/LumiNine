"""Domain repository interface for StarGridPattern access."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any


class IStarGridPatternRepository(ABC):
    @abstractmethod
    def get_by_center_star(self, center_star: int) -> Optional[Any]:
        """中央の星番号から九星盤パターンを取得する。"""
        raise NotImplementedError


