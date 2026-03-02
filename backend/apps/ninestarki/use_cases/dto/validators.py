from typing import Tuple, List
from datetime import datetime
from .report_dtos import ReportInputDTO


def validate_report_input(dto: ReportInputDTO) -> Tuple[bool, List[str]]:
    """Validate minimal fields for ReportInputDTO. Returns (is_valid, missing_or_invalid_fields).
    This is a shallow validator for route boundary checks.
    """
    missing: List[str] = []

    if not dto.get('full_name'):
        missing.append('full_name')
    if not dto.get('birthdate'):
        missing.append('birthdate')
    if not dto.get('gender'):
        missing.append('gender')

    # birthdate format validation (YYYY-MM-DD)
    bd = dto.get('birthdate')
    if isinstance(bd, str):
        try:
            datetime.strptime(bd, '%Y-%m-%d')
        except Exception:
            missing.append('birthdate(format)')

    ty = dto.get('target_year')
    if ty is not None:
        try:
            ty_int = int(ty)
            if not (1900 <= ty_int <= 2100):
                missing.append('target_year(range)')
        except Exception:
            missing.append('target_year(type)')

    partner = dto.get('partner')
    if partner:
        if not partner.get('birthdate'):
            missing.append('partner.birthdate')
        else:
            try:
                datetime.strptime(partner['birthdate'], '%Y-%m-%d')
            except Exception:
                missing.append('partner.birthdate(format)')
        if not partner.get('gender'):
            missing.append('partner.gender')

    return (len(missing) == 0, missing)
