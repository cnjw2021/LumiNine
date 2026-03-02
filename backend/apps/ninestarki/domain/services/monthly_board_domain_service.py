"""월반(月盤) 편성(組立) 도메인 서비스.

설계 원칙 (Clean Architecture):
- 이 모듈은 Domain 레이어에 속하며, FastAPI·SQLAlchemy 등 인프라 구체 클래스에 의존하지 않는다.
- 외부 의존은 repository 인터페이스(ISolarTermsRepository, IStarGridPatternRepository)를 통해서만 접근한다.
- calendar_utils 는 순수 산술 연산이므로 Core 유틸로서 Domain이 의존한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

from injector import inject

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from core.utils.calendar_utils import (
    get_monthly_center_star,
    get_monthly_kanshi,
    get_year_stem_index_from_zodiac,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────
# Value Object: 월반 편성 결과
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class MonthlyBoardResult:
    """월반(月盤) 편성 결과를 담는 불변 Value Object.

    Attributes:
        setsu_month_index: 절월(節月) 인덱스 (1=寅月/立春~ … 12=丑月/小寒~)
        center_star: 월반 중궁성 (1~9)
        grid_pattern: StarGridPattern 엔티티 (방위별 별 배치). None 이면 DB 미등록.
        month_stem: 月天干 문자 (예: '丙')
        month_branch: 月地支 문자 (예: '寅')
        month_zodiac: 月干支 결합 문자열 (예: '丙寅')
        period_start: 해당 절월의 시작일 (절입일)
        period_end: 해당 절월의 종료일 (다음 절입일 -1)
    """
    setsu_month_index: int
    center_star: int
    grid_pattern: Optional[Any]
    month_stem: str
    month_branch: str
    month_zodiac: str
    period_start: date
    period_end: date

    def to_dict(self) -> dict:
        return {
            "setsu_month_index": self.setsu_month_index,
            "center_star": self.center_star,
            "month_stem": self.month_stem,
            "month_branch": self.month_branch,
            "month_zodiac": self.month_zodiac,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "grid_pattern": self.grid_pattern.to_dict() if self.grid_pattern else None,
        }


# ──────────────────────────────────────────────
# Domain Service
# ──────────────────────────────────────────────

class MonthlyBoardDomainService:
    """월반(月盤) 편성 파이프라인을 총괄하는 도메인 서비스.

    연반 중궁성과 연간지를 입력받아 지정 날짜에 해당하는 절월(節月)을 결정하고,
    `get_monthly_center_star` / `get_monthly_kanshi` 를 통해 월반을 편성한다.

    의존성은 생성자 주입(injector) 방식으로 공급된다.
    """

    @inject
    def __init__(
        self,
        solar_terms_repo: ISolarTermsRepository,
        star_grid_repo: IStarGridPatternRepository,
    ) -> None:
        self._solar_terms_repo = solar_terms_repo
        self._star_grid_repo = star_grid_repo

    # ──────────────────────────────
    # Public API
    # ──────────────────────────────

    def get_monthly_board(
        self,
        target_date: date,
        year_center_star: int,
        year_zodiac: str,
    ) -> MonthlyBoardResult:
        """주어진 날짜가 속하는 절월(節月)의 월반(月盤)을 편성해 반환한다.

        Args:
            target_date: 기준 날짜 (절입일 경계를 포함해 판정)
            year_center_star: 해당 연도의 연반 중궁성 (1~9)
            year_zodiac: 해당 연도의 연간지 (예: '甲子')

        Returns:
            MonthlyBoardResult

        Raises:
            ValueError: 절기 데이터가 DB에 없거나 year_zodiac 포맷이 올바르지 않은 경우
        """
        # 1. 연도 천간 인덱스 추출 (五虎遁 계산에 사용)
        year_stem_index = get_year_stem_index_from_zodiac(year_zodiac)

        # 2. target_date 가 속하는 절월(節月) 결정
        setsu_month_index, period_start, period_end = self._determine_setsu_month(
            target_date, target_date.year
        )

        # 3. 월반 중궁성 산출 (역행 공식)
        monthly_center_star = get_monthly_center_star(year_center_star, setsu_month_index)

        # 4. 월간지(月干支) 산출 (五虎遁)
        month_stem, month_branch = get_monthly_kanshi(year_stem_index, setsu_month_index)

        # 5. StarGridPattern 조회
        grid_pattern = self._star_grid_repo.get_by_center_star(monthly_center_star)
        if grid_pattern is None:
            logger.warning(
                "StarGridPattern が見つかりません。center_star=%d", monthly_center_star
            )

        return MonthlyBoardResult(
            setsu_month_index=setsu_month_index,
            center_star=monthly_center_star,
            grid_pattern=grid_pattern,
            month_stem=month_stem,
            month_branch=month_branch,
            month_zodiac=month_stem + month_branch,
            period_start=period_start,
            period_end=period_end,
        )

    # ──────────────────────────────
    # Private helpers
    # ──────────────────────────────

    def _determine_setsu_month(
        self, target_date: date, lookup_year: int
    ) -> tuple[int, date, date]:
        """target_date 가 속하는 절월(節月) 인덱스와 기간(시작일/종료일)을 返す.

        절입일은 ISolarTermsRepository 경유로 DB에서 취득한다.
        절입일 이전이면 이전 절월에 속한다.

        Returns:
            (setsu_month_index, period_start_date, period_end_date)

        Raises:
            ValueError: 해당 연도 전후 절기 데이터가 DB에 없는 경우
        """
        # 당해 연도 + 전해 연도의 절기를 취득해 절입일 경계 리스트를 구성한다.
        # 節月 인덱스 1(寅月)는 立春(2月절기) 부터 시작, 12(丑月)는 小寒(1月절기)까지이므로
        # 이전 연도의 12월 절기(小寒)도 필요하다.
        terms_prev_year = self._solar_terms_repo.get_yearly_terms(lookup_year - 1)
        terms_curr_year = self._solar_terms_repo.get_yearly_terms(lookup_year)
        terms_next_year = self._solar_terms_repo.get_yearly_terms(lookup_year + 1)

        if not terms_curr_year:
            raise ValueError(
                f"절기 데이터를 찾을 수 없습니다. year={lookup_year}. "
                "DB에 solar_terms 데이터를 확인해 주세요."
            )

        # 月 → 절입일 매핑 (연도별로 month=1~12 가 각각 存在)
        # SolarTerm.month 는 節月 인덱스와 같은 의미
        all_terms = sorted(
            [*terms_prev_year, *terms_curr_year, *terms_next_year],
            key=lambda t: (t.year, t.month),
        )

        # target_date 직전(또는 당일)의 절기를 찾아 절월 인덱스를 결정
        matched_term = None
        for term in reversed(all_terms):
            if term.solar_terms_date <= target_date:
                matched_term = term
                break

        if matched_term is None:
            raise ValueError(
                f"target_date={target_date} に対応する절월을 찾을 수 없습니다。"
            )

        setsu_month_index = matched_term.month  # 1~12

        # 다음 절월의 절입일 - 1 을 종료일로 한다
        next_idx = all_terms.index(matched_term) + 1
        if next_idx < len(all_terms):
            next_term = all_terms[next_idx]
            period_end = next_term.solar_terms_date - timedelta(days=1)
        else:
            period_end = matched_term.solar_terms_date + timedelta(days=29)  # 폴백

        return setsu_month_index, matched_term.solar_terms_date, period_end
