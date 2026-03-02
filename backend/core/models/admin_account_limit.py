"""管理者アカウント上限モデル"""

from core.database import db

class AdminAccountLimit(db.Model):
    """管理者アカウントの上限を管理するモデルクラス"""
    __tablename__ = 'admin_account_limit'

    id = db.Column(db.Integer, primary_key=True)
    max_accounts = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, max_accounts=10):
        self.max_accounts = max_accounts 