"""月命星読みデータを管理するモデル"""

from datetime import datetime
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class MonthlyStarReading(db.Model):
    """月命星読みのデータモデル
    各星の月命星としての特徴や性質を格納します
    """
    __tablename__ = 'monthly_star_readings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    star_number = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    title = db.Column(db.String(100), nullable=False, comment='見出し（例：社会的な顔）')
    keywords = db.Column(db.Text, nullable=True, comment='特徴を表すキーワード')
    description = db.Column(db.Text, nullable=False, comment='詳細な鑑定内容')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, star_number, title, description, keywords=None):
        self.star_number = star_number
        self.title = title
        self.description = description
        self.keywords = keywords
    
    def to_dict(self):
        """辞書形式に変換するメソッド"""
        return {
            'id': self.id,
            'star_number': self.star_number,
            'title': self.title,
            'keywords': self.keywords,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_star(cls, star_number):
        """特定の星の月命星読みを取得"""
        return cls.query.filter_by(star_number=star_number).first()
    
    @classmethod
    def get_all(cls):
        """全ての月命星読みを取得"""
        return cls.query.order_by(cls.star_number).all() 