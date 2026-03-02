"""モデルモジュール"""

from .admin_account_limit import AdminAccountLimit
from .system_config import SystemConfig
from .solar_starts import SolarStarts
from .solar_terms import SolarTerms
from .star_attribute import StarAttribute
from .monthly_star_reading import MonthlyStarReading
from .daily_star_reading import DailyStarReading
from .star_groups import StarGroups, StarGroup
from .monthly_directions import MonthlyDirections

from .compatibility_readings_master import CompatibilityReadingsMaster
from .compatibility_symbol_master import CompatibilitySymbolMaster
from .compatibility_symbol_pattern_master import CompatibilitySymbolPatternMaster
from .compatibility_master import CompatibilityMaster
from .hourly_star_zodiac import HourlyStarZodiac
from .zodiac_group import ZodiacGroup
from .zodiac_group_member import ZodiacGroupMember

from .pattern_switch_date import PatternSwitchDate

# 全てのモデルをエクスポート
__all__ = [
    'AdminAccountLimit',
    'SystemConfig',
    'SolarStarts',
    'SolarTerms',
    'StarGroups',
    'StarGroup',
    'MonthlyStarReading',
    'DailyStarReading',
    'StarAttribute',
    'MonthlyDirections',
    'CompatibilityReadingsMaster',
    'CompatibilitySymbolMaster',
    'CompatibilitySymbolPatternMaster',
    'CompatibilityMaster',
    'HourlyStarZodiac',
    'ZodiacGroup',
    'ZodiacGroupMember',
    'PatternSwitchDate'
] 