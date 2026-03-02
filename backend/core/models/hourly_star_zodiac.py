from datetime import datetime
from core.database import db

class HourlyStarZodiac(db.Model):
    """干支グループ×九星中宮 → 時の十二支（陽遁/隠遁別）"""
    __tablename__ = 'hourly_star_zodiacs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pattern_type = db.Column(db.Enum('SP_ASC', 'SP_DESC'), nullable=False)  # 陽遁=SP_ASC, 隠遁=SP_DESC
    group_id = db.Column(db.Integer, db.ForeignKey('zodiac_groups.id'), nullable=False)
    center_star = db.Column(db.Integer, nullable=False)  # 中宮の九星
    hour_zodiac = db.Column(db.String(2), nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = db.relationship('ZodiacGroup', backref='hourly_rules')

    __table_args__ = ()

    def to_dict(self):
        return {
            'id': self.id,
            'pattern_type': self.pattern_type,
            'group_id': self.group_id,
            'center_star': self.center_star,
            'hour_zodiac': self.hour_zodiac,
            'start_hour': self.start_hour,
            'end_hour': self.end_hour
        } 