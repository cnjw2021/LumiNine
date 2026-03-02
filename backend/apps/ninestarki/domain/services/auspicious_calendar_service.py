from __future__ import annotations

from typing import List, Tuple
from datetime import date, timedelta

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.entities.solar_term import SolarTerm


class AuspiciousCalendarService:
    """
    吉日計算に必要な節気関連のドメインロジックを提供するサービス。
    - 立春日、年星、年度の節気配列、日付範囲などをポート経由で取得/計算する。
    - インフラ層に依存しない。必要なデータはISolarTermsRepositoryポートから供給される。
    """

    @staticmethod
    def get_spring_start(target_year: int, solar_terms_repo: ISolarTermsRepository) -> date:
        spring_term = solar_terms_repo.get_spring_start(target_year)
        if not spring_term:
            raise ValueError(f"立春データが存在しません: {target_year}年")
        return spring_term.solar_terms_date

    @staticmethod
    def get_year_star(target_year: int, solar_terms_repo: ISolarTermsRepository) -> int:
        spring_term = solar_terms_repo.get_spring_start(target_year)
        if not spring_term:
            raise ValueError(f"立春データが存在しません: {target_year}年")
        return spring_term.star_number

    @staticmethod
    def get_solar_terms_for_year(year: int, solar_terms_repo: ISolarTermsRepository) -> List[SolarTerm]:
        terms: List[SolarTerm] = []
        # 当年2月~12月
        for month in range(2, 13):
            term = solar_terms_repo.get_term_by_month(year, month)
            if term:
                terms.append(term)
        # 翌年1月
        next_january = solar_terms_repo.get_term_by_month(year + 1, 1)
        if next_january:
            terms.append(next_january)
        return sorted(terms, key=lambda t: t.solar_terms_date)

    @staticmethod
    def calculate_date_range(year: int, solar_terms_repo: ISolarTermsRepository) -> Tuple[date, date]:
        start_date = AuspiciousCalendarService.get_spring_start(year, solar_terms_repo)
        end_date = AuspiciousCalendarService.get_spring_start(year + 1, solar_terms_repo) - timedelta(days=1)
        return start_date, end_date

    @staticmethod
    def get_period_range(term_records: List[SolarTerm], idx: int, end_date: date) -> Tuple[date, date]:
        period_start = term_records[idx].solar_terms_date
        if idx + 1 < len(term_records):
            period_end = term_records[idx + 1].solar_terms_date - timedelta(days=1)
        else:
            period_end = end_date
        return period_start, period_end


