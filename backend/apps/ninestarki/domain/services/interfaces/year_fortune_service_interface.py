from typing import Protocol, Dict, Any


class IYearFortuneService(Protocol):
    """年運サービスのドメインポート"""

    def get_year_fortune_for_report(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        ...

    def get_year_fortune(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        ...


