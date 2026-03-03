"""推薦履歴モデル."""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from core.database import db


class RecommendationHistory(db.Model):
    """パワーストーン推薦履歴テーブル.

    ユーザーごとの月別推薦結果を記録する。
    同一ユーザー×年×月は UNIQUE 制約により1件のみ保持。
    """

    __tablename__ = 'recommendation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    main_star = Column(Integer, nullable=False)
    target_year = Column(Integer, nullable=False)
    target_month = Column(Integer, nullable=False)
    base_stone_id = Column(String(30), nullable=False)
    monthly_stone_id = Column(String(30), nullable=False)
    protection_stone_id = Column(String(30), nullable=False)
    locale = Column(String(5), nullable=False, default='ja')
    created_at = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<RecommendationHistory user={self.user_id} "
            f"{self.target_year}/{self.target_month}>"
        )
