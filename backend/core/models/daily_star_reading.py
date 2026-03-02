"""日命星読みデータを管理するモデル"""

from datetime import datetime
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class DailyStarReading(db.Model):
    """日命星読みのデータモデル
    各星の日命星としての特徴や性質を格納します
    """
    __tablename__ = 'daily_star_readings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    star_number = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    title = db.Column(db.String(100), nullable=False, comment='見出し（例：内面的な性質）')
    keywords = db.Column(db.Text, nullable=True, comment='特徴を表すキーワード')
    description = db.Column(db.Text, nullable=False, comment='詳細な鑑定内容')
    advice = db.Column(db.Text, nullable=True, comment='アドバイス')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, star_number, title, description, keywords=None, advice=None):
        self.star_number = star_number
        self.title = title
        self.description = description
        self.keywords = keywords
        self.advice = advice
    
    def to_dict(self):
        """辞書形式に変換するメソッド（created_at, updated_at は除外）"""
        return {
            'id': self.id,
            'star_number': self.star_number,
            'title': self.title,
            'keywords': self.keywords,
            'description': self.description,
            'advice': self.advice
        }
    
    @classmethod
    def get_by_star(cls, star_number):
        """特定の星の日命星読みを取得"""
        return cls.query.filter_by(star_number=star_number).first()
    
    @classmethod
    def get_all(cls):
        """全ての日命星読みを取得"""
        return cls.query.order_by(cls.star_number).all() 