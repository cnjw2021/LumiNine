"""월반(月盤) 편성(組立) 도메인 서비스.

설계 원칙 (Clean Architecture):
- 이 모듈은 Domain 레이어에 속하며, FastAPI·SQLAlchemy 등 인프라 구체 클래스에 의존하지 않는다.
- 외부 의존은 repository 인터페이스(ISolarTermsRepository, IStarGridPatternRepository,
  IMonthlyDirectionsRepository)를 통해서만 접근한다.
- solar_terms_data 의 star_number 는 절기운성이며, 월반 중궁성은 그룹 판정 →
  monthly_directions 테이블 경유로 결정한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

from injector import inject

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.domain.exceptions import SetsuMonthNotFoundError
from apps.ninestarki.domain.services.interfaces.monthly_board_service_interface import IMonthlyBoardDomainService
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

class MonthlyBoardDomainService(IMonthlyBoardDomainService):
    """월반(月盤) 편성 파이프라인을 총괄하는 도메인 서비스.

    solar_terms_data 의 절기 정보(날짜·간지)와 monthly_directions 테이블의
    그룹별 월반 중궁성을 사용하여 지정 날짜에 해당하는 절월을 결정하고 월반을 편성한다.

    의존성은 생성자 주입(injector) 방식으로 공급된다.
    """

    @inject
    def __init__(
        self,
        solar_terms_repo: ISolarTermsRepository,
        solar_starts_repo: ISolarStartsRepository,
        star_grid_repo: IStarGridPatternRepository,
        monthly_directions_repo: IMonthlyDirectionsRepository,
    ) -> None:
        self._solar_terms_repo = solar_terms_repo
        self._solar_starts_repo = solar_starts_repo
        self._star_grid_repo = star_grid_repo
        self._monthly_directions_repo = monthly_directions_repo

    # ──────────────────────────────
    # Public API
    # ──────────────────────────────

    def get_monthly_board(
        self,
        target_date: date,
    ) -> MonthlyBoardResult:
        """주어진 날짜가 속하는 절월(節月)의 월반(月盤)을 편성해 반환한다.

        절기 정보(날짜·간지)는 solar_terms_data 에서 조회하고,
        월반 중궁성은 立春 의 star_number 로부터 그룹을 산출한 뒤,
        해당 그룹을 사용해 monthly_directions 테이블에서 조회해 결정한다.

        Args:
            target_date: 기준 날짜 (절입일 경계를 포함해 판정)

        Returns:
            MonthlyBoardResult

        Raises:
            SetsuMonthNotFoundError: 절기 데이터가 DB에 없는 경우
        """
        # 절기 기준 연도(節年):
        # - 해당 양력 연도의 立春(입춘) 이전 날짜는 전년도의 절년으로 본다.
        # - 立春 당일 및 이후부터는 해당 연도의 절년으로 본다.
        lookup_year = target_date.year
        spring_start_term = self._solar_terms_repo.get_spring_start(lookup_year)
        if spring_start_term and target_date < spring_start_term.solar_terms_date:
            lookup_year -= 1
        elif not spring_start_term and target_date.month == 1:
            lookup_year -= 1

        matched_term, setsu_month_index, period_end = self._determine_setsu_month(
            target_date, lookup_year
        )

        month_zodiac = matched_term.zodiac          # 예: '庚寅'
        month_stem   = month_zodiac[0] if month_zodiac else ''
        month_branch = month_zodiac[1] if len(month_zodiac) > 1 else ''

        # 그룹 판정 → monthly_directions 경유로 월반 중궁성 결정
        # 주의: solar_terms_data.star_number 는 절기운성이며, 년반 중궁성이 아님.
        #       solar_starts_data.star_number 가 년반 중궁성이므로, 이를 사용하여
        #       그룹을 판정해야 한다. (1,4,7→G1 / 2,5,8→G2 / 3,6,9→G3)
        center_star = self._resolve_center_star(
            lookup_year, matched_term.month,
        )

        # StarGridPattern 조회
        grid_pattern = self._star_grid_repo.get_by_center_star(center_star)
        if grid_pattern is None:
            logger.warning("StarGridPattern が見つかりません。center_star=%d", center_star)

        return MonthlyBoardResult(
            setsu_month_index=setsu_month_index,
            center_star=center_star,
            grid_pattern=grid_pattern,
            month_stem=month_stem,
            month_branch=month_branch,
            month_zodiac=month_zodiac,
            period_start=matched_term.solar_terms_date,
            period_end=period_end,
        )

    def _resolve_center_star(
        self, lookup_year: int, calendar_month: int,
    ) -> int:
        """그룹 판정 → monthly_directions 경유로 월반 중궁성을 결정한다.

        1. 해당 절년의 年盤中宮星(solar_starts_data.star_number) 조회
        2. 年盤中宮星 을 3으로 나눈 나머지로 그룹 판정
           (1, 4, 7 → group_id=1 / 2, 5, 8 → group_id=2 / 3, 6, 9 → group_id=3)
        3. monthly_directions(group_id, month) 에서 center_star 취득

        중요: solar_terms_data.star_number 는 절기운성(節気運星)이지,
              年盤中宮星이 아니다. 그룹 판정에는 solar_starts_data.star_number
              를 사용해야 한다.

        Args:
            lookup_year: 절년(節年) 기준 연도
            calendar_month: 양력 월 (1~12, solar_terms_data.month)

        Returns:
            center_star (1~9)

        Raises:
            SetsuMonthNotFoundError: 年盤 데이터 또는 monthly_directions 데이터가 없는 경우
        """
        # solar_starts_data 에서 年盤中宮星 조회
        year_starts = self._solar_starts_repo.get_by_year(lookup_year)
        if not year_starts:
            raise SetsuMonthNotFoundError(
                f"solar_starts 데이터를 찾을 수 없습니다. year={lookup_year}",
                details="DB에 solar_starts_data 를 확인해 주세요.",
            )
        year_center_star: int = year_starts.star_number

        # 그룹 판정: 1,4,7→G1 / 2,5,8→G2 / 3,6,9→G3
        group_id = year_center_star % 3
        if group_id == 0:
            group_id = 3

        monthly_dir = self._monthly_directions_repo.get_by_group_and_month(
            group_id, calendar_month
        )
        if not monthly_dir:
            raise SetsuMonthNotFoundError(
                f"monthly_directions 데이터를 찾을 수 없습니다. "
                f"group={group_id}, month={calendar_month}",
                details="monthly_directions 테이블 데이터를 확인해 주세요.",
            )

        logger.debug(
            "center_star resolved: year=%d month=%d → year_center_star=%d "
            "→ group=%d → center_star=%d",
            lookup_year, calendar_month, year_center_star,
            group_id, monthly_dir.center_star,
        )
        return monthly_dir.center_star

    def _determine_setsu_month(
        self, target_date: date, lookup_year: int
    ) -> tuple[Any, int, date]:
        """target_date 가 속하는 절기 레코드, 절월 인덱스, 종료일을 반환한다.

        【DB 구조】
        solar_terms_data.month 는 그레고리력 월:
          month=2 → 立春 (setsu_index=1)
          month=3 → 啓蟄 (setsu_index=2)  …
          month=12 → 大雪 (setsu_index=11)
          month=1(다음해) → 小寒 (setsu_index=12)
        solar_terms_date 순으로 정렬하면 자동으로 절월 순서와 일치한다.

        Returns:
            (matched_term, setsu_month_index, period_end_date)
        """
        terms_curr_year = self._solar_terms_repo.get_yearly_terms(lookup_year)
        terms_next_year = self._solar_terms_repo.get_yearly_terms(lookup_year + 1)

        if not terms_curr_year:
            raise SetsuMonthNotFoundError(
                f"절기 데이터를 찾을 수 없습니다. year={lookup_year}",
                details="DB에 solar_terms 데이터를 확인해 주세요.",
            )

        # 절월 시퀀스: lookup_year 의 2~12월 + 다음해 1월(小寒) — solar_terms_date 오름차순
        setsu_sequence = sorted(
            [t for t in terms_curr_year if t.solar_terms_date.month != 1]
            + [t for t in terms_next_year if t.solar_terms_date.month == 1],
            key=lambda t: t.solar_terms_date,
        )

        # target_date 직전(또는 당일)의 절기를 찾는다
        matched_term = None
        matched_pos = None
        for i, term in enumerate(setsu_sequence):
            if term.solar_terms_date <= target_date:
                matched_term = term
                matched_pos = i

        if matched_term is None:
            # target_date 가 해당 연도 첫 절기(立春) 이전 → 전년 丑月(=12)
            prev_year_jan = sorted(
                [t for t in self._solar_terms_repo.get_yearly_terms(lookup_year)
                 if t.solar_terms_date.month == 1],
                key=lambda t: t.solar_terms_date,
            )
            if prev_year_jan:
                matched_term = prev_year_jan[-1]
                matched_pos = None  # 시퀀스 外
            else:
                raise SetsuMonthNotFoundError(
                    f"절기 데이터를 찾을 수 없습니다. target_date={target_date}",
                    details="DB의 solar_terms 테이블에 해당 날짜 이전/당일 절기가 존재하는지 확인해 주세요.",
                )

        # 위치 기반 setsu_month_index (1-indexed)
        if matched_pos is not None:
            setsu_month_index = matched_pos + 1
        else:
            setsu_month_index = 12  # 丑月 폴백
        setsu_month_index = max(1, min(12, setsu_month_index))

        # 종료일 = 다음 절기 전날
        if matched_pos is not None and matched_pos + 1 < len(setsu_sequence):
            period_end = setsu_sequence[matched_pos + 1].solar_terms_date - timedelta(days=1)
        else:
            # setsu_sequence 에서 다음 절기를 찾지 못한 경우:
            # 절월 인덱스를 기반으로 다음 절입일을 조회하여 종료일을 계산한다.
            if setsu_month_index == 12:
                # matched_term.solar_terms_date는 (year + 1)년 1월의 小寒
                setsu_year = matched_term.solar_terms_date.year - 1
            else:
                setsu_year = matched_term.solar_terms_date.year

            # 다음 절월 인덱스와 절년 계산
            if setsu_month_index == 12:
                next_setsuyear = setsu_year + 1
                next_index = 1  # 丑月 다음은 寅月(立春)
            else:
                next_setsuyear = setsu_year
                next_index = setsu_month_index + 1

            next_start = self.get_period_start_for_setsu(next_setsuyear, next_index)
            if next_start is not None:
                period_end = next_start - timedelta(days=1)
            else:
                # DB에 다음 절입일이 없을 때의 최후 폴백 (기존 동작 보존)
                period_end = matched_term.solar_terms_date + timedelta(days=29)

        return matched_term, setsu_month_index, period_end

    def get_period_start_for_setsu(self, year: int, setsu_index: int) -> Optional[date]:
        """절월 인덱스(1=寅月…12=丑月)에 해당하는 절입일(date)을 반환한다.

        UseCase 에서 getattr() 없이 직접 접근할 수 있도록 제공하는 퍼블릭 헬퍼.

        절월 인덱스 → 그레고리력 (연, 월) 대응:
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
