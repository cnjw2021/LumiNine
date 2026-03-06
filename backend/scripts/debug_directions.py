"""Debug script: 방위 길흉 상세 덤프.

Docker 환경(backend 컨테이너)에서 실행:
    make debug-directions MAIN_STAR=7 MONTH_STAR=9

MonthlyDirectionsUseCase 와 get_fortune_status 의 출력을 비교한다.
"""
from __future__ import annotations
import os

from app import create_app
app = create_app()

with app.app_context():
    from apps.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
    from apps.ninestarki.domain.services.year_star_domain_service import YearStarDomainService
    from apps.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardDomainService
    from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
    from apps.ninestarki.infrastructure.persistence.solar_terms_repository import SolarTermsRepository
    from apps.ninestarki.infrastructure.persistence.solar_starts_repository import SolarStartsRepository
    from apps.ninestarki.infrastructure.persistence.star_grid_pattern_repository import StarGridPatternRepository
    from apps.ninestarki.infrastructure.persistence.monthly_directions_repository import MonthlyDirectionsRepository
    from apps.ninestarki.domain.services.five_elements_fortune_service import FiveElementsFortuneService

    nine_star_repo = NineStarRepository()
    solar_terms_repo = SolarTermsRepository()
    solar_starts_repo = SolarStartsRepository()
    star_grid_repo = StarGridPatternRepository()
    monthly_repo = MonthlyDirectionsRepository()

    year_star_svc = YearStarDomainService(nine_star_repo, solar_terms_repo, solar_starts_repo, star_grid_repo)
    monthly_board_svc = MonthlyBoardDomainService(solar_terms_repo, solar_starts_repo, star_grid_repo, monthly_repo)
    five_elements_svc = FiveElementsFortuneService()
    uc = MonthlyDirectionsUseCase(year_star_svc, monthly_board_svc, five_elements_svc)

    MAIN_STAR = int(os.environ.get("MAIN_STAR", 7))
    MONTH_STAR = int(os.environ.get("MONTH_STAR", 9))
    TARGET_YEAR = int(os.environ.get("TARGET_YEAR", 2026))
    SETSU_MONTH = int(os.environ.get("SETSU_MONTH", 2))

    print(f"=== Debug: main={MAIN_STAR} month={MONTH_STAR} year={TARGET_YEAR} setsu={SETSU_MONTH} ===\n")

    result = uc.execute(MAIN_STAR, MONTH_STAR, TARGET_YEAR, target_month=SETSU_MONTH)

    for key, board in result.get("monthly_boards", {}).items():
        print(f"center_star   : {board['center_star']}")
        print(f"month_zodiac  : {board['month_zodiac']}")

        year_info = result.get("year_info", {})
        print(f"year_center   : {year_info.get('year_center_star')}")
        print(f"year_zodiac   : {year_info.get('year_zodiac')}")

        grid = board.get("grid_pattern") or {}
        directions_list = ['southeast', 'south', 'southwest', 'east', 'west', 'northeast', 'north', 'northwest']
        star_values = {d: grid.get(d, '?') for d in directions_list}
        print(f"\nGrid ({board['center_star']}中宮):")
        print(f"  SE={star_values['southeast']}  S={star_values['south']}  SW={star_values['southwest']}")
        print(f"  E ={star_values['east']}  C={board['center_star']}  W ={star_values['west']}")
        print(f"  NE={star_values['northeast']}  N={star_values['north']}  NW={star_values['northwest']}")

        print("\n=== 방위판 결과 ===")
        for direction in directions_list:
            data = board.get("directions", {}).get(direction, {})
            auspicious = data.get("is_auspicious", "?")
            marks = data.get("marks", [])
            reason = data.get("reason", "")
            compat = data.get("compatibility_level", "")
            fortune_level = data.get("fortune_level", "")
            symbol = "◎" if fortune_level == "best_auspicious" else "○" if fortune_level == "auspicious" else "×" if fortune_level == "inauspicious" else "·"
            reason_str = reason or ""
            print(f"  {symbol} {direction:10s} level={fortune_level:18s} reason={reason_str:30s} marks={marks}  compat={compat}")

    print("\n=== 기대 결과 (타 서비스 기준 2026년 3월, main=7 month=9) ===")
    print("  S  = 吉 (最大吉方)")
    print("  NE = 吉")
    print("  E  = 凶 (五黄殺)")
