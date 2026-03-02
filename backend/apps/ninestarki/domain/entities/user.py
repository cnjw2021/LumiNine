import datetime
from datetime import datetime, timezone
import bcrypt
from sqlalchemy.orm import validates, relationship
from sqlalchemy import func
from core.database import db
from core.utils.logger import get_logger
from apps.ninestarki.domain.entities.user_permission import UserPermission
from apps.ninestarki.domain.entities.permission import Permission

logger = get_logger(__name__)

class User(db.Model):
    """User エンティティと核心的なビジネスロジックを定義します."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    account_limit = db.Column(db.Integer, default=0)

    permissions = db.relationship(
        Permission, secondary=UserPermission.__table__,
        backref=db.backref('users', lazy='dynamic'), lazy='dynamic'
    )
    
    created_accounts = db.relationship(
        'User', foreign_keys=[created_by],
        backref=db.backref('creator', foreign_keys=[created_by], remote_side=[id]),
        lazy='dynamic'
    )

    @validates('password')
    def hash_password(self, key, password):
        """パスワードが設定されるたびに自動的にハッシュ化します."""
        if not password:
            raise ValueError("Password cannot be empty.")
        if isinstance(password, str) and password.startswith('$2b$'):
            return password
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_password(self, password_to_check: str) -> bool:
        """入力されたパスワードが保存されたハッシュと一致するかどうかを確認します."""
        if not self.password or not password_to_check:
            return False
        return bcrypt.checkpw(password_to_check.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self):
        """エンティティを辞書に変換します."""
        return {
            'id': self.id, 'name': self.name, 'email': self.email,
            'is_active': self.is_active, 'is_admin': self.is_admin,
            'is_superuser': self.is_superuser,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'is_subscription_active': self.is_subscription_active
        }

    # サブスクリプション有効期限のチェック
    @property
    def is_subscription_active(self):
        if self.is_superuser or self.is_admin:
            return True
        
        now = datetime.now(timezone.utc)
        
        # サブスクリプション開始日がNoneの場合は無効
        if not self.subscription_start:
            return False
        
        # タイムゾーン情報を追加してから比較
        start_date = self.subscription_start
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
            
        # サブスクリプション開始前の場合は無効
        if start_date > now:
            return False
            
        # サブスクリプション終了日がNoneの場合は永続的に有効
        if not self.subscription_end:
            return True
            
        # タイムゾーン情報を追加してから比較
        end_date = self.subscription_end
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
            
        # 現在日時がサブスクリプション期間内かチェック
        return now <= end_date

    # アカウント作成制限チェック
    def can_create_more_users(self):
        """ユーザーが追加アカウントを作成できるかどうかをチェック"""
        # スーパーユーザーは制限なし
        if self.is_superuser:
            return True
            
        # 管理者でない場合は作成不可
        if not self.is_admin:
            return False
            
        # アカウント制限が0の場合は制限なし
        limit = self.get_account_limit()
        if limit == 0:
            return True
            
        # 作成済みのアカウント数をカウント
        active_accounts = self.created_accounts.filter_by(is_deleted=False).count()
        return active_accounts < limit
        
    # アカウント制限の取得
    def get_account_limit(self):
        """ユーザーが作成できるアカウント数の上限を取得"""
        # スーパーユーザーは制限なし
        if self.is_superuser:
            return 0  # 0は無制限を意味する
            
        # このユーザー自身の制限を返す
        return self.account_limit
        
    # 残りのアカウント数を取得
    @property
    def remaining_accounts(self):
        """残り作成可能なアカウント数を取得"""
        # 無制限の場合
        if self.is_superuser or self.get_account_limit() == 0:
            return -1  # -1は無制限を意味する
            
        # 作成済みアカウント数を取得
        active_accounts = self.created_accounts.filter_by(is_deleted=False).count()
        limit = self.get_account_limit()
        
        return max(0, limit - active_accounts)
        
    # ユーザー管理権限のチェック
    def can_manage_user(self, target_user):
        """特定のユーザーを管理（更新・削除）できるかどうかをチェック"""
        # スーパーユーザーは他のスーパーユーザー以外なら管理可能
        if self.is_superuser:
            return not target_user.is_superuser or self.id == target_user.id
            
        # 管理者は自分が作成したユーザーと自分自身のみ管理可能
        if self.is_admin:
            return target_user.created_by == self.id or self.id == target_user.id
            
        # 一般ユーザーは自分自身のみ管理可能
        return self.id == target_user.id 