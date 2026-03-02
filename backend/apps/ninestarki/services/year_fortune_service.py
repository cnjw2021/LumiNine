"""YearFortuneService - 年の運気データを取得するサービス"""

from datetime import timedelta, datetime, date
from core.utils.logger import get_logger
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
from core.models.main_star_acquired_fortune_message import MainStarAcquiredFortuneMessage

logger = get_logger(__name__)

class YearFortuneService:
    """年の運気データを取り扱うサービスクラス"""
    def __init__(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository) -> None:
        self.solar_terms_repo = solar_terms_repo
        self.solar_starts_repo = solar_starts_repo
        self.star_grid_repo = star_grid_repo

    def get_year_fortune_for_report(self, main_star, month_star, target_year):
        """レポート生成用の年の運気データを取得するファサードメソッド
        
        Args:
            main_star (int): 本命星番号（1-9）
            month_star (int): 月命星番号（1-9）
            target_year (int): 対象年
            
        Returns:
            dict: 年の運気情報（3年分）
        """
        logger.debug(f"Getting year fortune for report: main_star={main_star}, month_star={month_star}, target_year={target_year}")
        
        try:
            # 内部の実装メソッドを呼び出す
            result = self._get_year_fortune(main_star, month_star, target_year)
            logger.debug(f"Year fortune data for report retrieved successfully")
            return result
        except Exception as e:
            logger.error(f"Error retrieving year fortune data for report: {str(e)}")
            # エラー時は空の辞書を返す（データがない状態）
            return {"directions": {}}
    
    def get_year_fortune(self, main_star, month_star, target_year):
        """APIエンドポイント用の年の運気データを取得するファサードメソッド
        
        Args:
            main_star (int): 本命星番号（1-9）
            month_star (int): 月命星番号（1-9）
            target_year (int): 対象年
            
        Returns:
            dict: 年の運気情報（3年分）
        """
        logger.debug(f"Getting year fortune for API: main_star={main_star}, month_star={month_star}, target_year={target_year}")
        
        try:
            # 内部の実装メソッドを呼び出す
            return self._get_year_fortune(main_star, month_star, target_year)
        except Exception as e:
            logger.error(f"Error retrieving year fortune data for API: {str(e)}")
            raise
    
    @staticmethod
    def _find_direction_star(star_number, grid_pattern):
        """
        特定の九星盤における本命星の方位を判定する
        
        Args:
            star_number (int): 検索対象の星番号（本命星）
            grid_pattern: 九星盤パターン
            
        Returns:
            str: 方位（north, south, east, west, northeast, northwest, southeast, southwest, center）
                 対象の星が見つからない場合はNone
        """
        try:
            logger.debug(f"Finding direction for star {star_number} in grid pattern with center {grid_pattern.center_star}")
            
            # 星番号と方位のマッピング
            direction_mapping = {
                grid_pattern.center_star: 'center',
                grid_pattern.north: 'north',
                grid_pattern.northeast: 'northeast',
                grid_pattern.east: 'east',
                grid_pattern.southeast: 'southeast',
                grid_pattern.south: 'south',
                grid_pattern.southwest: 'southwest',
                grid_pattern.west: 'west',
                grid_pattern.northwest: 'northwest'
            }
            
            # 与えられた星番号がどの方位にあるか検索
            direction = direction_mapping.get(star_number)
            logger.debug(f"Star {star_number} found in direction: {direction}")
            return direction
            
        except Exception as e:
            logger.error(f"Error finding direction for star {star_number}: {str(e)}")
            return None
    
    def _get_year_fortune(self, main_star, month_star, target_year):
        """特定の星番号と年に関連する年の運気情報を取得する（内部実装）
        
        Args:
            main_star (int): 本命星番号（1-9）
            month_star (int): 月命星番号（1-9）
            target_year (int): 対象年
            
        Returns:
            dict: 年の運気情報（3年分）
        """
        logger.debug(f"Internal method: Getting year fortune data for main_star={main_star}, month_star={month_star}, target_year={target_year}")
        
        # 3年分の吉方位情報を格納する配列
        directions = {}
        
        # 基準年を設定
        original_year = target_year
        
        # 3年分の吉方位情報を取得
        for year in [original_year, original_year + 1, original_year + 2]:
            # 入春基準のデータ取得（中心星/干支はSolarStarts、期間はSolarTerms）
            starts_row = self.solar_starts_repo.get_by_year(year)
            spring_term = self.solar_terms_repo.get_spring_start(year)
            if not starts_row or not spring_term:
                continue
            grid_pattern = self.star_grid_repo.get_by_center_star(starts_row.star_number)
            if not grid_pattern:
                directions[f"year_{year}"] = {
                    'error': f'九星盤データが見つかりません: {starts_row.star_number}'
                }
                continue
            
            # 期間の計算（入春〜翌年入春前日）: SolarStartsのdateを使用（元ロジック準拠）
            current_spring_start = starts_row.solar_starts_date
            next_year_starts = self.solar_starts_repo.get_by_year(year + 1) if year < 2100 else None
            next_year_spring_start = next_year_starts.solar_starts_date if next_year_starts else None
            period_start = current_spring_start.strftime('%Y-%m-%d') if current_spring_start else None
            period_end = (next_year_spring_start - timedelta(days=1)).strftime('%Y-%m-%d') if next_year_spring_start else None
            
            # 吉凶判定を行う
            base_params = {
                'main_star': main_star,
                'zodiac': starts_row.zodiac
            }
            fortune_status = grid_pattern.get_time_fortune_status(base_params)
            
            # 本命星の方位を特定
            user_star_direction = YearFortuneService._find_direction_star(main_star, grid_pattern)
            # 後天定位の固定盤（center=5）をDBから取得してマッピング
            fixed_grid = self.star_grid_repo.get_by_center_star(5)
            for direction, result in fortune_status.items():
                if not result.get("is_main_star"):
                    continue
                if not fixed_grid:
                    continue
                # 方向→固定星番号を固定盤から取得
                if direction == 'center':
                    acquired_fortune_star_number = fixed_grid.center_star
                elif direction == 'north':
                    acquired_fortune_star_number = fixed_grid.north
                elif direction == 'northeast':
                    acquired_fortune_star_number = fixed_grid.northeast
                elif direction == 'east':
                    acquired_fortune_star_number = fixed_grid.east
                elif direction == 'southeast':
                    acquired_fortune_star_number = fixed_grid.southeast
                elif direction == 'south':
                    acquired_fortune_star_number = fixed_grid.south
                elif direction == 'southwest':
                    acquired_fortune_star_number = fixed_grid.southwest
                elif direction == 'west':
                    acquired_fortune_star_number = fixed_grid.west
                elif direction == 'northwest':
                    acquired_fortune_star_number = fixed_grid.northwest
                else:
                    acquired_fortune_star_number = None

                if acquired_fortune_star_number is None:
                    continue
                fortune_message = MainStarAcquiredFortuneMessage.get_by_star_number(acquired_fortune_star_number)
                if not fortune_message:
                    continue
                if result.get("is_auspicious"):
                    result["title"] = fortune_message.luck_title
                    result["details"] = fortune_message.luck_details
                else:
                    result["title"] = fortune_message.unluck_title
                    result["details"] = fortune_message.unluck_details
            
            directions[f"year_{year}"] = {
                'year': year,
                'star_number': starts_row.star_number,
                'zodiac': starts_row.zodiac,
                'directions': fortune_status,
                'period_start': period_start,
                'period_end': period_end,
                'user_star_direction': user_star_direction
            }
        
        # 結果を返す
        result = {
            'target_year': target_year,
            'directions': directions
        }
        
        logger.debug(f"Year fortune data successfully generated")
        return result 
    