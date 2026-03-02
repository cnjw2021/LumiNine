from __future__ import annotations
from typing import Optional, List
from datetime import date, datetime

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.entities.solar_term import SolarTerm
from core.models.solar_terms import SolarTerms


class SolarTermsRepository(ISolarTermsRepository):
    def get_yearly_terms(self, year: int) -> List[SolarTerm]:
        rows = SolarTerms.query.filter(SolarTerms.year == year).order_by(SolarTerms.month).all()
        return [self._to_domain(r) for r in rows]

    def get_term_by_month(self, year: int, month: int) -> Optional[SolarTerm]:
        row = SolarTerms.query.filter(SolarTerms.year == year, SolarTerms.month == month).first()
        return self._to_domain(row) if row else None

    def get_term_by_date(self, target_date: date) -> Optional[SolarTerm]:
        # target_date は date/datetime いずれも許容
        target_date_only = target_date.date() if hasattr(target_date, 'date') else target_date
        year = target_date_only.year
        month = target_date_only.month
        current_term = SolarTerms.query.filter(SolarTerms.year == year, SolarTerms.month == month).first()
        if current_term and target_date_only >= current_term.solar_terms_date:
            return self._to_domain(current_term)
        # 前月へフォールバック
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year = year - 1
        prev_term = SolarTerms.query.filter(SolarTerms.year == prev_year, SolarTerms.month == prev_month).first()
        return self._to_domain(prev_term) if prev_term else (self._to_domain(current_term) if current_term else None)

    def get_spring_start(self, year: int) -> Optional[SolarTerm]:
        row = SolarTerms.query.filter(SolarTerms.year == year, SolarTerms.solar_terms_name == '立春').first()
        return self._to_domain(row) if row else None

    def _to_domain(self, r: SolarTerms) -> SolarTerm:
        return SolarTerm(
            year=r.year,
            month=r.month,
            solar_terms_date=r.solar_terms_date,
            solar_terms_time=getattr(r, 'solar_terms_time', None),
            solar_terms_name=r.solar_terms_name,
            zodiac=r.zodiac,
            star_number=r.star_number,
        )

    # 管理用（Admin用途）
    def list_all(self) -> List[SolarTerm]:
        rows = SolarTerms.query.all()
        return [self._to_domain(r) for r in rows]

    def get_by_id(self, term_id: int) -> Optional[SolarTerm]:
        r = SolarTerms.query.filter_by(id=term_id).first()
        return self._to_domain(r) if r else None

    def update_term(self, term_id: int, *, year: Optional[int] = None, month: Optional[int] = None, term_name: Optional[str] = None, dt_iso: Optional[str] = None) -> Optional[SolarTerm]:
        r = SolarTerms.query.filter_by(id=term_id).first()
        if not r:
            return None
        if year is not None:
            r.year = year
        if month is not None:
            r.month = month
        if term_name is not None:
            r.solar_terms_name = term_name
        if dt_iso:
            dt = datetime.fromisoformat(dt_iso)
            r.solar_terms_date = dt.date()
            r.solar_terms_time = dt.time()
        return self._to_domain(r)


