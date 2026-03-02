from typing import TypedDict, Dict, Any


class AnnualDirectionsResponseDTO(TypedDict, total=False):
    main_star: int
    month_star: int
    target_year: int
    annual_directions: Dict[str, Any]


class MonthAcquiredFortuneResponseDTO(TypedDict, total=False):
    main_star: int
    month_star: int
    target_year: int
    annual_directions: Dict[str, Any]


