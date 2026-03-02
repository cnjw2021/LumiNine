from __future__ import annotations
from typing import List, Dict, Any, Optional
from injector import inject

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository


class ListSolarTermsUseCase:
    @inject
    def __init__(self, repo: ISolarTermsRepository) -> None:
        self._repo = repo

    def execute(self) -> List[Dict[str, Any]]:
        rows = self._repo.list_all()
        result: List[Dict[str, Any]] = []
        for r in rows:
            result.append({
                'year': r.year,
                'month': r.month,
                'term_name': r.solar_terms_name,
                'date': r.solar_terms_date.isoformat(),
                'time': (r.solar_terms_time.isoformat() if r.solar_terms_time else None),
            })
        return result


class UpdateSolarTermUseCase:
    @inject
    def __init__(self, repo: ISolarTermsRepository) -> None:
        self._repo = repo

    def execute(self, term_id: int, *, year: Optional[int] = None, month: Optional[int] = None, term_name: Optional[str] = None, dt_iso: Optional[str] = None) -> Optional[Dict[str, Any]]:
        updated = self._repo.update_term(term_id, year=year, month=month, term_name=term_name, dt_iso=dt_iso)
        if not updated:
            return None
        return {
            'year': updated.year,
            'month': updated.month,
            'term_name': updated.solar_terms_name,
            'date': updated.solar_terms_date.isoformat(),
            'time': (updated.solar_terms_time.isoformat() if updated.solar_terms_time else None),
        }


