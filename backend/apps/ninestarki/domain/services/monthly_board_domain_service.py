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

    def _determine_setsu_month(
        self, target_date: date, lookup_year: int
    ) -> tuple[int, date, date]:
        """target_date 가 속하는 절월(節月) 인덱스와 기간(시작일/종료일)을 返す.

        【설계 주의】
        DB의 SolarTerm.month 는 그레고리력 월(1월=1, 2월=2…)이며,
        절월 인덱스(寅月=1, 卯月=2 … 丑月=12)와 직접 대응하지 않는다.
        따라서 절월 인덱스는 solar_terms_date 순으로 정렬 후 0-based 위치 + 1 로 산출한다.

        절기 시퀀스 순서 (절월 인덱스 기준):
          idx=1 (寅月) ← 立春 (약 2월)
          idx=2 (卯月) ← 啓蟄 (약 3월)
          …
          idx=11 (子月) ← 大雪 (약 12월)
          idx=12 (丑月) ← 小寒 (약 다음해 1월)

        Returns:
            (setsu_month_index, period_start_date, period_end_date)

        Raises:
            ValueError: 해당 연도 절기 데이터가 DB에 없는 경우
        """
        terms_prev_year = self._solar_terms_repo.get_yearly_terms(lookup_year - 1)
        terms_curr_year = self._solar_terms_repo.get_yearly_terms(lookup_year)
        terms_next_year = self._solar_terms_repo.get_yearly_terms(lookup_year + 1)

        if not terms_curr_year:
            raise ValueError(
                f"절기 데이터를 찾을 수 없습니다. year={lookup_year}. "
                "DB에 solar_terms 데이터를 확인해 주세요."
            )

        # solar_terms_date 기준으로 정렬 — SolarTerm.month(그레고리력) 기준이 아님
        all_terms = sorted(
            [*terms_prev_year, *terms_curr_year, *terms_next_year],
            key=lambda t: t.solar_terms_date,
        )

        # target_date 직전(또는 당일)의 절기를 찾는다
        matched_idx: Optional[int] = None
        for i, term in enumerate(reversed(all_terms)):
            if term.solar_terms_date <= target_date:
                matched_idx = len(all_terms) - 1 - i
                break

        if matched_idx is None:
            raise ValueError(
                f"target_date={target_date} に対応する절월을 찾을 수 없습니다。"
            )

        matched_term = all_terms[matched_idx]

        # 절월 인덱스 = 해당 연도(lookup_year)의 절기 시퀀스에서 몇 번째인지 (1-indexed)
        # 연도별 절기 12개를 solar_terms_date 순으로 재정렬해 순위를 결정한다
        curr_year_sorted = sorted(terms_curr_year, key=lambda t: t.solar_terms_date)
        # matched_term 이 curr_year 에 없으면(전해/다음해 절기) 가장 가까운 것으로 폴백
        if matched_term in curr_year_sorted:
            setsu_month_index = curr_year_sorted.index(matched_term) + 1
        else:
            # prev_year 최후 절기 → 12월 (丑月)에 해당
            setsu_month_index = 12

        # setsu_month_index 를 1~12 로 클램프
        setsu_month_index = max(1, min(12, setsu_month_index))

        # 다음 절월의 절입일 - 1 을 종료일로 한다
        next_idx = matched_idx + 1
        if next_idx < len(all_terms):
            period_end = all_terms[next_idx].solar_terms_date - timedelta(days=1)
        else:
            period_end = matched_term.solar_terms_date + timedelta(days=29)  # 폴백

        return setsu_month_index, matched_term.solar_terms_date, period_end

    def get_period_start_for_setsu(self, year: int, setsu_index: int) -> Optional[date]:
        """절월 인덱스(1=寅月…12=丑月)에 해당하는 절입일(date)을 반환한다.

        UseCase 에서 getattr() 없이 직접 접근할 수 있도록 제공하는 퍼블릭 헬퍼.

        설월 인덱스 → 그레고리력 (연, 월) 대응:
          1(寅月) → (year, 2)   立春
          2(卯月) → (year, 3)   啓蟄
          …
          11(子月) → (year, 12) 大雪
          12(丑月) → (year+1, 1) 小寒

        Args:
            year: 조회 연도 (節月 기준 해당 연도)
            setsu_index: 절월 인덱스 (1~12)

        Returns:
            절입일 date, 또는 DB에 없는 경우 None
        """
        if not 1 <= setsu_index <= 12:
            logger.warning("get_period_start_for_setsu: invalid setsu_index=%s", setsu_index)
            return None

        # 절월 인덱스 → (year, gregorian_month) 변환
        if setsu_index == 12:
            term_year, term_month = year + 1, 1   # 丑月=小寒: 다음해 1월
        else:
            term_year, term_month = year, setsu_index + 1  # 寅月=立春: 해당년 2월 …

        term = self._solar_terms_repo.get_term_by_month(term_year, term_month)
        if term is None and setsu_index == 12:
            # 丑月 폴백: DB에서 연도 경계가 다를 경우 당해 1월 시도
            term = self._solar_terms_repo.get_term_by_month(year, 1)

        return term.solar_terms_date if term else None
