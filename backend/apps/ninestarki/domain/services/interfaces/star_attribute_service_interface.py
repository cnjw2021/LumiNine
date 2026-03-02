from typing import Protocol, Dict, Any


class IStarAttributeService(Protocol):
    """星属性サービスのドメインポート"""

    def get_star_attributes(self, star_number: int) -> Dict[str, Any]:
        ...


