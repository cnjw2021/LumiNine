"""システム設定モデル"""

from core.database import db

class SystemConfig(db.Model):
    """システム設定テーブルのモデルクラス"""
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def get_by_key(cls, key):
        """キーに基づいて設定値を取得"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else None

    @classmethod
    def set_value(cls, key, value, description=None, updated_by=None):
        """設定値を保存または更新"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
            if description:
                config.description = description
        else:
            config = cls(
                key=key,
                value=str(value),
                description=description
            )
            db.session.add(config)
        db.session.commit() 