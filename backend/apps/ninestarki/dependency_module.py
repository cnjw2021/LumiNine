import os
from injector import Module, provider, singleton
from sqlalchemy.orm import Session
from core.database import db

# 必要なすべてのインターフェースと実装をインポート
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from apps.ninestarki.use_cases.interfaces.pdf_generator_interface import PdfGeneratorInterface
from apps.ninestarki.infrastructure.pdf.weasyprint_pdf_generator import WeasyPrintPdfGenerator
from apps.ninestarki.domain.repositories.user_repository_interface import IUserRepository
from apps.ninestarki.infrastructure.persistence.user_repository import UserRepository
from apps.ninestarki.domain.repositories.permission_repository_interface import IPermissionRepository
from apps.ninestarki.infrastructure.persistence.permission_repository import PermissionRepository
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from apps.ninestarki.infrastructure.persistence.star_life_guidance_repository import StarLifeGuidanceRepository
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from apps.ninestarki.infrastructure.persistence.reading_query_repository import ReadingQueryRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.infrastructure.persistence.solar_starts_repository import SolarStartsRepository
from apps.ninestarki.domain.services.interfaces.solar_calendar_provider_interface import ISolarCalendarProvider
from apps.ninestarki.infrastructure.services.solar_calendar_provider import SolarCalendarProvider
from apps.ninestarki.domain.repositories.annual_directions_repository_interface import IAnnualDirectionsRepository
from apps.ninestarki.infrastructure.persistence.annual_directions_repository import AnnualDirectionsRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.infrastructure.persistence.solar_terms_repository import SolarTermsRepository
from apps.ninestarki.use_cases.solar_admin_use_cases import ListSolarTermsUseCase, UpdateSolarTermUseCase

# Services / UseCases
from apps.ninestarki.services.year_fortune_service import YearFortuneService
from apps.ninestarki.services.month_fortune_service import MonthFortuneService
from apps.ninestarki.services.star_attribute_service import StarAttributeService
from apps.ninestarki.domain.services.star_life_guidance_service import StarLifeGuidanceService
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.services.compatibility_service import CompatibilityService
from apps.ninestarki.use_cases.context.report_context_builder import ReportContextBuilder
from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.domain.services.direction_rule_engine import DirectionRuleEngine
from apps.ninestarki.use_cases.auspicious_dates_use_case import AuspiciousDatesUseCase
from apps.ninestarki.presentation.auspicious_dates_presenter import AuspiciousDatesPresenter
from apps.ninestarki.domain.services.interfaces.year_fortune_service_interface import IYearFortuneService
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from apps.ninestarki.domain.services.interfaces.star_attribute_service_interface import IStarAttributeService
from apps.ninestarki.domain.services.interfaces.auspicious_dates_service_interface import IAuspiciousDatesService
from apps.ninestarki.domain.services.auspicious_dates_domain_service import AuspiciousDatesDomainService
from apps.ninestarki.domain.services.interfaces.astrology_data_reader_interface import IAstrologyDataReader
from apps.ninestarki.domain.services.interfaces.compatibility_service_interface import ICompatibilityService
from apps.ninestarki.infrastructure.services.adapters.astrology_data_reader_adapter import AstrologyDataReaderAdapter
from apps.ninestarki.infrastructure.services.adapters.compatibility_service_adapter import CompatibilityServiceAdapter
from apps.ninestarki.domain.services.annual_directions_domain_service import AnnualDirectionsDomainService
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.infrastructure.persistence.star_grid_pattern_repository import StarGridPatternRepository
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.infrastructure.persistence.monthly_directions_repository import MonthlyDirectionsRepository

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
    def provide_pdf_generator(self) -> PdfGeneratorInterface:
        # backendディレクトリを基準にする（static/templatesは backend/apps/ninestarki 配下）
        base_dir = os.environ.get("APP_ROOT_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return WeasyPrintPdfGenerator(base_dir=base_dir)

    @singleton
    @provider
    def provide_year_fortune_service(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository) -> YearFortuneService:
        return YearFortuneService(solar_terms_repo, solar_starts_repo, star_grid_repo)

    @singleton
    @provider
    def provide_month_fortune_service(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository, monthly_repo: IMonthlyDirectionsRepository) -> IMonthFortuneService:
        return MonthFortuneService(solar_terms_repo, solar_starts_repo, star_grid_repo, monthly_repo)

    @singleton
    @provider
    def provide_star_attribute_service(self) -> StarAttributeService:
        return StarAttributeService()

    @singleton
    @provider
    def provide_star_life_guidance_service(self, repo: IStarLifeGuidanceRepository) -> StarLifeGuidanceService:
        return StarLifeGuidanceService(repo)

    @singleton
    @provider
    def provide_calculate_stars_use_case(self, repo: INineStarRepository, solar_terms_repo: ISolarTermsRepository) -> CalculateStarsUseCase:
        return CalculateStarsUseCase(repo, solar_terms_repo)

    @singleton
    @provider
    def provide_compatibility_service(self) -> CompatibilityService:
        return CompatibilityService()

    @singleton
    @provider
    def provide_report_context_builder(self) -> ReportContextBuilder:
        return ReportContextBuilder()

    @singleton
    @provider
    def provide_astrology_data_reader(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository) -> IAstrologyDataReader:
        # ポート経由で節気/立春情報を取得するため、両方のリポジトリを注入
        return AstrologyDataReaderAdapter(solar_terms_repo, solar_starts_repo)

    @singleton
    @provider
    def provide_compatibility_service_port(self) -> ICompatibilityService:
        return CompatibilityServiceAdapter()

    @singleton
    @provider
    def provide_auspicious_dates_use_case(self, service: IAuspiciousDatesService) -> AuspiciousDatesUseCase:
        return AuspiciousDatesUseCase(service)

    @singleton
    @provider
    def provide_auspicious_dates_presenter(self) -> AuspiciousDatesPresenter:
        return AuspiciousDatesPresenter()

    @singleton
    @provider
    def provide_generate_report_use_case(
        self,
        pdf_generator: PdfGeneratorInterface,
        auspicious_dates_service: IAuspiciousDatesService,
        auspicious_dates_presenter: AuspiciousDatesPresenter,
        year_fortune_service: YearFortuneService,
        month_fortune_service: IMonthFortuneService,
        star_attribute_service: StarAttributeService,
        star_life_guidance_service: StarLifeGuidanceService,
        calculate_stars_use_case: CalculateStarsUseCase,
        compatibility_service: CompatibilityService,
        reading_query_repo: IReadingQueryRepository,
        solar_starts_repo: ISolarStartsRepository,
        solar_terms_repo: ISolarTermsRepository,
        solar_calendar_provider: ISolarCalendarProvider,
        report_context_builder: ReportContextBuilder,
        direction_marks_service: DirectionMarksDomainService,
    ) -> GenerateReportUseCase:
        return GenerateReportUseCase(
            pdf_generator=pdf_generator,
            auspicious_dates_use_case=auspicious_dates_service,
            auspicious_dates_presenter=auspicious_dates_presenter,
            year_fortune_service=year_fortune_service,
            month_fortune_service=month_fortune_service,
            star_attribute_service=star_attribute_service,
            star_life_guidance_service=star_life_guidance_service,
            calculate_stars_use_case=calculate_stars_use_case,
            compatibility_service=compatibility_service,
            reading_query_repo=reading_query_repo,
            solar_starts_repo=solar_starts_repo,
            solar_terms_repo=solar_terms_repo,
            solar_calendar_provider=solar_calendar_provider,
            report_context_builder=report_context_builder,
            direction_marks_service=direction_marks_service,
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
        binder.bind(IStarLifeGuidanceRepository, to=StarLifeGuidanceRepository, scope=singleton)
        binder.bind(IReadingQueryRepository, to=ReadingQueryRepository, scope=singleton)
        binder.bind(ISolarStartsRepository, to=SolarStartsRepository, scope=singleton)
        binder.bind(ISolarCalendarProvider, to=SolarCalendarProvider, scope=singleton)
        binder.bind(IYearFortuneService, to=YearFortuneService, scope=singleton)
        binder.bind(IMonthFortuneService, to=MonthFortuneService, scope=singleton)
        binder.bind(IStarAttributeService, to=StarAttributeService, scope=singleton)
        # ドメインサービス用アダプタのバインド
        binder.bind(IAstrologyDataReader, to=AstrologyDataReaderAdapter, scope=singleton)
        binder.bind(ICompatibilityService, to=CompatibilityServiceAdapter, scope=singleton)
        binder.bind(IAuspiciousDatesService, to=AuspiciousDatesDomainService, scope=singleton)
        # Setter injection for AuspiciousDatesDomainService -> DirectionRuleEngine
        binder.bind(DirectionMarksDomainService, to=DirectionMarksDomainService, scope=singleton)
        binder.bind(DirectionRuleEngine, to=DirectionRuleEngine, scope=singleton)
        binder.bind(IAnnualDirectionsRepository, to=AnnualDirectionsRepository, scope=singleton)
        binder.bind(ISolarTermsRepository, to=SolarTermsRepository, scope=singleton)
        binder.bind(IStarGridPatternRepository, to=StarGridPatternRepository, scope=singleton)
        binder.bind(IMonthlyDirectionsRepository, to=MonthlyDirectionsRepository, scope=singleton)
        binder.bind(ListSolarTermsUseCase, to=ListSolarTermsUseCase, scope=singleton)
        binder.bind(UpdateSolarTermUseCase, to=UpdateSolarTermUseCase, scope=singleton)
        binder.bind(AnnualDirectionsDomainService, to=AnnualDirectionsDomainService, scope=singleton)