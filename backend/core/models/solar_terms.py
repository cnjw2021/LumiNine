from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Date, Time
from core.database import db

class SolarTerms(db.Model):
    __tablename__ = 'solar_terms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    solar_terms_date = Column(Date, nullable=False)
    solar_terms_time = Column(Time, nullable=False)
    solar_terms_name = Column(String(20), nullable=False)
    zodiac = Column(String(10), nullable=False)
    star_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, year, month, solar_terms_date, solar_terms_time, solar_terms_name, zodiac, star_number):
        self.year = year
        self.month = month
        self.solar_terms_date = solar_terms_date
        self.solar_terms_time = solar_terms_time
        self.solar_terms_name = solar_terms_name
        self.zodiac = zodiac
        self.star_number = star_number
