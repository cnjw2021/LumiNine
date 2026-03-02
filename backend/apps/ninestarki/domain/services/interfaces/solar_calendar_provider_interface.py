"""Domain service interface to abstract calendar calculations used by UseCases."""
from abc import ABC, abstractmethod
from datetime import datetime

class ISolarCalendarProvider(ABC):
    @abstractmethod
    def get_calculation_year(self, dt: datetime) -> int:
        """Return the Ninestar calculation year for given datetime."""
        raise NotImplementedError
