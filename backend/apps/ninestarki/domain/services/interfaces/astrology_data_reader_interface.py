from __future__ import annotations
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from datetime import datetime


class IAstrologyDataReader(ABC):
    """年/日/候補日の占術データを取得するためのドメインポート"""

    @abstractmethod
    def get_yearly_chart_info(self, target_year: int) -> Optional[Dict]:
        raise NotImplementedError

    @abstractmethod
    def get_daily_info(self, target_date: datetime) -> Optional[Dict]:
        raise NotImplementedError

    @abstractmethod
    def get_dates_with_same_center_star(self, year: int) -> List[datetime]:
        raise NotImplementedError


