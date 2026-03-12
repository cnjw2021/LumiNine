"""대시보드 API 라우트 — thin controller.

각 핸들러: 요청 파싱 → UseCase 호출 → JSON 응답 포맷팅.
비즈니스 로직은 DashboardUseCase에 위임합니다.
"""
from datetime import datetime, timezone

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from apps.reading.shared.use_cases.dashboard_use_case import DashboardUseCase
from core.auth.auth_utils import get_current_user
from core.utils.logger import get_logger

import json

logger = get_logger(__name__)

# UseCase — create_dashboard_bp() 에서 주입
_use_case: DashboardUseCase = None  # type: ignore


def create_dashboard_bp(use_case: DashboardUseCase) -> Blueprint:
    """대시보드 Blueprint를 생성합니다."""
    global _use_case
    _use_case = use_case

    bp = Blueprint('dashboard', __name__, url_prefix='/api')

    # ── Superuser 전용 엔드포인트 ──────────────────────────

    @bp.route('/admin/dashboard/summary', methods=['GET'])
    @jwt_required()
    def admin_summary():
        try:
            current_user = get_current_user()
            result = _use_case.get_admin_summary(current_user)
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except PermissionError as e:
            return Response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=403, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"admin_summary 에러: {e}")
            return Response(
                json.dumps({'error': '대시보드 요약 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/dashboard/chart', methods=['GET'])
    @jwt_required()
    def admin_chart():
        try:
            current_user = get_current_user()
            start_str = request.args.get('start')
            end_str = request.args.get('end')
            interval = request.args.get('interval', 'daily')

            start = _parse_datetime(start_str)
            end = _parse_datetime(end_str)

            result = _use_case.get_admin_chart_data(current_user, start, end, interval)
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except PermissionError as e:
            return Response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=403, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"admin_chart 에러: {e}")
            return Response(
                json.dumps({'error': '차트 데이터 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/dashboard/users', methods=['GET'])
    @jwt_required()
    def admin_users():
        try:
            current_user = get_current_user()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            sort = request.args.get('sort', 'name')
            order = request.args.get('order', 'asc')
            search = request.args.get('search')

            result = _use_case.get_admin_users(
                current_user, page, per_page, sort, order, search,
            )
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except PermissionError as e:
            return Response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=403, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"admin_users 에러: {e}")
            return Response(
                json.dumps({'error': '사용자 목록 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    # ── 일반 사용자 엔드포인트 ─────────────────────────────

    @bp.route('/dashboard/my/summary', methods=['GET'])
    @jwt_required()
    def my_summary():
        try:
            current_user = get_current_user()
            result = _use_case.get_my_summary(current_user)
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"my_summary 에러: {e}")
            return Response(
                json.dumps({'error': '개인 요약 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    @bp.route('/dashboard/my/history', methods=['GET'])
    @jwt_required()
    def my_history():
        try:
            current_user = get_current_user()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            result = _use_case.get_my_history(current_user, page, per_page)
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"my_history 에러: {e}")
            return Response(
                json.dumps({'error': '이력 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    @bp.route('/dashboard/my/chart', methods=['GET'])
    @jwt_required()
    def my_chart():
        try:
            current_user = get_current_user()
            result = _use_case.get_my_chart(current_user)
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"my_chart 에러: {e}")
            return Response(
                json.dumps({'error': '차트 데이터 조회 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    # ── PDF 이벤트 기록 ───────────────────────────────────

    @bp.route('/events/pdf-download', methods=['POST'])
    @jwt_required()
    def record_pdf_download():
        try:
            current_user = get_current_user()
            data = request.get_json() or {}

            _use_case.record_pdf_download(
                user_id=current_user.id,
                target_name=data.get('target_name'),
                target_year=data.get('target_year'),
                target_month=data.get('target_month'),
            )
            return Response(
                json.dumps({'status': 'ok'}, ensure_ascii=False),
                status=201, mimetype='application/json',
            )
        except Exception as e:
            logger.error(f"record_pdf_download 에러: {e}")
            return Response(
                json.dumps({'error': 'PDF 이벤트 기록 중 오류가 발생했습니다.'}, ensure_ascii=False),
                status=500, mimetype='application/json',
            )

    return bp


def _parse_datetime(value: str | None) -> datetime | None:
    """ISO-8601 문자열을 datetime으로 파싱합니다."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None
