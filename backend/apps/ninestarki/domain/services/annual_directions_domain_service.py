from __future__ import annotations
from datetime import timedelta
from typing import Dict, Any
from injector import inject

from apps.ninestarki.domain.repositories.annual_directions_repository_interface import IAnnualDirectionsRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository


class AnnualDirectionsDomainService:
    @inject
    def __init__(self, annual_repo: IAnnualDirectionsRepository, solar_terms_repo: ISolarTermsRepository) -> None:
        self._annual_repo = annual_repo
        self._solar_terms_repo = solar_terms_repo

    def compute(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        annual_directions: Dict[str, Any] = {}

        monthly_rows = self._annual_repo.get_monthly_directions(target_year)
        current_map = self._annual_repo.get_yearly_solar_terms_map(target_year)
        next_map = self._annual_repo.get_yearly_solar_terms_map(target_year + 1)

        for row in monthly_rows:
            month = row.get('month')
            if not month:
                continue

            year_for_term = target_year + 1 if month == 1 else target_year
            term = self._annual_repo.get_solar_term_by_month(year_for_term, month)
            if not term:
                # 期間/干支が取れない場合はスキップ
                continue

            base_params = {
                'main_star': main_star,
                'month_star': month_star,
                'target_year': target_year,
                'zodiac': term['zodiac'],
            }

            fortune = self._annual_repo.get_star_grid_fortune_status(row['center_star'], base_params)

            year_for_display = target_year + 1 if month == 1 else target_year
            current_term = next_map.get(month) if month == 1 else current_map.get(month)

            period_info = None
            if current_term:
                next_month = 2 if month == 1 else (1 if month == 12 else month + 1)
                next_term_map = next_map if (month == 12 or month == 1) else (next_map if next_month == 1 else current_map)
                next_term = next_term_map.get(next_month)
                if next_term:
                    start_date = current_term['solar_terms_date']
                    end_date = next_term['solar_terms_date'] - timedelta(days=1)
                    period_info = {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                    }

            key = f"month_{month}"
            annual_directions[key] = {
                'year': year_for_display,
                'month': month,
                'display_month': f"{year_for_display}年{month}月",
                'zodiac': current_term['zodiac'] if current_term else '',
                'center_star': row['center_star'],
                'directions': fortune,
            }
            if period_info:
                annual_directions[key]['period_start'] = period_info['start_date']
                annual_directions[key]['period_end'] = period_info['end_date']

        return {
            'month_star': month_star,
            'target_year': target_year,
            'annual_directions': annual_directions,
        }


