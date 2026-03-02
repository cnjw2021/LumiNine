"""PDF用の方位運データ取得サービス"""

from datetime import datetime, date, timedelta
from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from core.models.star_grid_pattern import StarGridPattern
from core.models.solar_starts import SolarStarts
from flask_injector import inject
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from core.services.solar_calendar_service import SolarCalendarService
from core.utils.logger import get_logger

logger = get_logger(__name__)

class DirectionFortunePdfService:
    """PDFレポート用の方位運データを取得するサービス"""
    
    @inject
    @staticmethod
    def get_direction_fortune_with_metadata(main_star, month_star, target_year, solar_terms_repo: ISolarTermsRepository):
        """方位運データとメタデータ（年運星、干支、立春日など）を取得する
        
        Args:
            main_star (int): The main star number (1-9)
            month_star (int): The month star number (1-9)
            target_year (int): The target year for the fortune
            
        Returns:
            dict: Direction fortune data with metadata
        """
        try:
            logger.debug(f"Getting direction fortune with metadata for main_star={main_star}, month_star={month_star}, year={target_year}")
            
            # 現在の日付を取得
            current_date = datetime.now().date()
            
            # 指定された年の日付を作成（現在の月日を使用）
            target_date = date(target_year, current_date.month, current_date.day)
            target_datetime = datetime.combine(target_date, datetime.min.time())
            
            # 年運星（対象年の本命星）を計算（SolarTermsリポジトリ考慮）
            target_year_star_number = StarCalculatorService.calculate_main_star_number(target_datetime, solar_terms_repo)
                
            # 九星盤パターンを取得（対象年の年運星を中央の星として使用）
            pattern = StarGridPattern.get_by_center_star(target_year_star_number)
            if not pattern:
                logger.error(f"星番号 {target_year_star_number} の九星盤パターンが見つかりません")
                return None
            
            # 対象年の干支を計算（SolarTermsリポジトリ優先）
            spring_term = solar_terms_repo.get_spring_start(target_year)
            zodiac = spring_term.zodiac if spring_term else ""
            
            # パラメータの検証
            fortune_params = {
                'main_star': main_star,
                'month_star': month_star,
                'year_star': target_year_star_number,
                'zodiac': zodiac
            }

            # 方位の吉凶情報を取得
            try:
                # pattern.get_fortune_statusメソッドで方位の吉凶状態を取得
                result = pattern.get_fortune_status(fortune_params)
                
                # 結果に年度情報を追加
                result_with_info = {
                    'year': target_year,
                    'year_star': target_year_star_number,
                    'zodiac': zodiac,
                    'directions': result
                }
                
                # 立春日の情報を追加
                spring_term = solar_terms_repo.get_spring_start(target_year)
                if spring_term:
                    result_with_info['spring_start_date'] = spring_term.solar_terms_date.strftime('%Y-%m-%d')
                    
                    # 立春の期間（次の年の立春前日まで）を計算して追加
                    next_year_spring_term = solar_terms_repo.get_spring_start(target_year + 1)
                    if next_year_spring_term:
                        end_date = next_year_spring_term.solar_terms_date - timedelta(days=1)
                        result_with_info['spring_end_date'] = end_date.strftime('%Y-%m-%d')
                
                return result_with_info
            except ValueError as e:
                logger.error(f"Failed to get direction fortune status: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting direction fortune data: {str(e)}")
            return None
