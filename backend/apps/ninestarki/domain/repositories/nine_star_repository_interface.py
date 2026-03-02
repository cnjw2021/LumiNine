from abc import ABC, abstractmethod
from typing import Optional, List
from apps.ninestarki.domain.entities.nine_star import NineStar

class INineStarRepository(ABC):
    """
    NineStar エンティティに対するデータストアの仕様(インターフェース)を定義します.
    """
    @abstractmethod
    def find_by_star_number(self, star_number: int) -> Optional[NineStar]:
        """星番号でNineStar エンティティを検索します."""
        pass

    @abstractmethod
    def find_all(self) -> List[NineStar]:
        """すべてのNineStar エンティティを検索します."""
        pass