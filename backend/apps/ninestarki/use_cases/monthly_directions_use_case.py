"""월반 방위 산출 유즈케이스 (Monthly Directions Use Case).

처리 흐름:
1. YearStarDomainService → 연반 중궁성 + 연간지 취득
2. MonthlyBoardDomainService → 절월(節月) 결정 + 월반 편성 (solar_terms_data 직접 조회)
3. StarGridPattern.get_fortune_status() → 길흉방위 판정
4. 응답 dict 반환
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from injector import inject

from apps.ninestarki.domain.services.year_star_domain_service import YearStarDomainService
from apps.ninestarki.domain.services.interfaces.monthly_board_service_interface import IMonthlyBoardDomainService
from apps.ninestarki.domain.exceptions import (
    YearInfoNotFoundError,
    MonthlyBoardCalculationError,
    SetsuMonthNotFoundError,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)


class MonthlyDirectionsUseCase:
    """월반(月盤) 기준 방위 길흉 판정 유즈케이스.

    Args:
        year_star_service: 연반 중궁성 / 연간지 정보 제공
        monthly_board_service: 월반 편성 도메인 포트 (IMonthlyBoardDomainService)
    """

    @inject
    def __init__(
        self,
        year_star_service: YearStarDomainService,
        monthly_board_service: IMonthlyBoardDomainService,
    ) -> None:
        self._year_star_service = year_star_service
        self._monthly_board = monthly_board_service

    def execute(
        self,
        main_star: int,
        month_star: int,
        target_year: int,
        target_month: Optional[int] = None,
    ) -> Dict[str, Any]:
        """월반 방위 길흉 결과를 반환한다.

        Args:
            main_star: 사용자 본명성 (1~9)
            month_star: 사용자 월명성 (1~9)
            target_year: 조회 연도
            target_month: 조회 절월(節月) 인덱스 (1=寅月/立春 … 12=丑月/小寒).
                None 이면 해당 연도 전체 절월(1~12)에 대해 월반 방위를 산출한다.

        Returns:
            {
                "main_star": int,
                "month_star": int,
                "target_year": int,
                "monthly_boards": {
                    "setsu_month_1": { ... },
                    ...
                }
            }
        """
        logger.info(
            "MonthlyDirectionsUseCase.execute: main=%d month=%d year=%d target_month=%s",
            main_star, month_star, target_year, target_month,
        )

        # ── 1. 연반 정보 취득 ──────────────────────────
        year_info = self._year_star_service.get_year_star_info(target_year)
        if not year_info:
            raise YearInfoNotFoundError(
                f"연반 정보를 찾을 수 없습니다. year={target_year}",
                details=f"solar_starts_data에 year={target_year} 데이터가 없습니다.",
            )

        year_center_star: int = year_info["star_number"]
        year_zodiac: str = year_info.get("zodiac", "")
        if not year_zodiac:
            raise YearInfoNotFoundError(
                f"연간지(年干支) 정보가 없습니다. year={target_year}",
                details="solar_starts_data.zodiac 컬럼을 확인하세요.",
            )

        # ── 2. 대상 절월(節月) 범위 결정 ──────────────
        # target_month 가 지정된 경우: 해당 월의 대표 날짜로 1절월만 조회
        # 지정 없는 경우: target_year 의 1월(寅月)~12월(丑月) 전체 순회
        if target_month is not None:
            months_to_query = [target_month]
        else:
            months_to_query = list(range(1, 13))

        # ── 3. 각 절월별 월반 편성 + 방위 판정 ────────
        monthly_boards: Dict[str, Any] = {}

        for setsu_index in months_to_query:
            try:
                # 절월 인덱스 1(寅月) → 입춘 직후인 날짜를 SolarTermsRepo 에서 취득하기 위해
                # 임시로 편의 날짜를 이용한다.
                # 실제로는 _solar_terms_repo 경유로 절입일을 특정하므로 여기선 해당 절월의
                # 「절입일 당일」을 get_monthly_board 에 넘기면 된다.
                period_start = self._resolve_setsu_month_start(target_year, setsu_index)
                if period_start is None:
                    logger.warning("절입일 미취득 setsu_index=%d year=%d", setsu_index, target_year)
                    continue

                board_result = self._monthly_board.get_monthly_board(
                    target_date=period_start,
                )

                # ── 4. 방위 길흉 판정 ──────────────────
                fortune_status: Dict[str, Any] = {}
                if board_result.grid_pattern is not None:
                    fortune_params = {
                        "main_star": main_star,
                        "month_star": month_star,
                        "year_star": year_center_star,
                        "zodiac": board_result.month_zodiac,
                    }
                    fortune_status = board_result.grid_pattern.get_fortune_status(fortune_params)

                key = f"setsu_month_{setsu_index}"
                monthly_boards[key] = {
                    "setsu_month_index": board_result.setsu_month_index,
                    "center_star": board_result.center_star,
                    "month_zodiac": board_result.month_zodiac,
                    "month_stem": board_result.month_stem,
                    "month_branch": board_result.month_branch,
                    "period_start": board_result.period_start.isoformat(),
                    "period_end": board_result.period_end.isoformat(),
                    "directions": fortune_status,
                }

            except Exception as exc:
                logger.warning(
                    "setsu_index=%d の月盤編成でエラー: %s", setsu_index, exc, exc_info=True
                )
                # 단일 월 조회인 경우에는 예외를 그대로 상위로 전파하여
                # 호출자가 명시적으로 실패를 인지할 수 있게 한다.
                if target_month is not None:
                    raise MonthlyBoardCalculationError(
                        f"절월 {setsu_index} 의 월반 편성 중 오류가 발생했습니다.",
                        details=str(exc),
                    ) from exc
                # 연간 일괄 조회인 경우에만 해당 월을 건너뛰고 나머지 월을 계속 처리한다.
                continue

        # ── 5. 결과 검증 ──────────────────────────────
        if target_month is not None and not monthly_boards:
            raise SetsuMonthNotFoundError(
                f"지정한 절월({target_month})의 데이터를 산출할 수 없습니다.",
                details="절입일이 DB에 존재하지 않거나 데이터 누락이 있습니다.",
            )

        return {
            "main_star": main_star,
            "month_star": month_star,
            "target_year": target_year,
            "year_center_star": year_center_star,
            "year_zodiac": year_zodiac,
            "monthly_boards": monthly_boards,
        }

    # ──────────────────────────────
    # Private helpers
    # ──────────────────────────────

    def _resolve_setsu_month_start(self, year: int, setsu_index: int) -> Optional[date]:
        """절월(節月) 인덱스에 해당하는 절입일(date)을 취득한다.

        MonthlyBoardDomainService.get_period_start_for_setsu() 경유로 접근하므로
        캡슐화를 유지한다. (getattr() 등의 내부 속성 직접 접근은 사용하지 않음)

        Args:
            year: 조회 연도
            setsu_index: 절월 인덱스 (1=寅月/立春 … 12=丑月/小寒)

        Returns:
            절입일, 또는 DB에 데이터가 없는 경우 None
        """
        return self._monthly_board.get_period_start_for_setsu(year, setsu_index)

