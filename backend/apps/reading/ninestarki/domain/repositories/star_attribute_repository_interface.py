from abc import ABC, abstractmethod
from typing import List


class IStarAttributeRepository(ABC):
    """
    StarAttribute エンティティに対するデータストアの仕様(インターフェース)を定義します.
    """
    @abstractmethod
    def find_by_star_and_type(self, star_number: int, attribute_type: str) -> List[str]:
        """指定された星番号と属性タイプに一致する属性値のリストを返します."""
        pass
