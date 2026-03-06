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

    nine_star_repo = NineStarRepository()
    solar_terms_repo = SolarTermsRepository()
    solar_starts_repo = SolarStartsRepository()
    star_grid_repo = StarGridPatternRepository()
    monthly_repo = MonthlyDirectionsRepository()

    year_star_svc = YearStarDomainService(nine_star_repo, solar_terms_repo, solar_starts_repo, star_grid_repo)
    monthly_board_svc = MonthlyBoardDomainService(solar_terms_repo, monthly_repo, star_grid_repo)
    uc = MonthlyDirectionsUseCase(year_star_svc, monthly_board_svc)

    MAIN_STAR = int(os.environ.get("MAIN_STAR", 7))
    MONTH_STAR = int(os.environ.get("MONTH_STAR", 9))
    TARGET_YEAR = int(os.environ.get("TARGET_YEAR", 2026))
    SETSU_MONTH = int(os.environ.get("SETSU_MONTH", 2))

    print(f"=== Debug: main={MAIN_STAR} month={MONTH_STAR} year={TARGET_YEAR} setsu={SETSU_MONTH} ===\n")

    result = uc.execute(main_star=MAIN_STAR, month_star=MONTH_STAR,
                        target_year=TARGET_YEAR, target_month=SETSU_MONTH)

    key = f"setsu_month_{SETSU_MONTH}"
    board = result["monthly_boards"][key]

    print(f"center_star   : {board['center_star']}")
    print(f"month_zodiac  : {board['month_zodiac']}")
    print(f"year_center   : {result.get('year_center_star')}")
    print(f"year_zodiac   : {result.get('year_zodiac')}")

    grid_pattern = star_grid_repo.get_by_center_star(board["center_star"])
    if grid_pattern:
        print(f"\nGrid ({board['center_star']}中宮):")
        print(f"  SE={grid_pattern.southeast}  S={grid_pattern.south}  SW={grid_pattern.southwest}")
        print(f"  E ={grid_pattern.east}  C={grid_pattern.center_star}  W ={grid_pattern.west}")
        print(f"  NE={grid_pattern.northeast}  N={grid_pattern.north}  NW={grid_pattern.northwest}")

    print("\n=== 방위판 결과 ===")
    for direction, data in board["directions"].items():
        auspicious = data.get("is_auspicious")
        marks = data.get("marks", [])
        reason = data.get("reason", "")
        compat = data.get("compatibility_level", "")
        symbol = "○" if auspicious else "×"
        print(f"  {symbol} {direction:10s} auspicious={str(auspicious):5s} reason={reason:30s} marks={marks}  compat={compat}")

    print("\n=== 기대 결과 (타 서비스 기준 2026년 3월, main=7 month=9) ===")
    print("  S  = 吉 (最大吉方)")
    print("  NE = 吉")
    print("  E  = 凶 (五黄殺)")
