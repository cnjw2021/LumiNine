"""대시보드 리포지토리 인터페이스.

감정 실행 수/PDF 다운로드 수 집계 및 이벤트 기록을 위한 계약 정의.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class IDashboardRepository(ABC):
    """대시보드 데이터 접근 인터페이스."""

    # ── 전체 집계 (Superuser) ──────────────────────────────

    @abstractmethod
    def get_total_reading_count(self) -> int:
        """전체 감정 실행 수."""

    @abstractmethod
    def get_total_pdf_count(self) -> int:
        """전체 PDF 다운로드 수."""

    @abstractmethod
    def get_active_user_count(self) -> int:
        """활성 사용자 수 (is_deleted=False AND is_active=True)."""

    @abstractmethod
    def get_readings_by_period(
        self, start: datetime, end: datetime, interval: str,
    ) -> List[Dict[str, Any]]:
        """기간별 감정 실행 추이 데이터.

        Args:
            interval: 'daily' | 'weekly' | 'monthly'
        Returns:
            [{"date": "2026-01-01", "count": 10}, ...]
        """

    @abstractmethod
    def get_pdfs_by_period(
        self, start: datetime, end: datetime, interval: str,
    ) -> List[Dict[str, Any]]:
        """기간별 PDF 다운로드 추이 데이터."""

    @abstractmethod
    def get_users_with_stats(
        self,
        page: int,
        per_page: int,
        sort: str,
        order: str,
        search: Optional[str],
    ) -> List[Dict[str, Any]]:
        """사용자별 집계 리스트 (서버 사이드 페이징).

        Returns:
            [{"id": 1, "name": "...", "email": "...",
              "reading_count": 5, "pdf_count": 3,
              "last_reading_date": "2026-01-01T00:00:00"}, ...]
        """

    @abstractmethod
    def get_users_count(self, search: Optional[str]) -> int:
        """검색 조건에 맞는 전체 사용자 수 (페이징 메타데이터용)."""

    # ── 개인 집계 (일반 사용자) ─────────────────────────────

    @abstractmethod
    def get_user_reading_count(self, user_id: int) -> int:
        """특정 사용자의 감정 실행 수."""

    @abstractmethod
    def get_user_pdf_count(self, user_id: int) -> int:
        """특정 사용자의 PDF 다운로드 수."""

    @abstractmethod
    def get_user_last_reading_date(self, user_id: int) -> Optional[str]:
        """특정 사용자의 최근 감정 실행일 (ISO 문자열)."""

    @abstractmethod
    def get_user_reading_history(
        self, user_id: int, page: int, per_page: int,
    ) -> List[Dict[str, Any]]:
        """사용자의 감정 실행 이력 (페이징)."""

    @abstractmethod
    def get_user_reading_history_count(self, user_id: int) -> int:
        """사용자의 감정 실행 이력 전체 건수."""

    @abstractmethod
    def get_user_pdf_history(
        self, user_id: int, page: int, per_page: int,
    ) -> List[Dict[str, Any]]:
        """사용자의 PDF 다운로드 이력 (페이징)."""

    @abstractmethod
    def get_user_pdf_history_count(self, user_id: int) -> int:
        """사용자의 PDF 다운로드 이력 전체 건수."""

    @abstractmethod
    def get_user_readings_by_month(
        self, user_id: int, months: int,
    ) -> List[Dict[str, Any]]:
        """최근 N개월 감정 실행 수 추이 (미니 차트).

        Returns:
            [{"month": "2026-01", "count": 3}, ...]
        """

    # ── 이벤트 기록 ───────────────────────────────────────

    @abstractmethod
    def record_pdf_download(
        self,
        user_id: int,
        target_name: Optional[str],
        target_year: Optional[int],
        target_month: Optional[int],
    ) -> None:
        """PDF 다운로드 이벤트를 기록."""
