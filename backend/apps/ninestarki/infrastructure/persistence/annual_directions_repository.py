from __future__ import annotations
from typing import Dict, List, Optional, Any

from apps.ninestarki.domain.repositories.annual_directions_repository_interface import IAnnualDirectionsRepository
from core.models.monthly_directions import MonthlyDirections
from core.models.star_groups import StarGroups
from core.models.star_grid_pattern import StarGridPattern
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from injector import inject


class AnnualDirectionsRepository(IAnnualDirectionsRepository):
    @inject
    def __init__(self, solar_terms_repo: ISolarTermsRepository):
        self._solar_terms_repo = solar_terms_repo
    def get_monthly_directions(self, target_year: int) -> List[Dict[str, Any]]:
        # 依存を SolarTerms ポートに切り替え、core.models 内の SolarTerms 直接参照を回避
        spring_term = self._solar_terms_repo.get_spring_start(target_year)
        if not spring_term:
            return []
        group_id = StarGroups.get_group_for_star(spring_term.star_number)
        if not group_id:
            return []
        rows = MonthlyDirections.get_all_by_group(group_id)
        result: List[Dict[str, Any]] = []
        for row in rows:
            if not row:
                continue
            result.append({
                'month': row.month,
                'center_star': row.center_star,
            })
        return result

    def get_star_grid_fortune_status(self, center_star: int, base_params: Dict[str, Any]) -> Dict[str, Any]:
        grid_pattern = StarGridPattern.get_by_center_star(center_star)
        return grid_pattern.get_fortune_status(base_params) if grid_pattern else {}

    def get_yearly_solar_terms_map(self, year: int) -> Dict[int, Dict[str, Any]]:
        return {term.month: {
            'zodiac': term.zodiac,
            'solar_terms_date': term.solar_terms_date,
        } for term in self._solar_terms_repo.get_yearly_terms(year)}

    def get_solar_term_by_month(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        term = self._solar_terms_repo.get_term_by_month(year, month)
        if not term:
            return None
        return {
            'zodiac': term.zodiac,
            'solar_terms_date': term.solar_terms_date,
        }


