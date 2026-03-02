from apps.ninestarki.domain.entities.user import User
from apps.ninestarki.domain.repositories.permission_repository_interface import IPermissionRepository

class PermissionService:
    """
    ユーザーの権限確認と関連するビジネスロジックを処理するサービス
    """
    def __init__(self, perm_repo: IPermissionRepository):
        self.perm_repo = perm_repo

    def has_permission(self, user: User, permission_code: str) -> bool:
        """
        ユーザーが特定の権限を持っているかどうかを確認するロジック全体
        """
        # 1. スーパーユーザーはすべての権限を持つ
        if user.is_superuser:
            return True
        
        # 2. 確認しようとしている権限コードがない場合はパスする
        if not permission_code:
            return True

        # 3. カンマ(,)で区切られた複数の権限コードが入力された場合,
        #    そのうちの1つでも持っていればTrueを返す
        if ',' in permission_code:
            permission_list = [p.strip() for p in permission_code.split(',')]
            return any(self.has_permission(user, p) for p in permission_list)

        # 4. 単一の権限を確認する
        # PermissionRepositoryを通じて、権限がDBに存在するかどうかを最初に確認する
        permission = self.perm_repo.find_by_name(permission_code)
        if not permission:
            return False
            
        # 5. SQLAlchemyのrelationshipを通じて、ユーザーがその権限を持っているかどうかを最終的に確認する
        # user.permissionsはクエリオブジェクトなので、.all()を通じてリストとして取得し、比較する
        return permission in user.permissions.all()

    def get_permissions_by_category(self, user: User) -> dict:
        """ユーザーが持っている権限をカテゴリ別にグルーピングする"""
        result = {}
        if user.is_superuser:
            return result
            
        user_permissions = user.permissions.all()
        
        for perm in user_permissions:
            category = perm.category or 'general'
            if category not in result:
                result[category] = []
            result[category].append({
                'id': perm.id,
                'name': perm.name,
                'description': perm.description
            })
        return result