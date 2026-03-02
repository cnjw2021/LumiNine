from __future__ import annotations
from typing import Dict, List
from abc import ABC, abstractmethod


class ICompatibilityService(ABC):
    """相性判定サービスのドメインポート"""

    @abstractmethod
    def get_best_common_and_main_compatible_stars(self, main_star: int, month_star: int) -> Dict[str, List[int]]:
        raise NotImplementedError


