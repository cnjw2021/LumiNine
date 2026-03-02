from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, ForeignKey
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class StarAttribute(db.Model):
    __tablename__ = 'star_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    star_number = Column(Integer, ForeignKey('stars.star_number'), nullable=False, comment='九星番号（1-9）')
    attribute_type = Column(String(50), nullable=False, comment='属性タイプ（color, shape, place等）')
    attribute_value = Column(String(100), nullable=False, comment='属性値')
    description = Column(Text, comment='説明')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('star_number', 'attribute_type', 'attribute_value', 
                        name='uix_attribute'),
    )

    def __init__(self, star_number, attribute_type, attribute_value, 
                description=None):
        self.star_number = star_number
        self.attribute_type = attribute_type
        self.attribute_value = attribute_value
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'star_number': self.star_number,
            'attribute_type': self.attribute_type,
            'attribute_value': self.attribute_value,
            'description': self.description
        } 