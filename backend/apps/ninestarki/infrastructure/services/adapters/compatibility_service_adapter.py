from __future__ import annotations
from typing import Dict, List

from apps.ninestarki.domain.services.interfaces.compatibility_service_interface import ICompatibilityService
from apps.ninestarki.services.star_compatibility_service import StarCompatibilityService


class CompatibilityServiceAdapter(ICompatibilityService):
    """ドメインポートICompatibilityServiceのアダプタ。既存サービスを委譲。"""

    def __init__(self) -> None:
        self._impl = StarCompatibilityService()

    def get_best_common_and_main_compatible_stars(self, main_star: int, month_star: int) -> Dict[str, List[int]]:
        return self._impl.get_best_common_and_main_compatible_stars(main_star, month_star)


