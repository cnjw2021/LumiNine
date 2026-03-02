"""Infrastructure implementation for IReadingQueryRepository"""
from typing import Optional, Dict, Any
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from core.utils.logger import get_logger
from core.database import read_only_session
from core.models.monthly_star_reading import MonthlyStarReading
from core.models.daily_star_reading import DailyStarReading
from core.models.main_star_acquired_fortune_message import MainStarAcquiredFortuneMessage
from core.exceptions import ExternalServiceError

logger = get_logger(__name__)

class ReadingQueryRepository(IReadingQueryRepository):
    def get_monthly_star_reading(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        if not star_number:
            return None
        try:
            with read_only_session() as read_session:
                monthly_star_reading = read_session.query(MonthlyStarReading).filter_by(star_number=star_number).first()
                if not monthly_star_reading:
                    return None
                return {
                    'id': getattr(monthly_star_reading, 'id', None),
                    'star_number': getattr(monthly_star_reading, 'star_number', None),
                    'title': getattr(monthly_star_reading, 'title', None),
                    'description': getattr(monthly_star_reading, 'description', None),
                    'keywords': getattr(monthly_star_reading, 'keywords', None),
                }
        except Exception as e:
            logger.error(f"Infra: monthly star reading fetch failed: {e}", exc_info=True)
            raise ExternalServiceError("Failed to fetch monthly star reading", details=str(e)) from e

    def get_daily_star_reading(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        if not star_number:
            return None
        try:
            with read_only_session() as read_session:
                daily_star_reading = read_session.query(DailyStarReading).filter_by(star_number=star_number).first()
                if not daily_star_reading:
                    return None
                return {
                    'id': getattr(daily_star_reading, 'id', None),
                    'star_number': getattr(daily_star_reading, 'star_number', None),
                    'title': getattr(daily_star_reading, 'title', None),
                    'description': getattr(daily_star_reading, 'description', None),
                    'keywords': getattr(daily_star_reading, 'keywords', None),
                    'advice': getattr(daily_star_reading, 'advice', ''),
                }
        except Exception as e:
            logger.error(f"Infra: daily star reading fetch failed: {e}", exc_info=True)
            raise ExternalServiceError("Failed to fetch daily star reading", details=str(e)) from e

    def get_main_star_message(self, star_number: Optional[int]) -> Optional[Dict[str, Any]]:
        if not star_number:
            return None
        try:
            with read_only_session() as read_session:
                main_star_message = read_session.query(MainStarAcquiredFortuneMessage).filter_by(star_number=star_number).first()
                if not main_star_message:
                    return None
                return {
                    'id': getattr(main_star_message, 'id', None),
                    'star_number': getattr(main_star_message, 'star_number', None),
                    'title': getattr(main_star_message, 'title', None),
                    'description': getattr(main_star_message, 'description', None),
                    'keywords': getattr(main_star_message, 'keywords', None),
                }
        except Exception as e:
            logger.error(f"Infra: main star message fetch failed: {e}", exc_info=True)
            raise ExternalServiceError("Failed to fetch main star message", details=str(e)) from e
