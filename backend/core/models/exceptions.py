class UserNotFoundError(Exception):
    """ユーザーが見つからない場合の例外"""
    pass

class InvalidCredentialsError(Exception):
    """認証情報が無効な場合の例外"""
    pass

class UserAlreadyExistsError(Exception):
    """ユーザーが既に存在する場合の例外"""
    pass

class DatabaseError(Exception):
    """データベース操作に関連する一般的な例外"""
    pass

class ValidationError(Exception):
    """入力データのバリデーションに失敗した場合の例外"""
    pass

class PasswordAuthenticationError(Exception):
    """パスワード認証に失敗した場合の例外"""
    pass

class PasswordValidationError(Exception):
    """パスワードのバリデーションに失敗した場合の例外"""
    pass

class SubscriptionExpiredError(Exception):
    """サブスクリプションが期限切れの場合の例外"""
    pass

class AccountLimitExceededError(Exception):
    """アカウント作成の上限に達した場合の例外"""
    def __init__(self, limit, current):
        self.limit = limit
        self.current = current
        message = f"アカウント作成の上限に達しました。上限: {limit}, 現在: {current}"
        super().__init__(message)

class AuthorizationError(Exception):
    """認可に失敗した場合の例外"""
    pass

class PermissionError(Exception):
    """権限が不足している場合の例外"""
    pass 