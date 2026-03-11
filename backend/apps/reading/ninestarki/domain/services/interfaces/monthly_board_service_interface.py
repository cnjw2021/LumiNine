"""Domain port interface for the monthly-board (月盤) assembly service."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from apps.reading.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardResult


class IMonthlyBoardDomainService(ABC):
    """월반(月盤) 편성(組立) 서비스의 도메인 포트.

    구체적인 구현은 Domain 레이어(MonthlyBoardDomainService)에 위치하며,
    이 인터페이스를 통해 Use Case 레이어에서 의존성을 역전시킨다.

    런타임 DI(Injector)는 ABC 기반 바인딩을 사용하므로,
    이 모듈은 프로젝트 표준(ABC + @abstractmethod)에 맞춰 정의한다.
    """

    @abstractmethod
    def get_monthly_board(
        self,
        target_date: date,
    ) -> "MonthlyBoardResult":
        """주어진 날짜에 해당하는 월반(月盤) 결과를 반환한다.

        solar_terms_data 에 star_number(중궁성)와 zodiac(월간지)가
        사전 구축되어 있으므로 target_date 만 넘기면 된다.

        Args:
            target_date: 방위를 조회할 기준 날짜 (절입일 경계를 포함해 판정)

        Returns:
            MonthlyBoardResult 인스턴스
        """

    @abstractmethod
    def resolve_period_start(self, year: int, setsu_index: int) -> Optional[date]:
        """절월 인덱스를 절입일(date)로 해석하는 도메인 규칙.

        Args:
            year: 조회 연도
            setsu_index: 절월 인덱스 (1~12)

        Returns:
            절입일 date, 또는 DB에 없는 경우 None

        Raises:
            ValueError: setsu_index 가 유효 범위(1~12) 밖일 때
        """
