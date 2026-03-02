from datetime import datetime, timedelta
from typing import Dict, Any
from injector import inject

from apps.ninestarki.services.year_fortune_service import YearFortuneService
from apps.ninestarki.services.month_fortune_service import MonthFortuneService
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.domain.services.annual_directions_domain_service import AnnualDirectionsDomainService
from apps.ninestarki.services.year_fortune_service import YearFortuneService
from apps.ninestarki.domain.repositories.annual_directions_repository_interface import IAnnualDirectionsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from core.utils.logger import get_logger
from apps.ninestarki.domain.services.year_star_domain_service import YearStarDomainService
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from core.exceptions import ValidationError, DomainRuleViolation, ExternalServiceError
from apps.ninestarki.use_cases.dto.fortune_dtos import AnnualDirectionsResponseDTO, MonthAcquiredFortuneResponseDTO

logger = get_logger(__name__)

class GetFortuneDataUseCase:
    """
    年運、月運、方位運など、様々な運気データを取得する責任を持ちます。
    """
    @inject
    def __init__(self, nine_star_repo: INineStarRepository, annual_repo: IAnnualDirectionsRepository, solar_terms_repo: ISolarTermsRepository, month_fortune_service: IMonthFortuneService, annual_domain: AnnualDirectionsDomainService, solar_starts_repo: ISolarStartsRepository, year_fortune_service: YearFortuneService, star_grid_repo: IStarGridPatternRepository, direction_marks_service: DirectionMarksDomainService):
        """
        UseCaseが使用するリポジトリとサービスを初期化し、Domainサービスに依存性を注入します.
        """
        self.nine_star_repo = nine_star_repo
        self.annual_repo = annual_repo
        self.solar_terms_repo = solar_terms_repo
        self.month_fortune_service = month_fortune_service
        self.annual_domain = annual_domain
        self.year_fortune_service = year_fortune_service
        self.star_grid_repo = star_grid_repo
        self.direction_marks_service = direction_marks_service
        self.year_star_service = YearStarDomainService(
            nine_star_repo=self.nine_star_repo,
            solar_terms_repo=solar_terms_repo,
            solar_starts_repo=solar_starts_repo,
            star_grid_repo=star_grid_repo,
        )


    def get_direction_fortune(self, main_star: int, month_star: int, target_year: int) -> Dict[str, Any]:
        """九星盤における方位の吉凶判定を取得します。"""
        logger.debug(f"get_direction_fortune を実行: {target_year}")
        if not (1 <= int(main_star) <= 9) or not (1 <= int(month_star) <= 9):
            raise ValidationError("Stars must be in 1..9", fields=["main_star", "month_star"])
        # 年星・干支はポート経由で算出
        year_info = self.year_star_service.get_year_star_info(target_year)
        if not year_info or not year_info.get('star_number') or not year_info.get('zodiac'):
            raise DomainRuleViolation(f"中宮情報（年星/干支）の取得に失敗しました: {target_year}")
        ctx = self.direction_marks_service.get_direction_fortune_with_context(
            main_star=main_star,
            month_star=month_star,
            target_year=target_year,
            year_star_number=year_info['star_number'],
            zodiac=year_info['zodiac'],
        )
        if not ctx:
            raise DomainRuleViolation(f"方位の吉凶情報の取得に失敗しました: {target_year}")
        return ctx

    def get_year_star_info(self, target_year: int) -> Dict[str, Any]:
        """指定された年の中宮情報を取得します。"""
        logger.debug(f"get_year_star_info を実行: {target_year}")
        result = self.year_star_service.get_year_star_info(target_year)
        if not result:
            raise DomainRuleViolation(f"中宮情報の取得に失敗しました: {target_year}")
        return result

    def get_annual_directions(self, main_star: int, month_star: int, target_year: int) -> AnnualDirectionsResponseDTO:
        """1年分の吉方位情報を取得します。"""
        logger.debug(f"get_annual_directions を実行: {target_year}")
        if not (1 <= int(main_star) <= 9) or not (1 <= int(month_star) <= 9):
            raise ValidationError("Stars must be in 1..9", fields=["main_star", "month_star"])
        return self.annual_domain.compute(main_star, month_star, target_year)

    def get_year_acquired_fortune(self, main_star: int, month_star: int, target_year: int) -> dict:
        """指定年を含む3年分の運気情報を取得します。"""
        logger.info("Executing get_year_acquired_fortune")
        return self.year_fortune_service.get_year_fortune(
            main_star=main_star,
            month_star=month_star,
            target_year=target_year
        )

    def get_month_acquired_fortune(self, main_star: int, month_star: int, target_year: int) -> MonthAcquiredFortuneResponseDTO:
        """月の運気情報を取得します。"""
        logger.info("Executing get_month_acquired_fortune")
        if not (1 <= int(main_star) <= 9) or not (1 <= int(month_star) <= 9):
            raise ValidationError("Stars must be in 1..9", fields=["main_star", "month_star"])
        try:
            month_fortune_data = self.month_fortune_service.get_month_fortune(
                main_star=main_star,
                month_star=month_star,
                target_year=target_year,
            )
        except Exception as e:
            raise ExternalServiceError("Failed to fetch month fortune", details=str(e)) from e
        return {
            'month_star': month_star,
            'target_year': target_year,
            'annual_directions': month_fortune_data.get('directions', {})
        }