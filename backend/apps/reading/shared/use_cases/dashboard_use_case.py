"""대시보드 유즈케이스.

Superuser 전체 통계와 일반 사용자 개인 통계의 오케스트레이션을 담당합니다.
비즈니스 로직(권한 체크, 데이터 조합)만 포함하며, HTTP/DB 레이어를 직접 참조하지 않습니다.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from injector import inject

from apps.reading.shared.domain.entities.user import User
from apps.reading.shared.domain.repositories.dashboard_repository_interface import (
    IDashboardRepository,
)
from core.exceptions import ForbiddenError
from core.utils.logger import get_logger

logger = get_logger(__name__)

# ── 상수 ────────────────────────────────────────────────
DEFAULT_CHART_DAYS = 30
MINI_CHART_MONTHS = 6
MAX_PER_PAGE = 100
VALID_INTERVALS = ('daily', 'weekly', 'monthly')
VALID_SORT_FIELDS = ('name', 'email', 'reading_count', 'pdf_count', 'last_reading_date')
VALID_ORDERS = ('asc', 'desc')


class DashboardUseCase:
    """대시보드 비즈니스 오케스트레이션 유즈케이스."""

    @inject
    def __init__(self, repo: IDashboardRepository) -> None:
        self._repo = repo

    # ── Superuser 전용 ────────────────────────────────────

    def get_admin_summary(self, current_user: User) -> Dict[str, Any]:
        """전체 요약 통계를 반환합니다.

        Args:
            current_user: 현재 인증된 사용자 (is_superuser 검증용).

        Raises:
            ForbiddenError: superuser가 아닌 경우.
        """
        self._require_superuser(current_user)

        return {
            'total_readings': self._repo.get_total_reading_count(),
            'total_pdfs': self._repo.get_total_pdf_count(),
            'active_users': self._repo.get_active_user_count(),
        }

    def get_admin_chart_data(
        self,
        current_user: User,
        start: Optional[datetime],
        end: Optional[datetime],
        interval: str,
    ) -> Dict[str, Any]:
        """기간별 추이 차트 데이터를 반환합니다."""
        self._require_superuser(current_user)

        now = datetime.now(timezone.utc)
        if not end:
            end = now
        if not start:
            start = now - timedelta(days=DEFAULT_CHART_DAYS)
        if interval not in VALID_INTERVALS:
            interval = 'daily'

        return {
            'readings': self._repo.get_readings_by_period(start, end, interval),
            'pdfs': self._repo.get_pdfs_by_period(start, end, interval),
            'start': start.isoformat(),
            'end': end.isoformat(),
            'interval': interval,
        }

    def get_admin_users(
        self,
        current_user: User,
        page: int,
        per_page: int,
        sort: str,
        order: str,
        search: Optional[str],
    ) -> Dict[str, Any]:
        """사용자별 집계 리스트를 반환합니다 (서버 사이드 페이징)."""
        self._require_superuser(current_user)

        page = max(1, page)
        per_page = min(max(1, per_page), MAX_PER_PAGE)
        if sort not in VALID_SORT_FIELDS:
            sort = 'name'
        if order not in VALID_ORDERS:
            order = 'asc'

        users = self._repo.get_users_with_stats(page, per_page, sort, order, search)
        total = self._repo.get_users_count(search)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

        return {
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
            },
        }

    # ── 일반 사용자 ───────────────────────────────────────

    def get_my_summary(self, current_user: User) -> Dict[str, Any]:
        """현재 사용자의 개인 요약 통계를 반환합니다."""
        user_id = current_user.id
        return {
            'reading_count': self._repo.get_user_reading_count(user_id),
            'pdf_count': self._repo.get_user_pdf_count(user_id),
            'last_reading_date': self._repo.get_user_last_reading_date(user_id),
        }

    def get_my_history(
        self,
        current_user: User,
        page: int,
        per_page: int,
    ) -> Dict[str, Any]:
        """현재 사용자의 이용 이력을 반환합니다 (페이징)."""
        user_id = current_user.id
        page = max(1, page)
        per_page = min(max(1, per_page), MAX_PER_PAGE)

        readings = self._repo.get_user_reading_history(user_id, page, per_page)
        readings_total = self._repo.get_user_reading_history_count(user_id)
        pdfs = self._repo.get_user_pdf_history(user_id, page, per_page)
        pdfs_total = self._repo.get_user_pdf_history_count(user_id)

        return {
            'readings': {
                'items': readings,
                'total': readings_total,
                'page': page,
                'per_page': per_page,
            },
            'pdfs': {
                'items': pdfs,
                'total': pdfs_total,
                'page': page,
                'per_page': per_page,
            },
        }

    def get_my_chart(self, current_user: User) -> Dict[str, Any]:
        """현재 사용자의 최근 6개월 미니 차트 데이터를 반환합니다."""
        user_id = current_user.id
        return {
            'readings': self._repo.get_user_readings_by_month(
                user_id, MINI_CHART_MONTHS,
            ),
        }

    # ── PDF 이벤트 기록 ───────────────────────────────────

    def record_pdf_download(
        self,
        user_id: int,
        target_name: Optional[str],
        target_year: Optional[int],
        target_month: Optional[int],
    ) -> None:
        """PDF 다운로드 이벤트를 기록합니다."""
        self._repo.record_pdf_download(user_id, target_name, target_year, target_month)
        logger.debug("PDF 다운로드 이벤트 기록: user_id=%d", user_id)

    # ── 내부 헬퍼 ─────────────────────────────────────────

    @staticmethod
    def _require_superuser(user: User) -> None:
        """superuser 권한을 검증합니다."""
        if not user.is_superuser:
            raise ForbiddenError(
                "이 기능은 슈퍼유저만 사용할 수 있습니다.",
                details="is_superuser=True 권한이 필요합니다.",
            )
