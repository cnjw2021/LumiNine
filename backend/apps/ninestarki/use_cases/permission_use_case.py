from typing import List, Dict, Any
from apps.ninestarki.domain.entities.user import User
from apps.ninestarki.domain.entities.permission import Permission
from apps.ninestarki.domain.repositories.user_repository_interface import IUserRepository
from apps.ninestarki.domain.repositories.permission_repository_interface import IPermissionRepository
from core.models.exceptions import UserNotFoundError, PermissionError
from apps.ninestarki.domain.services.permission_service import PermissionService

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

    def update_user_permissions(self, current_user_email: str, target_user_id: int, permission_names: List[str]):
        """ユーザーの権限を更新します."""
        current_user = self.user_repo.find_by_email(current_user_email)
        target_user = self.user_repo.find_by_id(target_user_id)

        if not target_user:
            raise UserNotFoundError(f"ID {target_user_id}のユーザーを見つけることができませんでした.")
        if target_user.is_superuser:
            raise PermissionError("スーパーユーザーの権限は変更できません.")

        user = self.user_repo.find_by_id(user_id)
        
        # スーパーユーザーの権限は変更不可
        if user.is_superuser:
            return jsonify({'error': 'スーパーユーザーの権限は変更できません'}), 400
            
        current_user_email = get_jwt_identity()
        current_user = self.user_repo.find_by_email(current_user_email)

        # システム権限の変更はスーパーユーザーのみ可能
        system_permissions = self.perm_repo.find_by_category('system')
        system_permission_codes = [p.code for p in system_permissions]
        
        # 現在のシステム権限を取得
        current_permissions = user.get_permissions()
        current_system_permissions = [p.code for p in current_permissions if p.code in system_permission_codes]
        
        # 更新後のシステム権限を取得
        new_system_permissions = [code for code in permission_codes if code in system_permission_codes]
        
        # システム権限に変更がある場合はスーパーユーザーチェック
        if set(current_system_permissions) != set(new_system_permissions):
            if not current_user.is_superuser:
                return jsonify({
                    'error': 'システム権限の変更にはスーパーユーザー権限が必要です',
                    'code': 'permission_denied'
                }), 403
        
        # 現在の権限を取得
        current_permission_codes = [p.code for p in current_permissions]
        
        # 追加する権限
        permissions_to_add = [code for code in permission_codes if code not in current_permission_codes]
        
        # 削除する権限
        permissions_to_remove = [code for code in current_permission_codes 
                               if code not in permission_codes]
        
        # 権限を追加
        for code in permissions_to_add:
            user.grant_permission(code, current_user)
            
        # 権限を削除
        for code in permissions_to_remove:
            user.revoke_permission(code, current_user)

    def create_permission(self, data: Dict[str, Any]) -> Permission:
        """新しい権限を作成します."""
        code = data.get('code')
        name = data.get('name')
        category = data.get('category')
        if not all([code, name, category]):
            raise ValueError("必須フィールドが不足しています.")

        existing = self.perm_repo.find_by_name(code)
        if existing:
            raise PermissionError(f"'{code}' 権限はすでに存在します.")

        permission = Permission(
            name=code, # 'name' フィールドに 'code' を使用
            description=data.get('description'),
            category=category
        )
        return self.perm_repo.save(permission)

    def check_user_permission(self, email: str, permission_code: str) -> bool:
        """ユーザーが特定の権限を持っているかどうかを確認します."""
        if not permission_code:
            raise ValueError("権限コードが指定されていません.")
            
        user = self.user_repo.find_by_email(email)
        if not user:
            raise UserNotFoundError("ユーザーを見つけることができませんでした.")

        return user.has_permission(permission_code)