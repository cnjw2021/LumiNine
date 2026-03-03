"""パワーストーンマスターモデル."""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from core.database import db


class PowerStoneMaster(db.Model):
    """パワーストーンマスターテーブル.

    powerstone_catalog.json のデータを DB で管理する。
    stone_id をキーとして五行・主副区分・多言語名・基本石マッピングを保持。
    """

    __tablename__ = 'powerstone_master'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stone_id = Column(String(30), unique=True, nullable=False)
    name_ja = Column(String(50), nullable=False)
    name_ko = Column(String(50), nullable=False)
    name_en = Column(String(50), nullable=False)
    gogyo = Column(String(5), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    image_url = Column(String(255), nullable=True)
    base_star = Column(Integer, nullable=True)
    created_at = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<PowerStoneMaster {self.stone_id} ({self.gogyo})>"
