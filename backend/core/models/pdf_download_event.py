"""PDF 다운로드 이벤트 모델."""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from core.database import db


class PdfDownloadEvent(db.Model):
    """PDF 다운로드 이벤트 테이블.

    프론트엔드에서 PDF 다운로드 시 기록되는 이벤트를 저장합니다.
    """

    __tablename__ = 'pdf_download_events'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    target_name = Column(String(100), nullable=True)
    target_year = Column(Integer, nullable=True)
    target_month = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<PdfDownloadEvent user={self.user_id} "
            f"{self.target_year}/{self.target_month}>"
        )
