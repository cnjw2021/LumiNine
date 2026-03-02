from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.sql import func
import enum
from core.database import db

class CategoryEnum(enum.Enum):
    job = 'job'
    lucky_color = 'lucky_color'
    lucky_item = 'lucky_item'

class StarLifeGuidance(db.Model):
    """星と人生のガイダンス情報のエンティティクラス"""
    __tablename__ = 'star_life_guidance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    main_star = Column(Integer, nullable=False, comment='本命星')
    month_star = Column(Integer, nullable=False, comment='月命星')
    category = Column(Enum(CategoryEnum), nullable=False, comment='カテゴリ')
    content = Column(Text, nullable=False, comment='内容')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('main_star', 'month_star', 'category', name='idx_main_month_star_category'),
    )

    def __init__(self, main_star, month_star, category, content):
        self.main_star = main_star
        self.month_star = month_star
        self.category = category
        self.content = content

    def to_dict(self):
        """モデルを辞書に変換するメソッド（created_at, updated_at は除外）"""
        return {
            'id': self.id,
            'main_star': self.main_star,
            'month_star': self.month_star,
            'category': self.category.value if self.category else None,
            'content': self.content
        }

    def __repr__(self):
        return f"<StarLifeGuidance(id={self.id}, main_star={self.main_star}, month_star={self.month_star}, category='{self.category.value if self.category else None}')>"
