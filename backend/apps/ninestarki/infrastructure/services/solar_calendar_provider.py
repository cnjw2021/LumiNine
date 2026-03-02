"""Infrastructure implementation of ISolarCalendarProvider"""
from datetime import datetime
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from core.services.solar_calendar_service import SolarCalendarService

class SolarCalendarProvider(ISolarCalendarProvider):
    def get_calculation_year(self, dt: datetime) -> int:
        return SolarCalendarService.get_calculation_year(dt)
