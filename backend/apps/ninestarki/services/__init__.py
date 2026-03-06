"""Service module for the NineStarKi app."""

from .star_attribute_service import StarAttributeService
from .year_fortune_service import YearFortuneService
from .compatibility_service import CompatibilityService
from .pattern_switch_service import PatternSwitchService

__all__ = [
    'StarAttributeService',
    'YearFortuneService',
    'CompatibilityService',
    'PatternSwitchService',
]