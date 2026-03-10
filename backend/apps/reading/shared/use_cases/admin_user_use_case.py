"""Admin user management use case.

Encapsulates all business logic for admin user operations:
authorization checks, validation, user CRUD, and account limit management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from apps.reading.shared.domain.entities.user import User
from apps.reading.shared.domain.repositories.user_repository_interface import IUserRepository
from core.models.exceptions import (
    UserNotFoundError,
    PermissionError,
    AccountLimitExceededError,
    ValidationError,
    UserAlreadyExistsError,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)


class AdminUserUseCase:
    """관리자 유저 CRUD 비즈니스 로직을 캡슐화합니다.

    모든 메서드는 인가, 검증, 비즈니스 규칙을 담당합니다.
    라우트 핸들러는 요청 파싱 → UseCase 호출 → 응답 포맷팅만 수행합니다.
    """

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    # ─── Authorization Helpers ─────────────────────────────────

    def _require_admin(self, current_user: User) -> None:
        """관리자 권한 확인. 실패시 PermissionError."""
        if not current_user.is_admin:
            raise PermissionError("管理者権限が必要です")

    def _require_superuser(self, current_user: User) -> None:
        """슈퍼유저 권한 확인. 실패시 PermissionError."""
        if not current_user.is_superuser:
            raise PermissionError("この操作にはスーパーユーザー権限が必要です")

    def _require_can_manage(self, current_user: User, target_user: User) -> None:
        """대상 유저 관리 권한 확인. 실패시 PermissionError."""
        if not current_user.can_manage_user(target_user):
            raise PermissionError("このユーザーを管理する権限がありません")

    # ─── Queries ───────────────────────────────────────────────

    def list_users(self, current_user: User, show_deleted: bool = False) -> Dict[str, Any]:
        """관리자가 유저 목록을 조회합니다.

        Returns: {"users": [...], "total_count": int, "includes_deleted": bool}
        Raises: PermissionError
        """
        self._require_admin(current_user)

        # スーパーユーザーを除外してユーザーを取得
        query = User.query.filter_by(is_superuser=False)
        if not show_deleted:
            query = query.filter_by(is_deleted=False)

        users = query.all()
        user_list = []

        for user in users:
            user_data = user.to_dict()
            if user.is_deleted and user.deleted_by:
                deleted_by_user = self.user_repo.find_by_id(user.deleted_by)
                if deleted_by_user:
                    user_data['deleted_by_email'] = deleted_by_user.email
                    user_data['deleted_at'] = (
                        user.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if user.deleted_at else None
                    )
            user_list.append(user_data)

        return {
            "users": user_list,
            "total_count": len(user_list),
            "includes_deleted": show_deleted,
        }

    # ─── Commands ──────────────────────────────────────────────

    def create_user(self, current_user: User, data: Dict[str, Any]) -> Dict[str, Any]:
        """관리자가 새 유저를 생성합니다.

        Returns: {"message": str, "user": {...}, "remaining_accounts": int}
        Raises: PermissionError, AccountLimitExceededError, ValidationError, UserAlreadyExistsError
        """
        self._require_admin(current_user)

        # アカウント作成制限のチェック
        if not current_user.can_create_more_users():
            raise AccountLimitExceededError(
                current_user.get_account_limit(),
                len(current_user.created_accounts)
            )

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)
        subscription_start = data.get('subscription_start')
        subscription_end = data.get('subscription_end')

        # 入力検証
        if not name or not email or not password:
            raise ValidationError("名前、メールアドレス、パスワードは必須です")

        if not subscription_start or not subscription_end:
            raise ValidationError("利用開始日と終了日は必須です")

        # メールアドレスの重複チェック
        if User.query.filter_by(email=email, is_deleted=False).first():
            raise UserAlreadyExistsError("このメールアドレスは既に登録されています")

        # 日付パース
        try:
            start_date = datetime.strptime(subscription_start.replace('/', '-'), '%Y-%m-%d')
            end_date = datetime.strptime(subscription_end.replace('/', '-'), '%Y-%m-%d')
        except ValueError:
            raise ValidationError("日付形式が正しくありません")

        if end_date <= start_date:
            raise ValidationError("利用終了日は開始日より後である必要があります")

        # 管理者権限の設定チェック
        if is_admin and not current_user.is_superuser:
            raise PermissionError("管理者権限の設定にはスーパーユーザー権限が必要です")

        # ユーザー作成
        new_user = User(
            name=name,
            email=email,
            password=password,
            is_admin=is_admin,
            subscription_start=start_date,
            subscription_end=end_date,
            created_by=current_user.id,
        )
        saved_user = self.user_repo.save(new_user)

        logger.info(f"New user created by admin: {email}")
        return {
            "message": "ユーザーを作成しました",
            "user": {
                "id": saved_user.id,
                "email": saved_user.email,
                "is_admin": saved_user.is_admin,
                "subscription_start": saved_user.subscription_start.isoformat(),
                "subscription_end": saved_user.subscription_end.isoformat(),
                "is_subscription_active": saved_user.is_subscription_active,
            },
            "remaining_accounts": current_user.remaining_accounts,
        }

    def delete_user(self, current_user: User, user_id: int) -> Dict[str, Any]:
        """관리자가 유저를 논리 삭제합니다.

        Returns: {"message": str, "deleted_user": {...}}
        Raises: PermissionError, UserNotFoundError
        """
        self._require_admin(current_user)

        target_user = self.user_repo.find_by_id(user_id)
        if not target_user:
            raise UserNotFoundError(f"ID {user_id}")

        if target_user.is_superuser:
            raise PermissionError("スーパーユーザーは削除できません")

        self._require_can_manage(current_user, target_user)

        deleted_user = self.user_repo.delete(target_user, current_user)
        logger.info(f"User {deleted_user.email} logically deleted by admin: {current_user.email}")

        return {
            "message": "ユーザーを削除しました",
            "deleted_user": {
                "email": deleted_user.email,
                "deleted_at": (
                    deleted_user.deleted_at.strftime('%Y-%m-%d %H:%M:%S')
                    if deleted_user.deleted_at else None
                ),
                "deleted_by": current_user.email,
            },
        }

    def update_user(self, current_user: User, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """관리자가 유저 정보를 수정합니다.

        Returns: {"message": str, "user": {...}}
        Raises: PermissionError, UserNotFoundError, ValidationError
        """
        self._require_admin(current_user)

        target_user = User.query.get(user_id)
        if not target_user:
            raise UserNotFoundError(f"ID {user_id}")

        self._require_can_manage(current_user, target_user)

        # スーパーユーザー以外は管理者権限の変更不可
        if not current_user.is_superuser and 'is_admin' in data:
            raise PermissionError("管理者権限の変更はスーパーユーザーのみ可能です")

        # フィールドの更新
        if 'name' in data:
            target_user.name = data['name']
        if 'email' in data:
            target_user.email = data['email']
        if 'is_admin' in data and current_user.is_superuser:
            target_user.is_admin = data['is_admin']
        if 'subscription_start' in data:
            try:
                target_user.subscription_start = datetime.strptime(
                    data['subscription_start'].replace('/', '-'), '%Y-%m-%d'
                )
            except ValueError:
                raise ValidationError("日付形式が正しくありません")
        if 'subscription_end' in data:
            try:
                target_user.subscription_end = datetime.strptime(
                    data['subscription_end'].replace('/', '-'), '%Y-%m-%d'
                )
            except ValueError:
                raise ValidationError("日付形式が正しくありません")
        if 'password' in data:
            target_user.password = data['password']

        self.user_repo.save(target_user)
        logger.info(f"User updated by admin: {target_user.email}")

        return {
            "message": "ユーザー情報を更新しました",
            "user": target_user.to_dict(),
        }

    def update_account_limit(
        self, current_user: User, user_id: int, new_limit: int
    ) -> Dict[str, Any]:
        """슈퍼유저가 관리자의 계정 제한을 변경합니다.

        Returns: {"message": str, "user": {...}}
        Raises: PermissionError, UserNotFoundError, ValidationError
        """
        self._require_superuser(current_user)

        target_user = User.query.get(user_id)
        if not target_user:
            raise UserNotFoundError(f"ID {user_id}")

        if not target_user.is_admin:
            raise ValidationError("管理者以外のアカウント制限数は変更できません")

        if not isinstance(new_limit, int) or new_limit < 0:
            raise ValidationError("有効なアカウント制限数を指定してください")

        # AdminAccountLimit テーブルを使用
        from core.models.admin_account_limit import AdminAccountLimit
        limit_info = AdminAccountLimit.query.filter_by(admin_id=target_user.id).first()
        if limit_info:
            limit_info.account_limit = new_limit
            limit_info.updated_by = current_user.id
        else:
            limit_info = AdminAccountLimit(
                admin_id=target_user.id,
                account_limit=new_limit,
                updated_by=current_user.id,
            )
            from core.database import db
            db.session.add(limit_info)
            db.session.commit()

        logger.info(f"Account limit updated for admin {target_user.email}: {new_limit}")
        return {
            "message": "アカウント制限数を更新しました",
            "user": {
                "id": target_user.id,
                "email": target_user.email,
                "account_limit": target_user.get_account_limit(),
                "remaining_accounts": target_user.remaining_accounts,
            },
        }
