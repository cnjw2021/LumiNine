from typing import List, Dict, Any
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import db
from core.utils.logger import get_logger
from core.models.daily_star_reading import DailyStarReading

logger = get_logger(__name__)
class DailyAstrology(db.Model):
    """日付ごとの干支と九星の情報を管理するモデル"""
    __tablename__ = 'daily_astrology'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, comment='日付')
    year = Column(Integer, nullable=False, comment='年')
    month = Column(Integer, nullable=False, comment='月')
    day = Column(Integer, nullable=False, comment='日')
    zodiac = Column(String(16), nullable=False, comment='干支')
    star_number = Column(Integer, nullable=False, comment='星盤')
    lunar_date = Column(String(6), nullable=False, comment='旧暦')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), comment='作成日時')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), 
                       onupdate=func.current_timestamp(), comment='更新日時')
    
    # 日命星読みとのリレーションシップ
    day_star_reading = relationship('DailyStarReading', 
                                    primaryjoin='DailyAstrology.star_number == DailyStarReading.star_number',
                                    foreign_keys='DailyStarReading.star_number',
                                    uselist=False,
                                    viewonly=True)

    def __init__(self, date: Date, zodiac: str, star_number: int, lunar_date: str):
        """初期化
        
        Args:
            date: 日付
            zodiac: 干支
            star_number: 星盤
        """
        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.zodiac = zodiac
        self.star_number = star_number
        self.lunar_date = lunar_date

    def __repr__(self):
        return f"<DailyAstrology(date={self.date}, zodiac={self.zodiac}, star_number={self.star_number}, lunar_date={self.lunar_date})>"

    @classmethod
    def find_day_astro_info(cls, target_date: Date):
        """指定された日付の日命星を取得
        
        Args:
            target_date: 検索する日付
            
        Returns:
            DailyAstrology: 該当するデータ。存在しない場合はNone
        """
        return cls.query.filter_by(date=target_date.date()).first()

    @classmethod
    def get_by_year_month(cls, year: int, month: int) -> List['DailyAstrology']:
        """指定された年月のデータを取得
        
        Args:
            year: 年
            month: 月
            
        Returns:
            List[DailyAstrology]: 該当するデータのリスト
        """
        return cls.query.filter_by(year=year, month=month).all()

    @classmethod
    def get_by_zodiac(cls, zodiac: str) -> List['DailyAstrology']:
        """指定された干支のデータを取得
        
        Args:
            zodiac: 干支
            
        Returns:
            List[DailyAstrology]: 該当するデータのリスト
        """
        return cls.query.filter_by(zodiac=zodiac).all()

    @classmethod
    def get_by_star_number(cls, star_number: int) -> List['DailyAstrology']:
        """指定された星盤のデータを取得
        
        Args:
            star_number: 星盤
            
        Returns:
            List[DailyAstrology]: 該当するデータのリスト
        """
        return cls.query.filter_by(star_number=star_number).all()
    
    def get_day_star_reading(self):
        """この日の日命星読みを取得します
        
        Returns:
            DailyStarReading: 日命星読みデータ。存在しない場合はNone
        """
        if hasattr(self, 'day_star_reading') and self.day_star_reading:
            return self.day_star_reading
        
        # リレーションシップで取得できない場合は直接クエリを実行
        return DailyStarReading.get_by_star(self.star_number)

    def to_dict(self) -> Dict[str, Any]:
        """モデルを辞書形式に変換（created_at, updated_at は除外）

        Returns:
            Dict[str, Any]: モデルのデータ
        """
        result = {
            'id': self.id,
            'date': self.date.isoformat(),
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'zodiac': self.zodiac,
            'star_number': self.star_number,
            'lunar_date': self.lunar_date
        }
        
        # 日命星読みが存在する場合は追加
        day_star_reading = self.get_day_star_reading()
        if day_star_reading:
            result['day_star_reading'] = day_star_reading.to_dict()
            
        return result 