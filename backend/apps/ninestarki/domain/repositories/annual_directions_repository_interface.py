"""年次の方位関連データ取得用ドメイン・リポジトリ・インターフェース

UseCase はこのインターフェースに依存し、具象実装は infrastructure に配置します。
ORM への直接依存を避けるため、プリミティブ(dict/list)で返却します。
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class IAnnualDirectionsRepository(ABC):
    """年次の月盤/節気/盤パターン情報を提供するポート"""

    @abstractmethod
    def get_monthly_directions(self, target_year: int) -> List[Dict[str, Any]]:
        """対象年の各月の中心星情報リストを返す。
        返却例: [{"month": 1, "center_star": 5}, ...]
        """
        raise NotImplementedError

    @abstractmethod
    def get_star_grid_fortune_status(self, center_star: int, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """九星盤パターンに基づく吉凶判定を返す。"""
        raise NotImplementedError

    @abstractmethod
    def get_yearly_solar_terms_map(self, year: int) -> Dict[int, Dict[str, Any]]:
        """その年の節気情報(月→辞書)を返す。
        値例: { 2: {"zodiac": "甲子", "solar_terms_date": date(...) }, ... }
        """
        raise NotImplementedError

    @abstractmethod
    def get_solar_term_by_month(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """指定年/月の節気情報を返す。存在しなければ None。"""
        raise NotImplementedError


