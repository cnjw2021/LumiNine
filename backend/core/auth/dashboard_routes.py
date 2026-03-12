"""대시보드 API 라우트 — thin controller.

각 핸들러: 요청 파싱 → UseCase 호출 → JSON 응답 포맷팅.
비즈니스 로직은 DashboardUseCase에 위임합니다.
"""
import json
from datetime import datetime, timezone

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from apps.reading.shared.use_cases.dashboard_use_case import DashboardUseCase
from core.auth.auth_utils import get_current_user
from core.exceptions import AppError
from core.models.exceptions import UserNotFoundError
from core.utils.logger import get_logger

logger = get_logger(__name__)

# target_name 최대 길이 (DB 컬럼 VARCHAR(100)과 일치)
_TARGET_NAME_MAX_LENGTH = 100


def create_dashboard_bp(use_case: DashboardUseCase) -> Blueprint:
    """대시보드 Blueprint를 생성합니다."""
    bp = Blueprint('dashboard', __name__, url_prefix='/api')

    # ── Superuser 전용 엔드포인트 ──────────────────────────

    @bp.route('/admin/dashboard/summary', methods=['GET'])
    @jwt_required()
    def admin_summary():
        try:
            current_user = get_current_user()
            result = use_case.get_admin_summary(current_user)
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except AppError as e:
            return _json_response(e.to_dict(), e.status)
        except Exception as e:
            logger.error("admin_summary 에러: %s", e)
            return _json_response(
                {'error': '대시보드 요약 조회 중 오류가 발생했습니다.'}, 500,
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

            # start/end가 제공됐지만 ISO 파싱 실패 시 400 응답
            if start_str is not None and start is None:
                return _json_response(
                    {'error': "Invalid 'start' parameter. Expected ISO 8601 datetime string."},
                    400,
                )
            if end_str is not None and end is None:
                return _json_response(
                    {'error': "Invalid 'end' parameter. Expected ISO 8601 datetime string."},
                    400,
                )

            result = use_case.get_admin_chart_data(current_user, start, end, interval)
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except AppError as e:
            return _json_response(e.to_dict(), e.status)
        except Exception as e:
            logger.error("admin_chart 에러: %s", e)
            return _json_response(
                {'error': '차트 데이터 조회 중 오류가 발생했습니다.'}, 500,
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

            result = use_case.get_admin_users(
                current_user, page, per_page, sort, order, search,
            )
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except AppError as e:
            return _json_response(e.to_dict(), e.status)
        except Exception as e:
            logger.error("admin_users 에러: %s", e)
            return _json_response(
                {'error': '사용자 목록 조회 중 오류가 발생했습니다.'}, 500,
            )

    # ── 일반 사용자 엔드포인트 ─────────────────────────────

    @bp.route('/dashboard/my/summary', methods=['GET'])
    @jwt_required()
    def my_summary():
        try:
            current_user = get_current_user()
            result = use_case.get_my_summary(current_user)
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except Exception as e:
            logger.error("my_summary 에러: %s", e)
            return _json_response(
                {'error': '개인 요약 조회 중 오류가 발생했습니다.'}, 500,
            )

    @bp.route('/dashboard/my/history', methods=['GET'])
    @jwt_required()
    def my_history():
        try:
            current_user = get_current_user()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            result = use_case.get_my_history(current_user, page, per_page)
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except Exception as e:
            logger.error("my_history 에러: %s", e)
            return _json_response(
                {'error': '이력 조회 중 오류가 발생했습니다.'}, 500,
            )

    @bp.route('/dashboard/my/chart', methods=['GET'])
    @jwt_required()
    def my_chart():
        try:
            current_user = get_current_user()
            result = use_case.get_my_chart(current_user)
            return _json_response(result, 200)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except Exception as e:
            logger.error("my_chart 에러: %s", e)
            return _json_response(
                {'error': '차트 데이터 조회 중 오류가 발생했습니다.'}, 500,
            )

    # ── PDF 이벤트 기록 ───────────────────────────────────

    @bp.route('/events/pdf-download', methods=['POST'])
    @jwt_required()
    def record_pdf_download():
        try:
            current_user = get_current_user()
            data = request.get_json(silent=True) or {}

            target_name_raw = data.get('target_name')
            if target_name_raw is None:
                target_name = None
            else:
                target_name = str(target_name_raw)
                if len(target_name) > _TARGET_NAME_MAX_LENGTH:
                    target_name = target_name[:_TARGET_NAME_MAX_LENGTH]

            # target_year / target_month 파라미터 검증 및 int 캐스팅
            target_year_raw = data.get('target_year')
            target_month_raw = data.get('target_month')

            target_year = None
            target_month = None
            try:
                if target_year_raw is not None:
                    target_year = int(target_year_raw)
                if target_month_raw is not None:
                    target_month = int(target_month_raw)
            except (TypeError, ValueError):
                return _json_response({'error': '잘못된 파라미터입니다.'}, 400)

            if target_month is not None and not (1 <= target_month <= 12):
                return _json_response({'error': '잘못된 파라미터입니다.'}, 400)

            use_case.record_pdf_download(
                user_id=current_user.id,
                target_name=target_name,
                target_year=target_year,
                target_month=target_month,
            )
            return _json_response({'status': 'ok'}, 201)
        except UserNotFoundError as e:
            return _json_response({'error': str(e)}, 404)
        except Exception as e:
            logger.error("record_pdf_download 에러: %s", e)
            return _json_response(
                {'error': 'PDF 이벤트 기록 중 오류가 발생했습니다.'}, 500,
            )

    return bp


# ── 헬퍼 함수 ─────────────────────────────────────────────

def _json_response(data: dict, status: int) -> Response:
    """JSON Response를 생성합니다."""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype='application/json',
    )


def _parse_datetime(value: str | None) -> datetime | None:
    """ISO-8601 문자열을 datetime으로 파싱합니다.

    JavaScript `new Date().toISOString()` 형식(trailing 'Z')도 지원합니다.
    """
    if not value:
        return None
    try:
        # JavaScript ISO 문자열의 trailing 'Z' → '+00:00' 정규화
        normalized = value.replace('Z', '+00:00')
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None
