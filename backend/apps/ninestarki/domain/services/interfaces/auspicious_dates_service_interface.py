from __future__ import annotations
from typing import Dict, Any
from abc import ABC, abstractmethod


class IAuspiciousDatesService(ABC):
    """引越し吉日/お水取り吉日の算出サービスのポートインターフェース"""

    @abstractmethod
    def execute(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        """指定条件で吉日情報を返す（画面/APIと同一フォーマットのdict）"""
        raise NotImplementedError


