from __future__ import annotations
from abc import ABC, abstractmethod


class IMonthFortuneService(ABC):
    @abstractmethod
    def get_month_fortune(self, main_star: int, month_star: int, target_year: int):
        raise NotImplementedError
from typing import Protocol, Dict, Any


class IMonthFortuneService(Protocol):
    """月運サービスのドメインポート"""

    def get_month_fortune_for_report(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        ...

    def get_month_fortune(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        ...


