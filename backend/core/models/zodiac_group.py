"""十二支グループマスタデータを管理するモデル"""

from datetime import datetime
from core.database import db

class ZodiacGroup(db.Model):
    """十二支グループマスタ（書籍上部にある 4 グループを管理）"""
    __tablename__ = 'zodiac_groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(20), nullable=False, unique=True)  # 例『子午卯酉』
    description = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'group_name': self.group_name,
            'description': self.description
        }
