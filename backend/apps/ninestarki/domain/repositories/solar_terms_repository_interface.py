from __future__ import annotations
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from datetime import date
from apps.ninestarki.domain.entities.solar_term import SolarTerm


class ISolarTermsRepository(ABC):
    @abstractmethod
    def get_yearly_terms(self, year: int) -> List[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def get_term_by_month(self, year: int, month: int) -> Optional[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def get_term_by_date(self, target_date: date) -> Optional[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def get_spring_start(self, year: int) -> Optional[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, term_id: int) -> Optional[SolarTerm]:
        raise NotImplementedError

    @abstractmethod
    def update_term(self, term_id: int, *, year: Optional[int] = None, month: Optional[int] = None, term_name: Optional[str] = None, dt_iso: Optional[str] = None) -> Optional[SolarTerm]:
        raise NotImplementedError
