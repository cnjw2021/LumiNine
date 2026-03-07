import os
from injector import Module, provider, singleton
from sqlalchemy.orm import Session
from core.database import db

# 必要なすべてのインターフェースと実装をインポート
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.domain.repositories.user_repository_interface import IUserRepository
from apps.ninestarki.infrastructure.persistence.user_repository import UserRepository
from apps.ninestarki.domain.repositories.permission_repository_interface import IPermissionRepository
from apps.ninestarki.infrastructure.persistence.permission_repository import PermissionRepository

from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.infrastructure.persistence.solar_starts_repository import SolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.infrastructure.services.solar_calendar_provider import SolarCalendarProvider

from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.infrastructure.persistence.solar_terms_repository import SolarTermsRepository
from apps.ninestarki.use_cases.solar_admin_use_cases import ListSolarTermsUseCase, UpdateSolarTermUseCase

# Services / UseCases
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase

from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.infrastructure.persistence.star_grid_pattern_repository import StarGridPatternRepository
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.infrastructure.persistence.monthly_directions_repository import MonthlyDirectionsRepository
from apps.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardDomainService
from apps.ninestarki.domain.services.interfaces.monthly_board_service_interface import IMonthlyBoardDomainService
from apps.ninestarki.domain.services.year_star_domain_service import YearStarDomainService
from apps.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
from apps.ninestarki.domain.services.five_elements_fortune_service import FiveElementsFortuneService
from apps.ninestarki.domain.services.additional_direction_marks_service import AdditionalDirectionMarksService

# Phase 2: PowerStone Matching Engine
from apps.ninestarki.domain.services.interfaces.gogyo_service_interface import IGogyoService
from apps.ninestarki.domain.services.gogyo_service import GogyoService
from apps.ninestarki.domain.services.interfaces.powerstone_matching_engine_interface import IPowerStoneMatchingEngine
from apps.ninestarki.domain.services.powerstone_matching_engine import PowerStoneMatchingEngine
from apps.ninestarki.domain.repositories.powerstone_repository_interface import IPowerStoneRepository
from apps.ninestarki.infrastructure.persistence.powerstone_repository import PowerStoneRepository
from apps.ninestarki.use_cases.interfaces.message_catalog_interface import IMessageCatalog
from apps.ninestarki.infrastructure.services.message_catalog import MessageCatalog
from apps.ninestarki.use_cases.powerstone_recommendation_use_case import PowerStoneRecommendationUseCase

# Phase 5: Numerology
from apps.ninestarki.domain.repositories.numerology_reading_repository_interface import INumerologyReadingRepository
from apps.ninestarki.infrastructure.persistence.numerology_reading_repository import NumerologyReadingRepository

# Phase 5-3: Numerology PowerStone
from apps.ninestarki.domain.repositories.numerology_powerstone_repository_interface import INumerologyPowerStoneRepository
from apps.ninestarki.infrastructure.persistence.numerology_powerstone_repository import NumerologyPowerStoneRepository
from apps.ninestarki.domain.services.numerology_powerstone_engine import NumerologyPowerStoneEngine

# Phase 5-4: 6-Layer UseCase
from apps.ninestarki.use_cases.six_layer_powerstone_use_case import SixLayerPowerStoneUseCase

# Permission UseCase
from apps.ninestarki.use_cases.permission_use_case import PermissionUseCase

class AppModule(Module):
    """
    アプリケーションの依存性注入規則を定義するモジュール
    """
    @singleton
    @provider
    def provide_db_session(self) -> Session:
        # データベースセッションを提供する方法を定義
        return db.session

    @singleton
    @provider
    def provide_calculate_stars_use_case(self, repo: INineStarRepository, solar_terms_repo: ISolarTermsRepository, numerology_reading_repo: INumerologyReadingRepository) -> CalculateStarsUseCase:
        return CalculateStarsUseCase(repo, solar_terms_repo, numerology_reading_repo)

    @singleton
    @provider
    def provide_report_context_builder(self) -> ReportContextBuilder:
        return ReportContextBuilder()

    @singleton
    @provider
    def provide_generate_report_use_case(
        self,
        monthly_directions_use_case: MonthlyDirectionsUseCase,
        calculate_stars_use_case: CalculateStarsUseCase,
        solar_starts_repo: ISolarStartsRepository,
        solar_terms_repo: ISolarTermsRepository,
        solar_calendar_provider: ISolarCalendarProvider,
        report_context_builder: ReportContextBuilder,
    ) -> GenerateReportUseCase:
        return GenerateReportUseCase(
            monthly_directions_use_case=monthly_directions_use_case,
            calculate_stars_use_case=calculate_stars_use_case,
            solar_starts_repo=solar_starts_repo,
            solar_terms_repo=solar_terms_repo,
            solar_calendar_provider=solar_calendar_provider,
            report_context_builder=report_context_builder,
        )

    @singleton
    @provider
    def provide_permission_use_case(self, user_repo: IUserRepository, perm_repo: IPermissionRepository) -> PermissionUseCase:
        return PermissionUseCase(user_repo, perm_repo)

    def configure(self, binder):
        # インターフェース(抽象)と実装(具体的)をバインディング
        binder.bind(INineStarRepository, to=NineStarRepository, scope=singleton)
        binder.bind(IUserRepository, to=UserRepository, scope=singleton)
        binder.bind(IPermissionRepository, to=PermissionRepository, scope=singleton)
        binder.bind(ISolarStartsRepository, to=SolarStartsRepository, scope=singleton)
        binder.bind(ISolarCalendarProvider, to=SolarCalendarProvider, scope=singleton)
        # ドメインサービス用アダプタのバインド
        binder.bind(ISolarTermsRepository, to=SolarTermsRepository, scope=singleton)
        binder.bind(IStarGridPatternRepository, to=StarGridPatternRepository, scope=singleton)
        binder.bind(IMonthlyDirectionsRepository, to=MonthlyDirectionsRepository, scope=singleton)
        binder.bind(ListSolarTermsUseCase, to=ListSolarTermsUseCase, scope=singleton)
        binder.bind(UpdateSolarTermUseCase, to=UpdateSolarTermUseCase, scope=singleton)
        binder.bind(IMonthlyBoardDomainService, to=MonthlyBoardDomainService, scope=singleton)
        binder.bind(YearStarDomainService, to=YearStarDomainService, scope=singleton)
        binder.bind(FiveElementsFortuneService, to=FiveElementsFortuneService, scope=singleton)
        binder.bind(AdditionalDirectionMarksService, to=AdditionalDirectionMarksService, scope=singleton)
        binder.bind(MonthlyDirectionsUseCase, to=MonthlyDirectionsUseCase, scope=singleton)

        # Phase 2: PowerStone Matching Engine DI バインディング
        binder.bind(IGogyoService, to=GogyoService, scope=singleton)
        binder.bind(IPowerStoneMatchingEngine, to=PowerStoneMatchingEngine, scope=singleton)
        binder.bind(IPowerStoneRepository, to=PowerStoneRepository, scope=singleton)
        binder.bind(IMessageCatalog, to=MessageCatalog, scope=singleton)
        binder.bind(PowerStoneRecommendationUseCase, to=PowerStoneRecommendationUseCase, scope=singleton)

        # Phase 5: Numerology DI バインディング
        binder.bind(INumerologyReadingRepository, to=NumerologyReadingRepository, scope=singleton)

        # Phase 5-3: Numerology PowerStone DI バインディング
        binder.bind(INumerologyPowerStoneRepository, to=NumerologyPowerStoneRepository, scope=singleton)
        binder.bind(NumerologyPowerStoneEngine, to=NumerologyPowerStoneEngine, scope=singleton)

        # Phase 5-4: 6-Layer UseCase DI バインディング
        binder.bind(SixLayerPowerStoneUseCase, to=SixLayerPowerStoneUseCase, scope=singleton)