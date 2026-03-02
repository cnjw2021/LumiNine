"""Infrastructure implementation for ISolarStartsRepository"""
from typing import Optional, Any
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from core.models.solar_starts import SolarStarts
from core.database import read_only_session
from core.exceptions import ExternalServiceError

class SolarStartsRepository(ISolarStartsRepository):
    def get_by_year(self, year: int) -> Optional[Any]:
        try:
            with read_only_session() as read_session:
                return read_session.query(SolarStarts).filter_by(year=year).first()
        except Exception as e:
            raise ExternalServiceError("Failed to fetch SolarStarts by year", details=str(e)) from e
