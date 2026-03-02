"""Domain repository interface for reading queries (月/日/本命のリーディング).

UseCase はこのインターフェースに依存し、具象実装は infrastructure に配置します。
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class IReadingQueryRepository(ABC):
    """リーディング取得用のドメイン・リポジトリ・インターフェース"""

    @abstractmethod
    def get_monthly_star_reading(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        """月命星読みを取得"""
        raise NotImplementedError

    @abstractmethod
    def get_daily_star_reading(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        """日命星読みを取得"""
        raise NotImplementedError

    @abstractmethod
    def get_main_star_message(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        """本命星の獲得運メッセージを取得"""
        raise NotImplementedError
