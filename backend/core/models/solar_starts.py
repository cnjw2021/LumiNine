from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Date, Time
from core.database import db

class SolarStarts(db.Model):
    __tablename__ = 'solar_starts'

    year = Column(Integer, primary_key=True)
    solar_starts_date = Column(Date, nullable=False)
    solar_starts_time = Column(Time, nullable=False)
    zodiac = Column(String(10), nullable=False)
    star_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, year, solar_starts_date, solar_starts_time, zodiac, star_number):
        self.year = year
        self.solar_starts_date = solar_starts_date
        self.solar_starts_time = solar_starts_time
        self.zodiac = zodiac
        self.star_number = star_number

    @classmethod
    def get_by_year(cls, year):
        """指定した年の立春情報を取得する"""
        return cls.query.filter(cls.year == year).first()
