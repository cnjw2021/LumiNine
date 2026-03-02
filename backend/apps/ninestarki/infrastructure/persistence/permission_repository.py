from core.database import db, read_only_session, write_session
from apps.ninestarki.domain.repositories.permission_repository_interface import IPermissionRepository
from apps.ninestarki.domain.entities.permission import Permission
from typing import List

class PermissionRepository(IPermissionRepository):
    """Permission エンティティに対するすべてのデータベースアクセスを処理します."""

    def find_by_name(self, name: str) -> Permission | None:
        """名前で権限を検索します."""
        with read_only_session() as read_session:
            return read_session.query(Permission).filter_by(name=name).first()

    def find_all(self) -> List[Permission]:
        """すべての権限を検索します."""
        with read_only_session() as read_session:
            return read_session.query(Permission).all()

    def save(self, permission: Permission) -> Permission:
        """権限を保存(追加または更新)します."""
        with write_session() as write_session_ctx:
            merged = write_session_ctx.merge(permission)
            write_session_ctx.add(merged)
            return merged
