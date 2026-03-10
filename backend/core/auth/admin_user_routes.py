"""Admin user CRUD routes — thin controllers delegating to AdminUserUseCase.

Each handler: parse request → call use case → format JSON response.
All business logic, validation, and authorization live in AdminUserUseCase.
"""

from flask import request, Response
from flask_jwt_extended import jwt_required
from apps.reading.shared.use_cases.admin_user_use_case import AdminUserUseCase
from core.models.exceptions import (
    UserNotFoundError,
    PermissionError,
    AccountLimitExceededError,
    ValidationError,
    UserAlreadyExistsError,
)
from core.auth.auth_utils import get_current_user
from core.utils.logger import get_logger
import json

logger = get_logger(__name__)

# UseCase instance — injected via register_admin_user_routes()
_use_case: AdminUserUseCase = None  # type: ignore


def register_admin_user_routes(bp, use_case: AdminUserUseCase):
    """Register admin user CRUD routes on the given blueprint."""
    global _use_case
    _use_case = use_case

    @bp.route('/admin/users', methods=['GET'])
    @jwt_required()
    def list_users():
        try:
            current_user = get_current_user()
            show_deleted = request.args.get('show_deleted', 'false').lower() == 'true'
            result = _use_case.list_users(current_user, show_deleted)
            return Response(json.dumps(result), status=200, mimetype='application/json')
        except PermissionError as e:
            return Response(json.dumps({"error": str(e)}), status=403, mimetype='application/json')
        except Exception as e:
            logger.error(f"Error in list_users: {str(e)}")
            return Response(
                json.dumps({"error": "ユーザー一覧の取得中にエラーが発生しました"}),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/users', methods=['POST'])
    @jwt_required()
    def create_user():
        try:
            current_user = get_current_user()
            data = request.get_json()
            result = _use_case.create_user(current_user, data)
            return Response(json.dumps(result), status=201, mimetype='application/json')
        except (PermissionError, AccountLimitExceededError) as e:
            return Response(json.dumps({"error": str(e)}), status=403, mimetype='application/json')
        except (ValidationError, UserAlreadyExistsError) as e:
            return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')
        except Exception as e:
            logger.error(f"Error in create_user: {str(e)}")
            return Response(
                json.dumps({"error": "ユーザー作成中にエラーが発生しました"}),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def delete_user(user_id):
        try:
            current_user = get_current_user()
            result = _use_case.delete_user(current_user, user_id)
            return Response(json.dumps(result), status=200, mimetype='application/json')
        except PermissionError as e:
            return Response(json.dumps({"error": str(e)}), status=403, mimetype='application/json')
        except UserNotFoundError as e:
            return Response(json.dumps({"error": str(e)}), status=404, mimetype='application/json')
        except Exception as e:
            logger.error(f"Error in delete_user: {str(e)}")
            return Response(
                json.dumps({"error": "ユーザー削除中にエラーが発生しました"}),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        try:
            current_user = get_current_user()
            data = request.get_json()
            result = _use_case.update_user(current_user, user_id, data)
            return Response(json.dumps(result), status=200, mimetype='application/json')
        except PermissionError as e:
            return Response(json.dumps({"error": str(e)}), status=403, mimetype='application/json')
        except UserNotFoundError as e:
            return Response(json.dumps({"error": str(e)}), status=404, mimetype='application/json')
        except ValidationError as e:
            return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')
        except Exception as e:
            logger.error(f"Error in update_user: {str(e)}")
            return Response(
                json.dumps({"error": "ユーザー更新中にエラーが発生しました"}),
                status=500, mimetype='application/json',
            )

    @bp.route('/admin/users/<int:user_id>/account-limit', methods=['PUT'])
    @jwt_required()
    def update_account_limit(user_id):
        try:
            current_user = get_current_user()
            data = request.get_json()
            new_limit = data.get('account_limit')
            result = _use_case.update_account_limit(current_user, user_id, new_limit)
            return Response(json.dumps(result), status=200, mimetype='application/json')
        except PermissionError as e:
            return Response(json.dumps({"error": str(e)}), status=403, mimetype='application/json')
        except UserNotFoundError as e:
            return Response(json.dumps({"error": str(e)}), status=404, mimetype='application/json')
        except ValidationError as e:
            return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')
        except Exception as e:
            logger.error(f"Error in update_account_limit: {str(e)}")
            return Response(
                json.dumps({"error": "アカウント制限数の更新中にエラーが発生しました"}),
                status=500, mimetype='application/json',
            )
