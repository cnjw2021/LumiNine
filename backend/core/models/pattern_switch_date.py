from datetime import datetime

from core.database import db

class PatternSwitchDate(db.Model):
    """陽遁 (SP_ASC) / 隠遁 (SP_DESC) の切替日マスタ"""

    __tablename__ = 'pattern_switch_dates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, unique=True, comment='切替日')
    pattern = db.Column(db.Enum('SP_ASC', 'SP_DESC'), nullable=False, comment='切替後のパターン')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='作成日時')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'pattern': self.pattern,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        } 