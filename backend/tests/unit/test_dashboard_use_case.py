"""대시보드 유즈케이스 단위 테스트.

DashboardUseCase의 비즈니스 로직을 Mock 리포지토리로 검증합니다.
외부 인프라(DB, HTTP) 없이 실행됩니다.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from apps.reading.shared.use_cases.dashboard_use_case import DashboardUseCase


# ── Stub User ─────────────────────────────────────────────

class _StubUser:
    """테스트용 사용자 스텁."""

    def __init__(self, user_id: int = 1, is_superuser: bool = False) -> None:
        self.id = user_id
        self.is_superuser = is_superuser


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture
def mock_repo() -> MagicMock:
    """Mock IDashboardRepository."""
    return MagicMock()


@pytest.fixture
def use_case(mock_repo: MagicMock) -> DashboardUseCase:
    """DashboardUseCase with injected mock repo."""
    return DashboardUseCase(mock_repo)


@pytest.fixture
def superuser() -> _StubUser:
    return _StubUser(user_id=1, is_superuser=True)


@pytest.fixture
def normal_user() -> _StubUser:
    return _StubUser(user_id=2, is_superuser=False)


# ── Superuser 요약 테스트 ─────────────────────────────────

class TestGetAdminSummary:
    """get_admin_summary 비즈니스 로직 테스트."""

    def test_superuser_returns_summary(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, superuser: _StubUser,
    ) -> None:
        mock_repo.get_total_reading_count.return_value = 100
        mock_repo.get_total_pdf_count.return_value = 50
        mock_repo.get_active_user_count.return_value = 10

        result = use_case.get_admin_summary(superuser)

        assert result['total_readings'] == 100
        assert result['total_pdfs'] == 50
        assert result['active_users'] == 10

    def test_normal_user_raises_permission_error(
        self, use_case: DashboardUseCase, normal_user: _StubUser,
    ) -> None:
        with pytest.raises(PermissionError):
            use_case.get_admin_summary(normal_user)


# ── Superuser 사용자 목록 테스트 ──────────────────────────

class TestGetAdminUsers:
    """get_admin_users 비즈니스 로직 테스트."""

    def test_returns_paginated_users(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, superuser: _StubUser,
    ) -> None:
        mock_repo.get_users_with_stats.return_value = [
            {'id': 1, 'name': 'User1', 'email': 'u1@test.com',
             'reading_count': 5, 'pdf_count': 3, 'last_reading_date': None},
        ]
        mock_repo.get_users_count.return_value = 1

        result = use_case.get_admin_users(superuser, page=1, per_page=20, sort='name', order='asc', search=None)

        assert len(result['users']) == 1
        assert result['pagination']['total'] == 1
        assert result['pagination']['page'] == 1

    def test_invalid_sort_defaults_to_name(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, superuser: _StubUser,
    ) -> None:
        mock_repo.get_users_with_stats.return_value = []
        mock_repo.get_users_count.return_value = 0

        result = use_case.get_admin_users(
            superuser, page=1, per_page=20, sort='invalid_field', order='asc', search=None,
        )

        # 내부적으로 sort='name'으로 폴백
        mock_repo.get_users_with_stats.assert_called_once_with(1, 20, 'name', 'asc', None)

    def test_per_page_clamped_to_100(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, superuser: _StubUser,
    ) -> None:
        mock_repo.get_users_with_stats.return_value = []
        mock_repo.get_users_count.return_value = 0

        use_case.get_admin_users(
            superuser, page=1, per_page=999, sort='name', order='asc', search=None,
        )

        # per_page가 100으로 클램핑됨
        mock_repo.get_users_with_stats.assert_called_once_with(1, 100, 'name', 'asc', None)

    def test_normal_user_denied(
        self, use_case: DashboardUseCase, normal_user: _StubUser,
    ) -> None:
        with pytest.raises(PermissionError):
            use_case.get_admin_users(normal_user, 1, 20, 'name', 'asc', None)


# ── 개인 요약 테스트 ──────────────────────────────────────

class TestGetMySummary:
    """get_my_summary 개인 대시보드 테스트."""

    def test_returns_user_stats(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, normal_user: _StubUser,
    ) -> None:
        mock_repo.get_user_reading_count.return_value = 10
        mock_repo.get_user_pdf_count.return_value = 5
        mock_repo.get_user_last_reading_date.return_value = '2026-03-01T00:00:00'

        result = use_case.get_my_summary(normal_user)

        assert result['reading_count'] == 10
        assert result['pdf_count'] == 5
        assert result['last_reading_date'] == '2026-03-01T00:00:00'
        mock_repo.get_user_reading_count.assert_called_once_with(2)


# ── 개인 이력 테스트 ──────────────────────────────────────

class TestGetMyHistory:
    """get_my_history 이력 조회 테스트."""

    def test_returns_paginated_history(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, normal_user: _StubUser,
    ) -> None:
        mock_repo.get_user_reading_history.return_value = [
            {'id': 1, 'target_year': 2026, 'target_month': 3, 'locale': 'ja', 'created_at': '2026-03-01T00:00:00'},
        ]
        mock_repo.get_user_reading_history_count.return_value = 1
        mock_repo.get_user_pdf_history.return_value = []
        mock_repo.get_user_pdf_history_count.return_value = 0

        result = use_case.get_my_history(normal_user, page=1, per_page=20)

        assert len(result['readings']['items']) == 1
        assert result['readings']['total'] == 1
        assert result['pdfs']['total'] == 0


# ── PDF 이벤트 기록 테스트 ────────────────────────────────

class TestRecordPdfDownload:
    """record_pdf_download 이벤트 기록 테스트."""

    def test_delegates_to_repo(
        self, use_case: DashboardUseCase, mock_repo: MagicMock,
    ) -> None:
        use_case.record_pdf_download(
            user_id=1,
            target_name='TestUser',
            target_year=2026,
            target_month=3,
        )

        mock_repo.record_pdf_download.assert_called_once_with(1, 'TestUser', 2026, 3)


# ── 차트 데이터 테스트 ────────────────────────────────────

class TestGetAdminChartData:
    """get_admin_chart_data 차트 데이터 테스트."""

    def test_default_interval_fallback(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, superuser: _StubUser,
    ) -> None:
        mock_repo.get_readings_by_period.return_value = []
        mock_repo.get_pdfs_by_period.return_value = []

        result = use_case.get_admin_chart_data(
            superuser, start=None, end=None, interval='invalid',
        )

        assert result['interval'] == 'daily'


class TestGetMyChart:
    """get_my_chart 미니 차트 테스트."""

    def test_returns_chart_data(
        self, use_case: DashboardUseCase, mock_repo: MagicMock, normal_user: _StubUser,
    ) -> None:
        mock_repo.get_user_readings_by_month.return_value = [
            {'month': '2026-01', 'count': 3},
            {'month': '2026-02', 'count': 5},
        ]

        result = use_case.get_my_chart(normal_user)

        assert len(result['readings']) == 2
        mock_repo.get_user_readings_by_month.assert_called_once_with(2, 6)
