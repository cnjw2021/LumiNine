from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

from apps.ninestarki.use_cases.permission_use_case import PermissionUseCase
from core.models.exceptions import UserNotFoundError, PermissionError
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_permission_bp(perm_use_case: PermissionUseCase):
    """권한 관련 Blueprint를 생성합니다."""
    permission_bp = Blueprint('permission', __name__, url_prefix='/api/permissions')
    
    def permission_manage_required(fn):
        """권한 관리 권한을 확인하는 데코레이터"""
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                perm_use_case.check_management_permission(get_jwt_identity())
                return fn(*args, **kwargs)
            except PermissionError as e:
                return jsonify({'error': str(e), 'code': 'permission_denied'}), 403
            except Exception as e:
                logger.error(f"Permission check error: {str(e)}")
                return jsonify({'error': '인증에 실패했습니다', 'code': 'authentication_failed'}), 401
        return wrapper

    @permission_bp.route('', methods=['GET'])
    @permission_manage_required
    def get_all_permissions():
        """모든 권한 목록을 가져옵니다."""
        try:
            result = perm_use_case.get_all_permissions()
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error getting permissions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @permission_bp.route('/<int:user_id>', methods=['GET'])
    @permission_manage_required
    def get_user_permissions(user_id):
        """특정 사용자의 권한을 가져옵니다."""
        try:
            result = perm_use_case.get_user_permissions(user_id)
            return jsonify(result), 200
        except UserNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @permission_bp.route('/<int:user_id>', methods=['POST'])
    @permission_manage_required
    def update_user_permissions(user_id):
        """사용자의 권한을 업데이트합니다."""
        try:
            data = request.get_json()
            permission_codes = data.get('permissions', [])
            if not isinstance(permission_codes, list):
                return jsonify({'error': '권한은 배열로 지정해야 합니다'}), 400
            
            perm_use_case.update_user_permissions(get_jwt_identity(), user_id, permission_codes)
            
            return jsonify({'message': '권한을 업데이트했습니다.'}), 200
        except (UserNotFoundError, PermissionError) as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @permission_bp.route('', methods=['POST'])
    @permission_manage_required
    def create_permission():
        """새로운 권한을 생성합니다."""
        try:
            permission = perm_use_case.create_permission(request.get_json())
            return jsonify({'message': '권한을 생성했습니다.', 'permission': permission.to_dict()}), 201
        except (ValueError, PermissionError) as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @permission_bp.route('/check', methods=['POST'])
    @jwt_required()
    def check_permission():
        """사용자가 특정 권한을 가졌는지 확인합니다."""
        try:
            data = request.get_json()
            permission_code = data.get('permission_code')
            has_permission = perm_use_case.check_user_permission(get_jwt_identity(), permission_code)
            return jsonify({'has_permission': has_permission, 'permission_code': permission_code}), 200
        except (ValueError, UserNotFoundError) as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return permission_bp