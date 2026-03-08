"""Domain repository interface for SolarStarts access."""
from abc import ABC, abstractmethod
from typing import Optional, Any

class ISolarStartsRepository(ABC):
    @abstractmethod
    def get_by_year(self, year: int) -> Optional[Any]:
        """Return SolarStarts-like object having attributes zodiac and solar_starts_date."""
        raise NotImplementedError
