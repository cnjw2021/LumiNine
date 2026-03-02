from __future__ import annotations
from typing import Optional, Dict, List
from datetime import datetime

from apps.ninestarki.domain.services.interfaces.astrology_data_reader_interface import IAstrologyDataReader
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.infrastructure.persistence.astrology_data_reader import AstrologyDataReader
from injector import inject


class AstrologyDataReaderAdapter(IAstrologyDataReader):
    """ドメインポートIAstrologyDataReaderのアダプタ。実体へ委譲（依存性はDIで注入）。"""

    @inject
    def __init__(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository) -> None:
        self._impl = AstrologyDataReader(solar_terms_repo, solar_starts_repo)

    def get_yearly_chart_info(self, target_year: int) -> Optional[Dict]:
        return self._impl.get_yearly_chart_info(target_year)

    def get_daily_info(self, target_date: datetime) -> Optional[Dict]:
        return self._impl.get_daily_info(target_date)

    def get_dates_with_same_center_star(self, year: int) -> List[datetime]:
        return self._impl.get_dates_with_same_center_star(year)


