"""十二支→グループID の対応テーブルを管理するモデル"""

from datetime import datetime
from core.database import db
from .zodiac_group import ZodiacGroup

class ZodiacGroupMember(db.Model):
    """十二支→グループID の対応テーブル"""
    __tablename__ = 'zodiac_group_members'

    zodiac = db.Column(db.String(2), primary_key=True)  # 子 丑 寅 …
    group_id = db.Column(db.Integer, db.ForeignKey('zodiac_groups.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = db.relationship('ZodiacGroup', backref='zodiacs')

    def to_dict(self):
        return {
            'zodiac': self.zodiac,
            'group_id': self.group_id,
            'group_name': self.group.group_name if self.group else None
        }
