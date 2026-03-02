"""後天定位の運気メッセージモデル"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql.expression import text
from core.database import db

class MonthStarAcquiredFortuneMessage(db.Model):
    """後天定位の運気メッセージモデル
    
    九星ごとに、後天定位の吉運と凶運のメッセージを格納するモデル
    """
    __tablename__ = 'month_star_acquired_fortune_message'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    star_number = Column(Integer, nullable=False, unique=True, comment="九星番号（1-9）")
    luck_title = Column(String(100), nullable=False, comment="吉運タイトル")
    luck_details = Column(Text, nullable=False, comment="吉運の詳細説明")
    unluck_title = Column(String(100), nullable=False, comment="凶運タイトル")
    unluck_details = Column(Text, nullable=False, comment="凶運の詳細説明")
    
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), 
                        onupdate=text('CURRENT_TIMESTAMP'), nullable=False)
    
    def __repr__(self):
        return f"<MonthStarAcquiredFortuneMessage(id={self.id}, star={self.star_number})>"
    
    def to_dict(self):
        """モデルを辞書に変換"""
        return {
            'id': self.id,
            'star_number': self.star_number,
            'luck_title': self.luck_title,
            'luck_details': self.luck_details,
            'unluck_title': self.unluck_title,
            'unluck_details': self.unluck_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_star_number(cls, star_number):
        """星番号から後天定位メッセージを取得"""
        return cls.query.filter_by(star_number=star_number).first()
    
    @classmethod
    def get_all(cls):
        """全ての後天定位メッセージを取得"""
        return cls.query.order_by(cls.star_number).all() 