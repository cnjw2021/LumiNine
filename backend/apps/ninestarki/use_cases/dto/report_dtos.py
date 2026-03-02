from typing import TypedDict, Optional, Dict, Any

class PartnerDTO(TypedDict, total=False):
    fullName: str
    birthdate: str  # YYYY-MM-DD
    gender: str     # 'male' | 'female'

class ReportInputDTO(TypedDict, total=False):
    full_name: str
    birthdate: str
    gender: str
    target_year: int
    template_id: int
    background_id: int
    use_simple: bool
    partner: Optional[PartnerDTO]
    # result_data 등은 서버 재계산 후 컨텍스트로 이동

class ReportContextDTO(TypedDict, total=False):
    user_info: Dict[str, Any]
    ninestar_info: Dict[str, Any]
    auspicious_day_result: Any
    year_fortune: Any
    month_fortune: Any
    main_star_attributes: Dict[str, Any]
    month_star_attributes: Dict[str, Any]
    guidance_data: Dict[str, Any]
    direction_fortune: Dict[str, Any]
    year_zodiac: Any
    spring_start_date: Any
    spring_end_date: Any
    template_id: int
    background_id: int
    use_simple: bool
    compatibility: Any
    report_date: str
