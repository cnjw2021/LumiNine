from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Unicode
from core.database import db

class NineStar(db.Model):
    """
    'stars' テーブルのデータ構造を定義するエンティティクラス。
    ビジネスロジックは含まれていません。
    """
    __tablename__ = 'stars'

    star_number = Column(Integer, primary_key=True, autoincrement=False) # IDではないのでautoincrement=False
    name_jp = Column(Unicode(50), nullable=False)
    name_en = Column(Unicode(50), nullable=False)
    element = Column(Unicode(20), nullable=False)
    keywords = Column(Unicode(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """
        エンティティオブジェクトをAPI応答に使用しやすい辞書形式に変換します。
        """
        return {
            'star_number': self.star_number,
            'name_jp': self.name_jp,
            'name_en': self.name_en,
            'element': self.element,
            'keywords': self.keywords,
            'description': self.description,
        }