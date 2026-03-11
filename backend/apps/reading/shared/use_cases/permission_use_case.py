from typing import List, Dict, Any
from apps.reading.shared.domain.entities.user import User
from apps.reading.shared.domain.entities.permission import Permission
from apps.reading.shared.domain.repositories.user_repository_interface import IUserRepository
from apps.reading.shared.domain.repositories.permission_repository_interface import IPermissionRepository
from core.models.exceptions import UserNotFoundError, PermissionError
from apps.reading.shared.domain.services.permission_service import PermissionService

class PermissionUseCase:
    def __init__(self, user_repo: IUserRepository, perm_repo: IPermissionRepository):
        self.user_repo = user_repo
        self.perm_repo = perm_repo
        self.permission_service = PermissionService(self.perm_repo)

    def check_management_permission(self, email: str):
        """ユーザーが権限を管理できる権限を持っているかどうかを確認します."""
        user = self.user_repo.find_by_email(email)
        if not user:
            raise PermissionError('ユーザーが見つかりませんでした.')
        if not self.permission_service.has_permission(user, 'permission_manage'):
            raise PermissionError('この操作には権限管理権限が必要です.')

    def get_all_permissions(self) -> Dict[str, List[Dict]]:
        """すべての権限をカテゴリ別にグループ化して返します."""
        permissions = self.perm_repo.find_all()
        result = {}
        for permission in permissions:
            category = permission.category or 'general'
            if category not in result:
                result[category] = []
            result[category].append(permission.to_dict())
        return result

    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """特定のユーザーの権限情報を返します."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"ID {user_id}のユーザーを見つけることができませんでした.")
        
        permissions_by_category = self.permission_service.get_permissions_by_category(user)
        return {
            'user_id': user.id,
            'email': user.email,
            'is_admin': user.is_admin,
            'is_superuser': user.is_superuser,
            'permissions': permissions_by_category
        }

    def update_user_permissions(self, current_user_email: str, target_user_id: int, permission_codes: List[str]):
        """사용자의 권한을 업데이트합니다."""
        current_user = self.user_repo.find_by_email(current_user_email)
        target_user = self.user_repo.find_by_id(target_user_id)

        if not current_user:
            raise PermissionError("현재 사용자 정보를 찾을 수 없습니다.")
        if not target_user:
            raise UserNotFoundError(f"ID {target_user_id}의 사용자를 찾을 수 없습니다.")
        
        # 슈퍼유저의 권한은 변경 불가
        if target_user.is_superuser:
            raise PermissionError("슈퍼유저의 권한은 변경할 수 없습니다.")

        # 시스템 권한 변경은 슈퍼유저만 가능
        system_permissions = self.perm_repo.find_by_category('system')
        system_permission_codes = [p.code for p in system_permissions]
        
        # 현재 시스템 권한 추출
        current_permissions = target_user.get_permissions()
        current_system_permissions = [p.code for p in current_permissions if p.code in system_permission_codes]
        
        # 요청된 새로운 시스템 권한 추출
        new_system_permissions = [code for code in permission_codes if code in system_permission_codes]
        
        # 시스템 권한에 변경이 있는 경우 현재 사용자가 슈퍼유저인지 확인
        if set(current_system_permissions) != set(new_system_permissions):
            if not current_user.is_superuser:
                raise PermissionError("시스템 권한 변경에는 슈퍼유저 권한이 필요합니다.")
        
        # 현재 권한 코드 목록
        current_permission_codes = [p.code for p in current_permissions]
        
        # 추가할 권한과 제거할 권한 계산
        permissions_to_add = [code for code in permission_codes if code not in current_permission_codes]
        permissions_to_remove = [code for code in current_permission_codes if code not in permission_codes]
        
        # 권한 추가
        for code in permissions_to_add:
            target_user.grant_permission(code, current_user)
            
        # 권한 제거
        for code in permissions_to_remove:
            target_user.revoke_permission(code, current_user)

    def create_permission(self, data: Dict[str, Any]) -> Permission:
        """새로운 권한을 생성합니다."""
        code = data.get('code')
        name = data.get('name')
        category = data.get('category')
        if not all([code, name, category]):
            raise ValueError("필수 필드(code, name, category)가 누락되었습니다.")

        existing = self.perm_repo.find_by_name(code)
        if existing:
            raise PermissionError(f"'{code}' 권한이 이미 존재합니다.")

        permission = Permission(
            name=name,
            description=data.get('description'),
            category=category,
            code=code
        )
        return self.perm_repo.save(permission)

    def check_user_permission(self, email: str, permission_code: str) -> bool:
        """사용자가 특정 권한을 가졌는지 확인합니다."""
        # 정규화 및 유효성 검증 (공백/빈 문자열/쉼표만 있는 입력 방어)
        normalized = permission_code.strip() if isinstance(permission_code, str) else ''
        if not normalized:
            raise ValueError("권한 코드가 지정되지 않았습니다.")
            
        user = self.user_repo.find_by_email(email)
        if not user:
            raise UserNotFoundError("사용자를 찾을 수 없습니다.")

        return self.permission_service.has_permission(user, normalized)

    def check_user_permissions_batch(self, email: str, permission_codes: List[str]) -> Dict[str, bool]:
        """여러 권한 코드를 일괄 확인합니다 (N+1 API 호출 방지)."""
        if not permission_codes:
            return {}

        # 중복 코드 제거 (순서 유지), 정규화 (trim) 및 빈 문자열/비문자열 필터링
        unique_codes = list(dict.fromkeys(
            code.strip() for code in permission_codes
            if isinstance(code, str) and code.strip()
        ))
        if not unique_codes:
            return {}

        user = self.user_repo.find_by_email(email)
        if not user:
            raise UserNotFoundError("사용자를 찾을 수 없습니다.")

        # スーパーユーザーは全権限を持つ（正規化済みコードに対して返却）
        if user.is_superuser:
            return {code: True for code in unique_codes}

        # 사용자의 권한을 한 번만 조회하여 N+1 쿼리 방지
        user_permission_names = {perm.name for perm in user.permissions.all()}

        return {
            code: code in user_permission_names
            for code in unique_codes
        }