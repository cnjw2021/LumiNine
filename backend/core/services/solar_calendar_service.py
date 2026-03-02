"""立春など太陽暦関連の計算を行うサービス"""

from datetime import datetime
from core.models.solar_starts import SolarStarts
from core.utils.logger import get_logger

logger = get_logger(__name__)

class SolarCalendarService:
    """太陽暦計算サービス
    立春の日付を考慮した年度計算などを提供します
    """
    
    @staticmethod
    def get_spring_beginning_datetime(year: int) -> datetime:
        """指定された年の立春日時を取得する
        
        Args:
            year (int): 計算対象の年
            
        Returns:
            datetime: 立春の日時
        """
        # 立春の日時を取得
        solar_start = SolarStarts.query.filter_by(year=year).first()
        
        if not solar_start:
            logger.warning(f"Solar start data not found for year {year}")
            # 立春データがない場合は、デフォルトとして2月4日を使用
            return datetime(year, 2, 4, 0, 0, 0)
        else:
            risshun_date = solar_start.solar_starts_date
            risshun_time = solar_start.solar_starts_time
            return datetime.combine(risshun_date, risshun_time)
    
    @classmethod
    def get_calculation_year(cls, birth_datetime: datetime) -> int:
        """立春を考慮して計算用の年を取得する
        立春前であれば前年として扱う
        
        Args:
            birth_datetime (datetime): 計算対象の日時
            
        Returns:
            int: 計算用の年
        """
        # 立春の日時を取得
        spring_beginning_datetime = cls.get_spring_beginning_datetime(birth_datetime.year)
        
        # 生年を決定（立春前か後かで変わる）
        calculation_year = birth_datetime.year
        if birth_datetime < spring_beginning_datetime:
            calculation_year -= 1
            logger.debug(f"Date {birth_datetime.date()} is before Spring Beginning, using previous year: {calculation_year}")
        
        return calculation_year 