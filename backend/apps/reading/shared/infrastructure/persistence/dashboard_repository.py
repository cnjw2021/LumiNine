"""대시보드 리포지토리 구현.

SQLAlchemy 기반으로 recommendation_history, pdf_download_events, users 테이블을
집계하여 대시보드 데이터를 제공합니다.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, text, desc, asc
from sqlalchemy.orm import Query

from apps.reading.shared.domain.entities.user import User
from apps.reading.shared.domain.repositories.dashboard_repository_interface import (
    IDashboardRepository,
)
from core.database import db
from core.models.pdf_download_event import PdfDownloadEvent
from core.models.recommendation_history import RecommendationHistory


# ── 집계 간격에 따른 날짜 포맷 (PostgreSQL) ───────────────
_INTERVAL_FORMAT = {
    'daily': 'YYYY-MM-DD',
    'weekly': 'IYYY-IW',       # ISO 주차
    'monthly': 'YYYY-MM',
}


class DashboardRepository(IDashboardRepository):
    """SQLAlchemy 기반 대시보드 리포지토리."""

    # ── 전체 집계 (Superuser) ──────────────────────────────

    def get_total_reading_count(self) -> int:
        return db.session.query(
            func.count(RecommendationHistory.id),
        ).scalar() or 0

    def get_total_pdf_count(self) -> int:
        return db.session.query(
            func.count(PdfDownloadEvent.id),
        ).scalar() or 0

    def get_active_user_count(self) -> int:
        return db.session.query(
            func.count(User.id),
        ).filter(User.is_deleted.is_(False)).scalar() or 0

    def get_readings_by_period(
        self, start: datetime, end: datetime, interval: str,
    ) -> List[Dict[str, Any]]:
        fmt = _INTERVAL_FORMAT.get(interval, _INTERVAL_FORMAT['daily'])
        rows = (
            db.session
            .query(
                func.to_char(RecommendationHistory.created_at, fmt).label('date'),
                func.count(RecommendationHistory.id).label('count'),
            )
            .filter(
                RecommendationHistory.created_at >= start,
                RecommendationHistory.created_at <= end,
            )
            .group_by(text('1'))
            .order_by(text('1'))
            .all()
        )
        return [{'date': r.date, 'count': r.count} for r in rows]

    def get_pdfs_by_period(
        self, start: datetime, end: datetime, interval: str,
    ) -> List[Dict[str, Any]]:
        fmt = _INTERVAL_FORMAT.get(interval, _INTERVAL_FORMAT['daily'])
        rows = (
            db.session
            .query(
                func.to_char(PdfDownloadEvent.created_at, fmt).label('date'),
                func.count(PdfDownloadEvent.id).label('count'),
            )
            .filter(
                PdfDownloadEvent.created_at >= start,
                PdfDownloadEvent.created_at <= end,
            )
            .group_by(text('1'))
            .order_by(text('1'))
            .all()
        )
        return [{'date': r.date, 'count': r.count} for r in rows]

    # ── 사용자별 집계 (서버 사이드 페이징) ─────────────────

    _SORT_COLUMNS = {
        'name': User.name,
        'email': User.email,
        'reading_count': 'reading_count',
        'pdf_count': 'pdf_count',
        'last_reading_date': 'last_reading_date',
    }

    def _users_base_query(self, search: Optional[str]) -> Query:
        """사용자 목록 기반 쿼리 (JOIN + 집계)."""
        reading_count = (
            db.session
            .query(
                RecommendationHistory.user_id,
                func.count(RecommendationHistory.id).label('reading_count'),
            )
            .group_by(RecommendationHistory.user_id)
            .subquery('rc')
        )

        pdf_count = (
            db.session
            .query(
                PdfDownloadEvent.user_id,
                func.count(PdfDownloadEvent.id).label('pdf_count'),
            )
            .group_by(PdfDownloadEvent.user_id)
            .subquery('pc')
        )

        last_reading = (
            db.session
            .query(
                RecommendationHistory.user_id,
                func.max(RecommendationHistory.created_at).label('last_reading_date'),
            )
            .group_by(RecommendationHistory.user_id)
            .subquery('lr')
        )

        q = (
            db.session
            .query(
                User.id,
                User.name,
                User.email,
                func.coalesce(reading_count.c.reading_count, 0).label('reading_count'),
                func.coalesce(pdf_count.c.pdf_count, 0).label('pdf_count'),
                last_reading.c.last_reading_date.label('last_reading_date'),
            )
            .outerjoin(reading_count, User.id == reading_count.c.user_id)
            .outerjoin(pdf_count, User.id == pdf_count.c.user_id)
            .outerjoin(last_reading, User.id == last_reading.c.user_id)
            .filter(User.is_deleted.is_(False))
        )

        if search:
            pattern = f'%{search}%'
            q = q.filter(
                (User.name.ilike(pattern)) | (User.email.ilike(pattern)),
            )

        return q

    def get_users_with_stats(
        self,
        page: int,
        per_page: int,
        sort: str,
        order: str,
        search: Optional[str],
    ) -> List[Dict[str, Any]]:
        q = self._users_base_query(search)

        # 정렬
        sort_col = self._SORT_COLUMNS.get(sort, User.name)
        if isinstance(sort_col, str):
            sort_col = text(sort_col)
        sort_expr = desc(sort_col) if order == 'desc' else asc(sort_col)
        q = q.order_by(sort_expr)

        # 페이징
        offset = (page - 1) * per_page
        rows = q.offset(offset).limit(per_page).all()

        return [
            {
                'id': r.id,
                'name': r.name,
                'email': r.email,
                'reading_count': r.reading_count,
                'pdf_count': r.pdf_count,
                'last_reading_date': (
                    r.last_reading_date.isoformat() if r.last_reading_date else None
                ),
            }
            for r in rows
        ]

    def get_users_count(self, search: Optional[str]) -> int:
        q = db.session.query(func.count(User.id)).filter(
            User.is_deleted.is_(False),
        )
        if search:
            pattern = f'%{search}%'
            q = q.filter(
                (User.name.ilike(pattern)) | (User.email.ilike(pattern)),
            )
        return q.scalar() or 0

    # ── 개인 집계 ─────────────────────────────────────────

    def get_user_reading_count(self, user_id: int) -> int:
        return db.session.query(
            func.count(RecommendationHistory.id),
        ).filter(RecommendationHistory.user_id == user_id).scalar() or 0

    def get_user_pdf_count(self, user_id: int) -> int:
        return db.session.query(
            func.count(PdfDownloadEvent.id),
        ).filter(PdfDownloadEvent.user_id == user_id).scalar() or 0

    def get_user_last_reading_date(self, user_id: int) -> Optional[str]:
        result = db.session.query(
            func.max(RecommendationHistory.created_at),
        ).filter(RecommendationHistory.user_id == user_id).scalar()
        return result.isoformat() if result else None

    def get_user_reading_history(
        self, user_id: int, page: int, per_page: int,
    ) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        rows = (
            db.session
            .query(RecommendationHistory)
            .filter(RecommendationHistory.user_id == user_id)
            .order_by(desc(RecommendationHistory.created_at))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        return [
            {
                'id': r.id,
                'target_year': r.target_year,
                'target_month': r.target_month,
                'locale': r.locale,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    def get_user_reading_history_count(self, user_id: int) -> int:
        return db.session.query(
            func.count(RecommendationHistory.id),
        ).filter(RecommendationHistory.user_id == user_id).scalar() or 0

    def get_user_pdf_history(
        self, user_id: int, page: int, per_page: int,
    ) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        rows = (
            db.session
            .query(PdfDownloadEvent)
            .filter(PdfDownloadEvent.user_id == user_id)
            .order_by(desc(PdfDownloadEvent.created_at))
            .offset(offset)
            .limit(per_page)
            .all()
        )
        return [
            {
                'id': r.id,
                'target_name': r.target_name,
                'target_year': r.target_year,
                'target_month': r.target_month,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    def get_user_pdf_history_count(self, user_id: int) -> int:
        return db.session.query(
            func.count(PdfDownloadEvent.id),
        ).filter(PdfDownloadEvent.user_id == user_id).scalar() or 0

    def get_user_readings_by_month(
        self, user_id: int, months: int,
    ) -> List[Dict[str, Any]]:
        rows = (
            db.session
            .query(
                func.to_char(RecommendationHistory.created_at, 'YYYY-MM').label('month'),
                func.count(RecommendationHistory.id).label('count'),
            )
            .filter(
                RecommendationHistory.user_id == user_id,
                RecommendationHistory.created_at >= func.now() - func.make_interval(months=months),
            )
            .group_by(text('1'))
            .order_by(text('1'))
            .all()
        )
        return [{'month': r.month, 'count': r.count} for r in rows]

    # ── 이벤트 기록 ───────────────────────────────────────

    def record_pdf_download(
        self,
        user_id: int,
        target_name: Optional[str],
        target_year: Optional[int],
        target_month: Optional[int],
    ) -> None:
        event = PdfDownloadEvent(
            user_id=user_id,
            target_name=target_name,
            target_year=target_year,
            target_month=target_month,
        )
        db.session.add(event)
        db.session.commit()
