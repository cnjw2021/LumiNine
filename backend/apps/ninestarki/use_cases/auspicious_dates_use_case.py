from __future__ import annotations
from typing import Dict, Any
from injector import inject

from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService


class AuspiciousDatesUseCase:
    """(薄い)ユースケース: ドメインサービスを呼び出して吉日情報(dict)を返す"""

    @inject
    def __init__(self, service: IAuspiciousDatesService) -> None:
        self._service = service

    def execute(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        return self._service.execute(main_star, month_star, target_year)


