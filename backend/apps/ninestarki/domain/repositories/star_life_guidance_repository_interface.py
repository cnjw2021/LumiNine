from abc import ABC, abstractmethod
from typing import List, Optional
from apps.ninestarki.domain.entities.star_life_guidance import StarLifeGuidance, CategoryEnum

class IStarLifeGuidanceRepository(ABC):
    """星と人生のガイダンス情報のリポジトリインターフェース"""

    @abstractmethod
    def find_by_stars_and_category(self, main_star: int, month_star: int, category: CategoryEnum) -> Optional[StarLifeGuidance]:
        """本命星、月命星、カテゴリで星と人生のガイダンス情報を取得する"""
        pass

    @abstractmethod
    def find_by_stars(self, main_star: int, month_star: int) -> List[StarLifeGuidance]:
        """本命星、月命星で星と人生のガイダンス情報を取得する"""
        pass
