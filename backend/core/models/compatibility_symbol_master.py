from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CompatibilitySymbolMaster(db.Model):
    __tablename__ = 'compatibility_symbol_master'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    symbol = Column(String(10), nullable=False, unique=True, comment='相性記号 (★,○,P,F,N,▲,◆ など)')
    meaning = Column(String(50), nullable=False, comment='記号の意味（最高・良好・ビジネスなど）')
    description = Column(Text, comment='説明')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, symbol, meaning, description=None):
        self.symbol = symbol
        self.meaning = meaning
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'meaning': self.meaning,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 