from datetime import datetime, timezone
from core.database import db

# ユーザー権限の中間テーブルモデル
class UserPermission(db.Model):
    """ユーザーと権限の中間テーブルモデル"""
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ユニーク制約
    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='user_permission'),
    )

    def __init__(self, user_id, permission_id):
        self.user_id = user_id
        self.permission_id = permission_id

    def __repr__(self):
        return f"<UserPermission user_id={self.user_id}, permission_id={self.permission_id}>"
