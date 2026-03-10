"""Token lifecycle hooks for the auth blueprint."""

from flask import request
from flask_jwt_extended import (
    create_access_token, verify_jwt_in_request, get_jwt_identity
)
from apps.reading.shared.domain.entities.user import User
from core.utils.logger import get_logger
from datetime import timedelta

logger = get_logger(__name__)


def register_token_routes(bp):
    """Register token lifecycle hooks (before/after request) on the given blueprint."""

    @bp.after_request
    def add_new_token_header(response):
        """レスポンスヘッダーに新しいトークンを追加"""
        try:
            # オプションリクエストの場合はスキップ
            if request.method == 'OPTIONS':
                return response

            # JWTトークンの存在確認（オプショナル）
            try:
                verify_jwt_in_request(optional=True)

                # トークンが存在する場合のみユーザー情報を取得
                current_user_email = get_jwt_identity()
                if current_user_email:
                    # メールアドレスでユーザーを検索
                    current_user = User.query.filter_by(email=current_user_email).first()
                    if current_user:
                        # 新しいトークンを1時間の有効期限で生成
                        additional_claims = {
                            'is_admin': current_user.is_admin,
                            'is_superuser': current_user.is_superuser,
                            'is_subscription_active': current_user.is_subscription_active
                        }
                        expires_delta = timedelta(hours=1)
                        new_token = create_access_token(
                            identity=current_user.email,
                            additional_claims=additional_claims,
                            expires_delta=expires_delta
                        )
                        response.headers['X-New-Token'] = new_token
            except Exception:
                # トークン検証エラーは無視（ログアウト時など）
                pass
        except Exception as e:
            logger.error(f"Error in add_new_token_header: {str(e)}")
        return response

    @bp.before_request
    def refresh_token_expiry():
        try:
            # トークン検証エラーは無視
            try:
                verify_jwt_in_request(optional=True)
            except Exception:
                # トークンがない場合や無効な場合は無視
                pass
        except Exception as e:
            # その他のエラーのみログに記録
            logger.error(f"Error in refresh_token_expiry: {str(e)}")
