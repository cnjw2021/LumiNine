"""
fortunetelling 앱 의존성 주입 모듈

도메인별 섹션으로 구성:
  1. ninestarki (구성기학)
  2. numerology (수비술)
  3. powerstone (파워스톤)
  4. shared (user, permission 공통)
"""
import os
from injector import Module, provider, singleton
from sqlalchemy.orm import Session
from core.database import db

# ─────────────────────────────────────────────────────────────
# 1. NINESTARKI (구성기학) 의존성
# ─────────────────────────────────────────────────────────────
from apps.reading.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.reading.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository

from apps.reading.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.reading.ninestarki.infrastructure.persistence.solar_starts_repository import SolarStartsRepository

from apps.reading.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.reading.ninestarki.infrastructure.services.solar_calendar_provider import SolarCalendarProvider

from apps.reading.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.reading.ninestarki.infrastructure.persistence.solar_terms_repository import SolarTermsRepository

from apps.reading.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.reading.ninestarki.infrastructure.persistence.star_grid_pattern_repository import StarGridPatternRepository

from apps.reading.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.reading.ninestarki.infrastructure.persistence.monthly_directions_repository import MonthlyDirectionsRepository

from apps.reading.ninestarki.domain.repositories.star_attribute_repository_interface import IStarAttributeRepository
from apps.reading.ninestarki.infrastructure.persistence.star_attribute_repository import StarAttributeRepository

from apps.reading.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardDomainService
from apps.reading.ninestarki.domain.services.interfaces.monthly_board_service_interface import IMonthlyBoardDomainService
from apps.reading.ninestarki.domain.services.year_star_domain_service import YearStarDomainService
from apps.reading.ninestarki.domain.services.five_elements_fortune_service import FiveElementsFortuneService
from apps.reading.ninestarki.domain.services.additional_direction_marks_service import AdditionalDirectionMarksService
from apps.reading.ninestarki.domain.services.fortune_status_service import FortuneStatusService

from apps.reading.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.reading.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase

# ─────────────────────────────────────────────────────────────
# 2. NUMEROLOGY (수비술) 의존성
# ─────────────────────────────────────────────────────────────
from apps.reading.numerology.domain.repositories.numerology_reading_repository_interface import INumerologyReadingRepository
from apps.reading.numerology.infrastructure.persistence.numerology_reading_repository import NumerologyReadingRepository

# ─────────────────────────────────────────────────────────────
# 3. POWERSTONE (파워스톤) 의존성
# ─────────────────────────────────────────────────────────────
from apps.reading.powerstone.domain.services.interfaces.gogyo_service_interface import IGogyoService
from apps.reading.powerstone.domain.services.gogyo_service import GogyoService

from apps.reading.powerstone.domain.services.interfaces.powerstone_matching_engine_interface import IPowerStoneMatchingEngine
from apps.reading.powerstone.domain.services.powerstone_matching_engine import PowerStoneMatchingEngine

from apps.reading.powerstone.domain.repositories.powerstone_repository_interface import IPowerStoneRepository
from apps.reading.powerstone.infrastructure.persistence.powerstone_repository import PowerStoneRepository

from apps.reading.powerstone.use_cases.interfaces.message_catalog_interface import IMessageCatalog
from apps.reading.powerstone.infrastructure.services.message_catalog import MessageCatalog

from apps.reading.powerstone.use_cases.powerstone_recommendation_use_case import PowerStoneRecommendationUseCase

from apps.reading.powerstone.domain.repositories.numerology_powerstone_repository_interface import INumerologyPowerStoneRepository
from apps.reading.powerstone.infrastructure.persistence.numerology_powerstone_repository import NumerologyPowerStoneRepository
from apps.reading.powerstone.domain.services.numerology_powerstone_engine import NumerologyPowerStoneEngine

from apps.reading.powerstone.use_cases.six_layer_powerstone_use_case import SixLayerPowerStoneUseCase

# ─────────────────────────────────────────────────────────────
# 4. SHARED (user, permission 공통) 의존성
# ─────────────────────────────────────────────────────────────
from apps.reading.shared.domain.repositories.user_repository_interface import IUserRepository
from apps.reading.shared.infrastructure.persistence.user_repository import UserRepository

from apps.reading.shared.domain.repositories.permission_repository_interface import IPermissionRepository
from apps.reading.shared.infrastructure.persistence.permission_repository import PermissionRepository

from apps.reading.shared.use_cases.permission_use_case import PermissionUseCase
from apps.reading.shared.use_cases.admin_user_use_case import AdminUserUseCase


class AppModule(Module):
    """
    fortunetelling 앱 의존성 주입 규칙 정의 모듈.
    도메인별 섹션으로 구성되어 있습니다.
    """

    @singleton
    @provider
    def provide_db_session(self) -> Session:
        return db.session

    # ── ninestarki ──────────────────────────────────────────
    @singleton
    @provider
    def provide_calculate_stars_use_case(
        self,
        repo: INineStarRepository,
        solar_terms_repo: ISolarTermsRepository,
        numerology_reading_repo: INumerologyReadingRepository,
        star_attr_repo: IStarAttributeRepository,
    ) -> CalculateStarsUseCase:
        return CalculateStarsUseCase(repo, solar_terms_repo, numerology_reading_repo, star_attr_repo)

    # ── shared ──────────────────────────────────────────────
    @singleton
    @provider
    def provide_permission_use_case(
        self,
        user_repo: IUserRepository,
        perm_repo: IPermissionRepository,
    ) -> PermissionUseCase:
        return PermissionUseCase(user_repo, perm_repo)

    @singleton
    @provider
    def provide_admin_user_use_case(
        self,
        user_repo: IUserRepository,
    ) -> AdminUserUseCase:
        return AdminUserUseCase(user_repo)

    def configure(self, binder):
        # ── ninestarki ────────────────────────────────────
        binder.bind(INineStarRepository, to=NineStarRepository, scope=singleton)
        binder.bind(ISolarStartsRepository, to=SolarStartsRepository, scope=singleton)
        binder.bind(ISolarCalendarProvider, to=SolarCalendarProvider, scope=singleton)
        binder.bind(ISolarTermsRepository, to=SolarTermsRepository, scope=singleton)
        binder.bind(IStarGridPatternRepository, to=StarGridPatternRepository, scope=singleton)
        binder.bind(IMonthlyDirectionsRepository, to=MonthlyDirectionsRepository, scope=singleton)
        binder.bind(IMonthlyBoardDomainService, to=MonthlyBoardDomainService, scope=singleton)
        binder.bind(YearStarDomainService, to=YearStarDomainService, scope=singleton)
        binder.bind(FiveElementsFortuneService, to=FiveElementsFortuneService, scope=singleton)
        binder.bind(AdditionalDirectionMarksService, to=AdditionalDirectionMarksService, scope=singleton)
        binder.bind(FortuneStatusService, to=FortuneStatusService, scope=singleton)
        binder.bind(IStarAttributeRepository, to=StarAttributeRepository, scope=singleton)
        binder.bind(MonthlyDirectionsUseCase, to=MonthlyDirectionsUseCase, scope=singleton)

        # ── numerology ────────────────────────────────────
        binder.bind(INumerologyReadingRepository, to=NumerologyReadingRepository, scope=singleton)

        # ── powerstone ────────────────────────────────────
        binder.bind(IGogyoService, to=GogyoService, scope=singleton)
        binder.bind(IPowerStoneMatchingEngine, to=PowerStoneMatchingEngine, scope=singleton)
        binder.bind(IPowerStoneRepository, to=PowerStoneRepository, scope=singleton)
        binder.bind(IMessageCatalog, to=MessageCatalog, scope=singleton)
        binder.bind(PowerStoneRecommendationUseCase, to=PowerStoneRecommendationUseCase, scope=singleton)
        binder.bind(INumerologyPowerStoneRepository, to=NumerologyPowerStoneRepository, scope=singleton)
        binder.bind(NumerologyPowerStoneEngine, to=NumerologyPowerStoneEngine, scope=singleton)
        binder.bind(SixLayerPowerStoneUseCase, to=SixLayerPowerStoneUseCase, scope=singleton)

        # ── shared ────────────────────────────────────────
        binder.bind(IUserRepository, to=UserRepository, scope=singleton)
        binder.bind(IPermissionRepository, to=PermissionRepository, scope=singleton)
