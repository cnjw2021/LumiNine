from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CompatibilitySymbolPatternMaster(db.Model):
    __tablename__ = 'compatibility_symbol_pattern_master'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    symbols = Column(String(10), nullable=False, unique=True, comment='相性記号 (★,○,P,F,N,▲ など)')
    pattern_code = Column(String(30), nullable=False, unique=True, comment='パターンコード')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, symbols, pattern_code):
        self.symbols = symbols
        self.pattern_code = pattern_code

    def to_dict(self):
        return {
            'id': self.id,
            'symbols': self.symbols,
            'pattern_code': self.pattern_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 