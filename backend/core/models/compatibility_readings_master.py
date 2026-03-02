from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, UniqueConstraint
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CompatibilityReadingsMaster(db.Model):
    """相性鑑定文マスターモデル"""
    __tablename__ = 'compatibility_readings_master'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pattern_code = Column(String(30), ForeignKey('compatibility_symbol_pattern_master.pattern_code'), 
                         nullable=False, comment='パターンコード')
    theme = Column(String(30), nullable=False, comment='テーマ')
    title = Column(String(100), nullable=False, comment='鑑定タイトル')
    content = Column(Text, nullable=False, comment='鑑定内容')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('pattern_code', 'theme', name='unique_reading'),
        Index('idx_pattern_code', 'pattern_code'),
    )

    def __init__(self, pattern_code, theme, title, content):
        self.pattern_code = pattern_code
        self.theme = theme
        self.title = title
        self.content = content

    def to_dict(self):
        return {
            'id': self.id,
            'pattern_code': self.pattern_code,
            'theme': self.theme,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 