from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from core.database import db


class StarAttribute(db.Model):
    """
    'star_attributes' テーブルのデータ構造を定義するエンティティクラス。
    九星ごとの詳細属性（色、食べ物、身体部位、場所など）を管理します。
    """
    __tablename__ = 'star_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    star_number = Column(Integer, nullable=False)
    attribute_type = Column(String(30), nullable=False)
    attribute_value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """エンティティオブジェクトを辞書形式に変換します。"""
        return {
            'id': self.id,
            'star_number': self.star_number,
            'attribute_type': self.attribute_type,
            'attribute_value': self.attribute_value,
            'description': self.description,
        }
