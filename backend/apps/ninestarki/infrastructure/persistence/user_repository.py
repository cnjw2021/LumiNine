from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import func
from core.database import db, write_session
from apps.ninestarki.domain.repositories.user_repository_interface import IUserRepository
from apps.ninestarki.domain.entities.user import User

class UserRepository(IUserRepository):
    """User エンティティに対するすべてのデータベースアクセスを処理します."""

    def find_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを検索します (大文字小文字を無視)."""
        if not email:
            return None
        return User.query.filter(
            func.lower(User.email) == func.lower(email),
            User.is_deleted == False,
            User.is_active == True
        ).first()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """IDでアクティブで、削除されていないユーザーを検索します."""
        if not user_id:
            return None
        return User.query.filter_by(
            id=user_id,
            is_deleted=False,
            is_active=True
        ).first()

    def save(self, user: User) -> User:
        """ユーザーインスタンスをデータベースに保存(追加または更新)します."""
        with write_session() as write_session_ctx:
            merged_user = write_session_ctx.merge(user)
            write_session_ctx.add(merged_user)
            return merged_user

    def delete(self, user: User, deleted_by_user: User) -> Optional[User]:
        """ユーザーを論理削除(soft-delete)し、マージ済みインスタンスを返します."""
        if not user:
            return None
        user.is_active = False
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.deleted_by = deleted_by_user.id
        with write_session() as write_session_ctx:
            merged_user = write_session_ctx.merge(user)
            # addは必須ではないが、明示的にトラッキングさせる
            write_session_ctx.add(merged_user)
            return merged_user
