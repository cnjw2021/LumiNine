from datetime import datetime, timezone
from core.database import db

class Permission(db.Model):
    """権限(Permission) エンティティ"""
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """エンティティ オブジェクトを辞書形式に変換します."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
        }
