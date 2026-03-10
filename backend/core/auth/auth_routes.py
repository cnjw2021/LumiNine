"""Core authentication routes (login, logout, password, user info).

Sub-modules are registered via register_*_routes(auth_bp) at the bottom of this file,
keeping the single auth_bp blueprint that app.py already imports.
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
import bcrypt
from apps.reading.shared.domain.entities.user import User
from core.models.exceptions import (
    UserNotFoundError,
    PasswordAuthenticationError,
    PasswordValidationError,
)
from core.database import db
from core.utils.logger import get_logger
from core.auth.auth_utils import get_current_user
import json

from apps.reading.shared.infrastructure.persistence.user_repository import UserRepository

# TODO: Usecaseで生成するように修正する
user_repo = UserRepository()

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Core Auth Routes
# ---------------------------------------------------------------------------


@auth_bp.route('/login', methods=['POST'])
def login():
    """ログイン処理"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')

        logger.info(f"ログイン試行: {email}")

        # ユーザー認証
        user = User.query.filter_by(email=email, is_active=True, is_deleted=False).first()
        if not user:
            logger.warning(f"ログイン失敗: ユーザーが見つかりません - {email}")
            return jsonify({'message': 'メールアドレスまたはパスワードが正しくありません'}), 401

        # パスワード検証
        if not user.check_password(password):
            logger.warning(f"ログイン失敗: パスワードが一致しません - {email}")
            return jsonify({'message': 'メールアドレスまたはパスワードが正しくありません'}), 401

        # 管理者かスーパーユーザーかをログに記録
        user_type = "通常ユーザー"
        if user.is_superuser:
            user_type = "スーパーユーザー"
        elif user.is_admin:
            user_type = "管理者"
        logger.info(f"ユーザー種別: {user_type}")

        # JWTトークン生成
        additional_claims = {
            'is_admin': user.is_admin,
            'is_superuser': user.is_superuser,
            'is_subscription_active': user.is_subscription_active,
            'user_id': user.id
        }

        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email)

        # ログイン成功ログ
        logger.info(f"ユーザーがログインしました: {email} (ID: {user.id})")

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"ログイン処理中にエラーが発生しました: {str(e)}")
        return jsonify({'message': 'ログイン処理ができませんでした。しばらく経ってからもう一度お試しください。'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """ログアウト処理"""
    try:
        # クライアント側でトークンを削除する前提
        current_user = get_jwt_identity()
        logger.info(f"ユーザーがログアウトしました: {current_user}")
        return jsonify({'message': 'ログアウトしました'}), 200
    except Exception as e:
        logger.error(f"ログアウト処理中にエラーが発生しました: {str(e)}")
        return jsonify({'message': 'ログアウト処理中にエラーが発生しました'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """ユーザーのパスワードを変更するエンドポイント"""
    try:
        # リクエストデータの取得
        data = request.get_json()
        if not data:
            return Response(
                json.dumps({'error': 'リクエストデータが不正です'}),
                status=400,
                mimetype='application/json'
            )

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # 入力検証
        if not current_password or not new_password:
            return Response(
                json.dumps({'error': '現在のパスワードと新しいパスワードを入力してください'}),
                status=400,
                mimetype='application/json'
            )

        # 現在のユーザーを取得
        try:
            user = get_current_user()
        except UserNotFoundError as e:
            logger.error(f"ユーザー取得失敗: {str(e)}")
            return Response(
                json.dumps({'error': 'ユーザーが見つかりません'}),
                status=404,
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"ユーザー取得中に予期せぬエラー: {str(e)}")
            return Response(
                json.dumps({'error': 'ユーザー情報の取得に失敗しました'}),
                status=500,
                mimetype='application/json'
            )

        # 現在のパスワードを検証
        try:
            if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
                return Response(
                    json.dumps({'error': '現在のパスワードが正しくありません'}),
                    status=400,
                    mimetype='application/json'
                )
        except PasswordAuthenticationError as e:
            logger.error(f"パスワード認証エラー: {str(e)}")
            return Response(
                json.dumps({'error': '現在のパスワードが正しくありません'}),
                status=400,
                mimetype='application/json'
            )

        # 新しいパスワードの検証と設定
        try:
            user.password = new_password
            user_repo.save(user)
            return Response(
                json.dumps({'message': 'パスワードが正常に変更されました'}),
                status=200,
                mimetype='application/json'
            )
        except PasswordValidationError as e:
            logger.error(f"パスワード検証エラー: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=400,
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"パスワード変更中にエラーが発生: {str(e)}")
            return Response(
                json.dumps({'error': 'パスワード変更中にエラーが発生しました'}),
                status=500,
                mimetype='application/json'
            )

    except Exception as e:
        logger.error(f"パスワード変更処理中に予期せぬエラーが発生: {str(e)}")
        return Response(
            json.dumps({'error': 'サーバーエラーが発生しました'}),
            status=500,
            mimetype='application/json'
        )


# ---------------------------------------------------------------------------
# User Info Routes
# ---------------------------------------------------------------------------


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """現在のユーザー情報を取得するエンドポイント"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            logger.error(f"ユーザーが見つかりません: {current_user_email}")
            return jsonify({'error': 'ユーザーが見つかりません'}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.error(f"ユーザー情報取得中にエラーが発生しました: {str(e)}")
        return jsonify({'error': 'ユーザー情報取得中にエラーが発生しました'}), 500


@auth_bp.route('/admin-status', methods=['GET'])
@jwt_required()
def admin_status():
    """ユーザーの管理者ステータスを返すエンドポイント"""
    try:
        # 現在のユーザー情報を取得
        identity = get_jwt_identity()

        # ユーザー情報を取得（IDまたはメールアドレスで検索）
        user = None
        if isinstance(identity, int) or (isinstance(identity, str) and identity.isdigit()):
            user_id = int(identity)
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
        else:
            user = User.query.filter_by(email=identity, is_deleted=False).first()

        if not user:
            logger.error(f"admin-status: ユーザーが見つかりません: {identity}")
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )

        return Response(
            json.dumps({
                "is_admin": user.is_admin,
                "is_superuser": user.is_superuser
            }),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in admin_status: {str(e)}")
        return Response(
            json.dumps({"error": "ステータス取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )


# ---------------------------------------------------------------------------
# Sub-module Registration (deferred to create_auth_bp factory)
# ---------------------------------------------------------------------------

from core.auth.debug_routes import register_debug_routes
from core.auth.token_routes import register_token_routes
from core.auth.admin_user_routes import register_admin_user_routes
from core.auth.admin_system_routes import register_admin_system_routes

_routes_registered = False


def create_auth_bp(admin_user_use_case=None):
    """認証関連のBlueprint作成関数

    すべてのサブモジュールのルート登録をここで行います。
    app.py から register_blueprint() の前に呼び出してください。

    Args:
        admin_user_use_case: DI container에서 주입받는 AdminUserUseCase.
            None이면 직접 인스턴스를 생성합니다 (하위 호환성).
    """
    global _routes_registered
    if _routes_registered:
        return auth_bp

    if admin_user_use_case is None:
        from apps.reading.shared.infrastructure.persistence.user_repository import UserRepository
        from apps.reading.shared.use_cases.admin_user_use_case import AdminUserUseCase
        admin_user_use_case = AdminUserUseCase(UserRepository())

    register_debug_routes(auth_bp)
    register_token_routes(auth_bp)
    register_admin_system_routes(auth_bp)
    register_admin_user_routes(auth_bp, admin_user_use_case)

    _routes_registered = True
    return auth_bp
