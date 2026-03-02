"""MonthFortuneService - 月の運気データを取得するサービス"""

from datetime import timedelta
from core.utils.logger import get_logger
from injector import inject
from apps.ninestarki.domain.repositories.solar_terms_repository_interface import ISolarTermsRepository
from apps.ninestarki.domain.repositories.solar_starts_repository_interface import ISolarStartsRepository
from apps.ninestarki.domain.services.interfaces.month_fortune_service_interface import IMonthFortuneService
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from core.models.main_star_acquired_fortune_message import MainStarAcquiredFortuneMessage
from core.models.month_star_acquired_fortune_message import MonthStarAcquiredFortuneMessage
from core.models.star_groups import StarGroups

logger = get_logger(__name__)

class MonthFortuneService(IMonthFortuneService):
    """月の運気データを取り扱うサービスクラス
    """
    @inject
    def __init__(self, solar_terms_repo: ISolarTermsRepository, solar_starts_repo: ISolarStartsRepository, star_grid_repo: IStarGridPatternRepository, monthly_repo: IMonthlyDirectionsRepository) -> None:
        self.solar_terms_repo = solar_terms_repo
        self.solar_starts_repo = solar_starts_repo
        self.star_grid_repo = star_grid_repo
        self.monthly_repo = monthly_repo

    def get_month_fortune_for_report(self, main_star, month_star, target_year):
        """レポート生成用の月の運気データを取得するファサードメソッド
        
        Args:
            main_star (int): 本命星番号（1-9）
            month_star (int): 月命星番号（1-9）
            target_year (int): 対象年
            
        Returns:
            dict: 年の運気情報（3年分）
        """
        logger.debug(f"Getting month fortune for report: main_star={main_star}, month_star={month_star}, target_year={target_year}")
        
        try:
            # 内部の実装メソッドを呼び出す
            month_fortune_data = self._get_month_fortune(main_star, month_star, target_year)
            
            # レポート表示用にデータ構造を変換
            result = {
                "directions": {}
            }
            
            # 'directions'キー内のデータを取得
            annual_directions = month_fortune_data.get('directions', {})
            
            # 各月のデータを変換
            for month_key, month_data in annual_directions.items():
                # month_key は "month_1", "month_2" のような形式
                month_num = month_key.split('_')[1]
                
                # 干支を取得
                zodiac = month_data.get('zodiac', '')
                
                # 期間の整形（YYYY-MM-DD形式からYYYY年MM月DD日形式へ）
                period_start = None
                period_end = None
                from datetime import datetime
                if 'period_start' in month_data and 'period_end' in month_data:
                    start_date = datetime.strptime(month_data['period_start'], '%Y-%m-%d')
                    end_date = datetime.strptime(month_data['period_end'], '%Y-%m-%d')
                    
                    # 期間表示の整形（画面と同様の形式に）
                    period_start = start_date.strftime('%Y年%m月%d日')
                    period_end = end_date.strftime('%Y年%m月%d日')
                    
                    # 簡略表示（月日のみ）も追加
                    period_start_short = start_date.strftime('%-m/%-d')
                    period_end_short = end_date.strftime('%-m/%-d')
                
                # 年月の表示用データを作成（画面と同様の表示に）
                display_year = month_data.get('year', target_year)
                month = int(month_num)
                display_month = f"{display_year}年{month}月"
                
                # 月と干支を組み合わせた表示（画面表示に合わせる）
                display_title = f"{display_year}年{month}月 {zodiac}"
                
                # 期間の表示（M/D ~ M/D）形式
                display_period = f"({period_start_short} ~ {period_end_short})"
                
                # 方位データの整形
                directions = {}
                for direction, direction_data in month_data.get('directions', {}).items():
                    directions[direction] = {
                        "title": direction_data.get('title'),
                        "details": direction_data.get('details'),
                        "is_main_star": direction_data.get('is_main_star', False),
                        "is_auspicious": direction_data.get('is_auspicious', False)
                    }
                
                # 月ごとのデータを格納
                result["directions"][month_num] = {
                    "star_number": month_data.get('center_star'),
                    "zodiac": zodiac,
                    "display_title": display_title,  # 画面表示用タイトル
                    "display_period": display_period,  # 画面表示用期間
                    "period_start": period_start,
                    "period_end": period_end,
                    "directions": directions
                }
            
            logger.debug(f"Month fortune data for report converted successfully")
            return result
        except Exception as e:
            logger.error(f"Error retrieving month fortune data for report: {str(e)}")
            # エラー時は空の辞書を返す（データがない状態）
            return {"directions": {}}
    
    def get_month_fortune(self, main_star, month_star, target_year):
        """APIエンドポイント用の月の運気データを取得するファサードメソッド
        
        Args:
            main_star (int): 本命星番号（1-9）
            month_star (int): 月命星番号（1-9）
            target_year (int): 対象年
            
        Returns:
            dict: 月の運気情報（12ヶ月分）
        """
        logger.debug(f"Getting month fortune for API: main_star={main_star}, month_star={month_star}, target_year={target_year}")
        
        try:
            # 内部の実装メソッドを呼び出す
            return self._get_month_fortune(main_star, month_star, target_year)
        except Exception as e:
            logger.error(f"Error retrieving month fortune data for API: {str(e)}")
            raise
    
    def _get_month_fortune(self, main_star, month_star, target_year):
        """
        月の運気情報を取得する
        
        クエリパラメータ:
            main_star: 本命星の番号（1-9）
            month_star: 月命星の番号（1-9）
            target_year: 鑑定年（デフォルトは現在の年）
        
        戻り値:
            12ヶ月分の時の運気情報
        """

        # 干支の取得
        zodiac = self.solar_starts_repo.get_by_year(target_year).zodiac

        # 現在の干支と年星のデータを準備
        base_params = {
            'main_star': main_star,
            'zodiac': zodiac
        }
        
        # 各月の盤面を取得（入春の星からグループを求めて取得）
        spring_term = self.solar_terms_repo.get_spring_start(target_year)
        if not spring_term:
            raise ValueError(f"入春データが存在しません: {target_year}")
        group_id = StarGroups.get_group_for_star(spring_term.star_number)
        if not group_id:
            raise ValueError(f"グループが判定できません: star={spring_term.star_number}")
        monthly_directions = self.monthly_repo.list_by_group(group_id)
        
        # 当年と翌年の節入り情報を取得
        current_year_terms = {term.month: term for term in self.solar_terms_repo.get_yearly_terms(target_year)}
        next_year_terms = {term.month: term for term in self.solar_terms_repo.get_yearly_terms(target_year + 1)}
    
    # 12ヶ月分の吉方位情報を格納する配列
        annual_directions = {}

        # 各月の吉方位情報を取得（2月〜翌年1月）
        for monthly_direction in monthly_directions:
            if not monthly_direction:
                annual_directions[f"month_{monthly_direction.month}"] = {
                    'error': f'月盤データが見つかりません: {month_star}-{monthly_direction.month}'
                }
                continue
            
            # 盤面の情報を取得
            grid_pattern = self.star_grid_repo.get_by_center_star(monthly_direction.center_star)
            
            if not grid_pattern:
                annual_directions[f"month_{monthly_direction.month}"] = {
                    'error': f'九星盤データが見つかりません: {monthly_direction.center_star}'
                }
                continue
                
            # 吉凶判定を行う
            fortune_status = grid_pattern.get_time_fortune_status(base_params)
            
            # 本命星の方位に対して、後天定位の鑑定メッセージを取得
            for direction, result in fortune_status.items():
                if result["is_main_star"]:
                    # 方位自体を使って後天定位の星番号を取得する
                    # 例：「北」方位なら、常に一白水星
                    acquired_fortune_star_number = {
                        'center': 5,  # 中央星
                        'north': 1,  # 一白水星
                        'northeast': 8,  # 八白土星
                        'east': 3,  # 三碧木星
                        'southeast': 4,  # 四緑木星
                        'south': 9,  # 九紫火星
                        'southwest': 2,  # 二黒土星
                        'west': 7,  # 七赤金星
                        'northwest': 6  # 六白金星
                    }.get(direction)
                    
                    # 後天定位の星番号でメッセージを取得
                    fortune_message = MonthStarAcquiredFortuneMessage.get_by_star_number(acquired_fortune_star_number)
                    if fortune_message:
                        if result["is_auspicious"]:
                            # 吉運メッセージを取得
                            result["title"] = fortune_message.luck_title
                            result["details"] = fortune_message.luck_details
                        else:
                            # 凶運メッセージを取得
                            result["title"] = fortune_message.unluck_title
                            result["details"] = fortune_message.unluck_details

            # 期間情報を取得
            period_info = None
            month = monthly_direction.month
            
            # 表示する年を決定（1月は翌年）
            year_for_display = target_year + 1 if month == 1 else target_year
            
            # 現在月の節入り日を取得
            current_term = None
            if month == 1:
                # 1月は翌年のデータ
                current_term = next_year_terms.get(month)
            else:
                current_term = current_year_terms.get(month)
            
            # 次の月の節入り日を取得して期間を計算
            if current_term:
                next_month = month + 1
                next_year = target_year
                
                # 年をまたぐ場合（12月→1月、1月→2月）
                if month == 12:
                    next_month = 1
                    next_year = target_year + 1
                elif month == 1:
                    next_month = 2
                    next_year = target_year + 1
                
                # 次の月の節入り日を取得
                next_term = None
                if next_year == target_year:
                    next_term = current_year_terms.get(next_month)
                elif next_year == target_year + 1:
                    next_term = next_year_terms.get(next_month)
                
                if next_term:
                    from datetime import timedelta
                    start_date = current_term.solar_terms_date
                    # 次の節入りの前日までが期間
                    end_date = next_term.solar_terms_date - timedelta(days=1)
                    
                    period_info = {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    }
            
            # 月ごとの吉凶方位を追加
            month_key = f"month_{monthly_direction.month}"
            annual_directions[month_key] = {
                'year': year_for_display,
                'month': monthly_direction.month,
                'display_month': f"{year_for_display}年{monthly_direction.month}月",
                'zodiac': current_term.zodiac if current_term else None,
                'center_star': monthly_direction.center_star,
                'directions': fortune_status
            }
            
            # 期間情報を追加
            if period_info:
                annual_directions[month_key]['period_start'] = period_info['start_date']
                annual_directions[month_key]['period_end'] = period_info['end_date']
        
        logger.debug(f"Month fortune data successfully generated")
        # 結果を適切な構造で返す
        result = {
            'directions': annual_directions
        }
        return result 