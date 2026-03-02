from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    verify_jwt_in_request
)
# werkzeug.securityの代わりにbcryptを使用
import bcrypt
from apps.ninestarki.domain.entities.user import User
from apps.ninestarki.domain.entities.permission import Permission
from apps.ninestarki.domain.entities.user_permission import UserPermission
from core.models.system_config import SystemConfig
from core.models.exceptions import (
    UserNotFoundError,
    PasswordAuthenticationError,
    PasswordValidationError,
    AccountLimitExceededError,
    PermissionError
)
from core.database import db
from core.utils.logger import get_logger
from datetime import datetime, timezone, timedelta
import os
from functools import wraps
from config import get_config
import json
from core.auth.auth_utils import permission_required
from core.models.admin_account_limit import AdminAccountLimit

from apps.ninestarki.infrastructure.persistence.user_repository import UserRepository

# 臨時：この Blueprintは app.py で生成されるため、Repositoryはここで直接生成します。
# TODO: Usecaseで生成するように修正する
user_repo = UserRepository()

# 日本のタイムゾーン（UTC+9）を定義
JST = timezone(timedelta(hours=+9))

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

def check_token_validity():
    """トークンの有効性をチェックするデコレータ"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                
                # スーパーユーザーと管理者は常にアクセス可能
                if claims.get('is_superuser', False) or claims.get('is_admin', False):
                    return fn(*args, **kwargs)
                
                # 一般ユーザーは利用期間内のみアクセス可能
                if not claims.get('is_subscription_active', False):
                    return Response(
                        json.dumps({
                            'error': '利用期間が終了しています',
                            'code': 'subscription_expired'
                        }),
                        status=401,
                        mimetype='application/json'
                    )

                # トークンの有効期限チェック
                exp = claims.get('exp')
                if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    return Response(
                        json.dumps({
                            'error': 'セッションの有効期限が切れています',
                            'code': 'token_expired'
                        }),
                        status=401,
                        mimetype='application/json'
                    )
                    
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Token validation error: {str(e)}")
                return Response(
                    json.dumps({
                        'error': '認証に失敗しました',
                        'code': 'authentication_failed'
                    }),
                    status=401,
                    mimetype='application/json'
                )
        return decorator
    return wrapper

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response(
                json.dumps({"error": "メールアドレスとパスワードは必須です"}),
                status=400,
                mimetype='application/json'
            )

        # メールアドレスの重複チェック
        if User.query.filter_by(email=email, is_deleted=False).first():
            return Response(
                json.dumps({"error": "このメールアドレスは既に登録されています"}),
                status=400,
                mimetype='application/json'
            )

        # ユーザー作成
        new_user = User(
            email=email,
            password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user registered: {email}")
        return Response(
            json.dumps({"message": "ユーザー登録が完了しました"}),
            status=201,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "登録中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

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

@auth_bp.route('/debug/users', methods=['GET'])
def debug_users():
    if os.environ.get('FLASK_ENV') != 'development':
        return Response(
            json.dumps({"error": "開発環境でのみ利用可能です"}),
            status=403,
            mimetype='application/json'
        )
    
    try:
        users = User.query.all()
        return Response(
            json.dumps({
                "user_count": len(users),
                "users": [{
                    "id": user.id,
                    "email": user.email,
                    "has_password": bool(user.password)
                } for user in users]
            }),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in debug_users: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/debug/db', methods=['GET'])
def debug_db():
    if os.environ.get('FLASK_ENV') != 'development':
        return Response(
            json.dumps({"error": "開発環境でのみ利用可能です"}),
            status=403,
            mimetype='application/json'
        )
    
    try:
        db.session.execute(db.text('SELECT 1'))
        return Response(
            json.dumps({"status": "データベース接続成功"}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in debug_db: {str(e)}")
        return Response(
            json.dumps({"error": f"データベース接続失敗: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/health', methods=['GET'])
def health_check():
    try:
        # 最小限のデータベース接続チェック
        db.session.execute(db.text('SELECT 1'))
        return Response(
            json.dumps({
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(
            json.dumps({
                "status": "unhealthy",
                "error": str(e)
            }),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def list_users():
    try:
        # 管理者権限チェック
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return Response(
                json.dumps({"error": "管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        # クエリパラメータから表示設定を取得
        show_deleted = request.args.get('show_deleted', 'false').lower() == 'true'

        # スーパーユーザーを除外してユーザーを取得
        query = User.query.filter_by(is_superuser=False)
        
        # 論理削除されたユーザーの表示制御
        if not show_deleted:
            query = query.filter_by(is_deleted=False)

        users = query.all()
        user_list = []
        
        for user in users:
            user_data = user.to_dict()
            if user.is_deleted and user.deleted_by:
                deleted_by_user = User.query.get(user.deleted_by)
                if deleted_by_user:
                    user_data['deleted_by_email'] = deleted_by_user.email
                    user_data['deleted_at'] = user.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if user.deleted_at else None
            user_list.append(user_data)
        
        return Response(
            json.dumps({
                "users": user_list,
                "total_count": len(user_list),
                "includes_deleted": show_deleted
            }),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in list_users: {str(e)}")
        return Response(
            json.dumps({"error": "ユーザー一覧の取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        # 管理者権限チェック
        current_user = get_current_user()
        if not current_user.is_admin:
            raise PermissionError("管理者")

        # アカウント作成制限のチェック
        try:
            if not current_user.can_create_more_users():
                raise AccountLimitExceededError(
                    current_user.get_account_limit(),
                    len(current_user.created_accounts)
                )
        except Exception as e:
            logger.error(f"アカウント制限チェックでエラー: {str(e)}, type: {type(e)}")
            raise

        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)
        subscription_start = data.get('subscription_start')
        subscription_end = data.get('subscription_end')

        if not name or not email or not password:
            return Response(
                json.dumps({"error": "名前、メールアドレス、パスワードは必須です"}),
                status=400,
                mimetype='application/json'
            )

        if not subscription_start or not subscription_end:
            return Response(
                json.dumps({"error": "利用開始日と終了日は必須です"}),
                status=400,
                mimetype='application/json'
            )

        # メールアドレスの重複チェック
        if User.query.filter_by(email=email, is_deleted=False).first():
            return Response(
                json.dumps({"error": "このメールアドレスは既に登録されています"}),
                status=400,
                mimetype='application/json'
            )

        try:
            subscription_start_date = datetime.strptime(subscription_start.replace('/', '-'), '%Y-%m-%d')
            subscription_end_date = datetime.strptime(subscription_end.replace('/', '-'), '%Y-%m-%d')
        except ValueError:
            return Response(
                json.dumps({"error": "日付形式が正しくありません"}),
                status=400,
                mimetype='application/json'
            )

        # 期間の妥当性チェック
        if subscription_end_date <= subscription_start_date:
            return Response(
                json.dumps({"error": "利用終了日は開始日より後である必要があります"}),
                status=400,
                mimetype='application/json'
            )

        # 管理者権限の設定チェック
        if is_admin and not current_user.is_superuser:
            raise PermissionError("スーパーユーザー")

        # ユーザー作成
        new_user = User(
            name=name,
            email=email,
            password=password,
            is_admin=is_admin,
            subscription_start=subscription_start_date,
            subscription_end=subscription_end_date,
            created_by=current_user.id
        )
        
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created by admin: {email}")
        return Response(
            json.dumps({
                "message": "ユーザーを作成しました",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "is_admin": new_user.is_admin,
                    "subscription_start": new_user.subscription_start.isoformat(),
                    "subscription_end": new_user.subscription_end.isoformat(),
                    "is_subscription_active": new_user.is_subscription_active
                },
                "remaining_accounts": current_user.remaining_accounts
            }),
            status=201,
            mimetype='application/json'
        )

    except PermissionError as e:
        logger.error(f"権限エラー: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=403,
            mimetype='application/json'
        )
    except AccountLimitExceededError as e:
        logger.error(f"アカウント制限エラー: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=403,
            mimetype='application/json'
        )
    except Exception as e:
        import traceback
        logger.error(f"Error in create_user: {str(e)}\nType: {type(e)}\nTraceback:\n{traceback.format_exc()}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "ユーザー作成中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        # 管理者権限チェック
        current_user = get_current_user()
        if not current_user.is_admin:
            return Response(
                json.dumps({"error": "管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        target_user = user_repo.find_by_id(user_id)
        if not target_user:
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )

        # スーパーユーザーの削除を防止
        if target_user.is_superuser:
            return Response(
                json.dumps({"error": "スーパーユーザーは削除できません"}),
                status=403,
                mimetype='application/json'
            )

        # 権限チェック
        if not current_user.can_manage_user(target_user):
            return Response(
                json.dumps({"error": "このユーザーを削除する権限がありません"}),
                status=403,
                mimetype='application/json'
            )

        # 論理削除を実行（マージ済みエンティティを受け取る）
        deleted_user = user_repo.delete(target_user, current_user)
        logger.info(f"User {deleted_user.email} logically deleted by admin: {current_user.email}")

        return Response(
            json.dumps({
                "message": "ユーザーを削除しました",
                "deleted_user": {
                    "email": deleted_user.email,
                    "deleted_at": deleted_user.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if deleted_user.deleted_at else None,
                    "deleted_by": current_user.email
                }
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "ユーザー削除中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        # 管理者権限チェック
        current_user = get_current_user()
        if not current_user.is_admin:
            return Response(
                json.dumps({"error": "管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        target_user = User.query.get(user_id)
        if not target_user:
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )

        # 権限チェック
        if not current_user.can_manage_user(target_user):
            return Response(
                json.dumps({"error": "このユーザーを編集する権限がありません"}),
                status=403,
                mimetype='application/json'
            )

        data = request.get_json()
        
        # スーパーユーザー以外は管理者権限の変更不可
        if not current_user.is_superuser and 'is_admin' in data:
            return Response(
                json.dumps({"error": "管理者権限の変更はスーパーユーザーのみ可能です"}),
                status=403,
                mimetype='application/json'
            )

        # フィールドの更新
        if 'name' in data:
            target_user.name = data['name']
        if 'email' in data:
            target_user.email = data['email']
        if 'is_admin' in data and current_user.is_superuser:
            target_user.is_admin = data['is_admin']
        if 'subscription_start' in data:
            target_user.subscription_start = datetime.strptime(data['subscription_start'].replace('/', '-'), '%Y-%m-%d')
        if 'subscription_end' in data:
            target_user.subscription_end = datetime.strptime(data['subscription_end'].replace('/', '-'), '%Y-%m-%d')
        if 'password' in data:
            target_user.password = data['password']

        db.session.commit()
        logger.info(f"User updated by admin: {target_user.email}")
        
        return Response(
            json.dumps({
                "message": "ユーザー情報を更新しました",
                "user": target_user.to_dict()
            }),
            status=200,
            mimetype='application/json'
        )

    except ValueError as e:
        return Response(
            json.dumps({"error": "日付形式が正しくありません"}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in update_user: {str(e)}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "ユーザー更新中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users/create', methods=['POST'])
@jwt_required()
def admin_create_user():
    try:
        # 管理者権限チェック
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return Response(
                json.dumps({"error": "管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)
        subscription_start = datetime.fromisoformat(data.get('subscription_start'))
        subscription_end = datetime.fromisoformat(data.get('subscription_end'))

        if not email or not password:
            return Response(
                json.dumps({"error": "メールアドレスとパスワードは必須です"}),
                status=400,
                mimetype='application/json'
            )

        # メールアドレスの重複チェック
        if User.query.filter_by(email=email, is_deleted=False).first():
            return Response(
                json.dumps({"error": "このメールアドレスは既に登録されています"}),
                status=400,
                mimetype='application/json'
            )

        # 利用期間の妥当性チェック
        if subscription_end <= subscription_start:
            return Response(
                json.dumps({"error": "利用終了日は開始日より後である必要があります"}),
                status=400,
                mimetype='application/json'
            )

        # ユーザー作成
        current_user_id = get_jwt_identity()
        new_user = User(
            email=email,
            is_admin=is_admin,
            password=password,
            subscription_start=subscription_start,
            subscription_end=subscription_end,
            created_by=current_user_id
        )
        
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created by admin: {email}")
        return Response(
            json.dumps({
                "message": "ユーザーが作成されました",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "is_admin": new_user.is_admin,
                    "subscription_start": new_user.subscription_start.isoformat(),
                    "subscription_end": new_user.subscription_end.isoformat()
                }
            }),
            status=201,
            mimetype='application/json'
        )

    except ValueError as e:
        return Response(
            json.dumps({"error": "日付形式が正しくありません"}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error in admin_create_user: {str(e)}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "ユーザー作成中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users/<int:user_id>/account-limit', methods=['PUT'])
@jwt_required()
def update_account_limit(user_id):
    try:
        # 権限チェック（スーパーユーザーのみ）
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        if not current_user or not current_user.is_superuser:
            return Response(
                json.dumps({"error": "この操作にはスーパーユーザー権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        target_user = User.query.get(user_id)
        if not target_user:
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )

        if not target_user.is_admin:
            return Response(
                json.dumps({"error": "管理者以外のアカウント制限数は変更できません"}),
                status=400,
                mimetype='application/json'
            )

        data = request.get_json()
        new_limit = data.get('account_limit')

        if not isinstance(new_limit, int) or new_limit < 0:
            return Response(
                json.dumps({"error": "有効なアカウント制限数を指定してください"}),
                status=400,
                mimetype='application/json'
            )

        # 既存の制限情報を取得または新規作成
        limit_info = AdminAccountLimit.query.filter_by(admin_id=target_user.id).first()
        if limit_info:
            limit_info.account_limit = new_limit
            limit_info.updated_by = current_user.id
        else:
            limit_info = AdminAccountLimit(
                admin_id=target_user.id,
                account_limit=new_limit,
                updated_by=current_user.id
            )
            db.session.add(limit_info)

        db.session.commit()

        logger.info(f"Account limit updated for admin {target_user.email}: {new_limit}")
        return Response(
            json.dumps({
                "message": "アカウント制限数を更新しました",
                "user": {
                    "id": target_user.id,
                    "email": target_user.email,
                    "account_limit": target_user.get_account_limit(),
                    "remaining_accounts": target_user.remaining_accounts
                }
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in update_account_limit: {str(e)}")
        db.session.rollback()
        return Response(
            json.dumps({"error": "アカウント制限数の更新中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/users/<int:user_id>/account-info', methods=['GET'])
@jwt_required()
def get_account_info(user_id):
    try:
        # 権限チェック（管理者またはスーパーユーザー）
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        if not current_user or (not current_user.is_admin and not current_user.is_superuser):
            return Response(
                json.dumps({"error": "管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        target_user = User.query.get(user_id)
        if not target_user:
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )

        # スーパーユーザーは全てのユーザーを管理可能
        if not current_user.is_superuser:
            if not current_user.can_manage_user(target_user):
                return Response(
                    json.dumps({"error": "このユーザーの情報を閲覧する権限がありません"}),
                    status=403,
                    mimetype='application/json'
                )

        return Response(
            json.dumps({
                "user": {
                    "id": target_user.id,
                    "email": target_user.email,
                    "is_admin": target_user.is_admin,
                    "account_limit": target_user.get_account_limit(),
                    "remaining_accounts": target_user.remaining_accounts,
                    "created_accounts_count": len(target_user.created_accounts)
                }
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in get_account_info: {str(e)}")
        return Response(
            json.dumps({"error": "アカウント情報の取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """リフレッシュトークンを使用して新しいアクセストークンを取得"""
    try:
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return Response(
            json.dumps({
                'access_token': new_access_token
            }),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"トークンリフレッシュ中にエラーが発生しました: {str(e)}")
        return Response(
            json.dumps({'message': 'トークンリフレッシュ中にエラーが発生しました'}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.after_request
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
                    expires_delta = timedelta(hours=1)  # 有効期限を1時間に設定
                    new_token = create_access_token(
                        identity=current_user.email,
                        additional_claims=additional_claims,
                        expires_delta=expires_delta
                    )
                    response.headers['X-New-Token'] = new_token
        except Exception as e:
            # トークン検証エラーは無視（ログアウト時など）
            pass
    except Exception as e:
        logger.error(f"Error in add_new_token_header: {str(e)}")
    return response

@auth_bp.before_request
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

@auth_bp.route('/verify', methods=['GET'])
@check_token_validity()
def verify_token():
    """トークンの有効性を確認するエンドポイント"""
    return Response(
        json.dumps({
            'status': 'valid',
            'message': 'トークンは有効です'
        }),
        status=200,
        mimetype='application/json'
    )

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
            # get_current_user関数を使用してユーザーを取得
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

def get_current_user():
    """現在のユーザーを取得"""
    try:
        logger.info("get_current_user関数が呼び出されました")
        current_user_email = get_jwt_identity()
        logger.info(f"JWT identity: {current_user_email}, 型: {type(current_user_email)}")
        
        # メールアドレスでユーザーを検索
        logger.info(f"ユーザー検索: email={current_user_email}")
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            logger.error(f"ユーザーが見つかりません: {current_user_email}")
            raise UserNotFoundError(current_user_email)
            
        logger.info(f"ユーザーが見つかりました: ID={user.id}, email={user.email}, is_admin={user.is_admin}, is_superuser={user.is_superuser}")
        return user
    except Exception as e:
        logger.error(f"get_current_user内でエラーが発生: {str(e)}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        raise

@auth_bp.route('/admin-status', methods=['GET'])
@jwt_required()
def admin_status():
    """
    ユーザーの管理者ステータスを返すエンドポイント
    """
    try:
        logger.info("admin-statusエンドポイントが呼び出されました")
        
        # 現在のユーザー情報を取得
        identity = get_jwt_identity()
        logger.info(f"admin-status: JWT identity: {identity}, type: {type(identity)}")
        
        # JWTクレームを取得
        claims = get_jwt()
        logger.info(f"admin-status: JWT claims: {claims}")
        
        # ユーザー情報を取得（IDまたはメールアドレスで検索）
        user = None
        if isinstance(identity, int) or (isinstance(identity, str) and identity.isdigit()):
            # IDで検索
            user_id = int(identity)
            logger.info(f"admin-status: ユーザーIDで検索: {user_id}")
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            logger.info(f"admin-status: ユーザーIDで検索結果: {user is not None}")
        else:
            # メールアドレスで検索
            logger.info(f"admin-status: メールアドレスで検索: {identity}")
            user = User.query.filter_by(email=identity, is_deleted=False).first()
            logger.info(f"admin-status: メールアドレスで検索結果: {user is not None}")
        
        if not user:
            logger.error(f"admin-status: ユーザーが見つかりません: {identity}")
            return Response(
                json.dumps({"error": "ユーザーが見つかりません"}),
                status=404,
                mimetype='application/json'
            )
        
        # 管理者ステータスを返す
        logger.info(f"admin-status: ユーザー {user.email} のステータス - admin: {user.is_admin}, superuser: {user.is_superuser}")
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
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return Response(
            json.dumps({"error": "ステータス取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/system-stats', methods=['GET'])
@jwt_required()
def get_system_stats():
    """システム全体の統計情報を取得するエンドポイント"""
    try:
        # 管理者またはスーパーユーザー権限チェック
        current_user = get_current_user()
        if not current_user.is_admin and not current_user.is_superuser:
            return Response(
                json.dumps({"error": "この操作には管理者権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        # 有効なユーザー数をカウント（削除されていない、かつサブスクリプションが有効なユーザー）
        from datetime import datetime, timezone, timedelta
        # JSTタイムゾーンの定義
        JST = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(JST).date()
        
        # 削除されていないユーザーを取得
        non_deleted_users = User.query.filter_by(is_deleted=False).all()
        
        # 削除されたユーザー数を取得
        deleted_users_count = User.query.filter_by(is_deleted=True).count()
        
        # サブスクリプションが有効なユーザーをカウント
        active_users_count = 0
        for user in non_deleted_users:
            if user.subscription_start and user.subscription_end:
                start_date = user.subscription_start.date() if user.subscription_start.tzinfo else user.subscription_start.replace(tzinfo=JST).date()
                end_date = user.subscription_end.date() if user.subscription_end.tzinfo else user.subscription_end.replace(tzinfo=JST).date()
                if start_date <= now <= end_date:
                    active_users_count += 1
        
        # アカウント制限数を取得
        config = get_config()
        account_limit = config.get_account_limit()
        
        return Response(
            json.dumps({
                "total_active_users": active_users_count,
                "deleted_users_count": deleted_users_count,
                "account_limit": account_limit,
                "remaining_capacity": max(0, account_limit - active_users_count)
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in get_system_stats: {str(e)}")
        return Response(
            json.dumps({"error": "システム統計情報の取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/account-limit', methods=['PUT'])
@jwt_required()
def update_system_account_limit():
    """アカウント制限数を更新するエンドポイント"""
    try:
        # スーパーユーザー権限チェック
        current_user = get_current_user()
        if not current_user.is_superuser:
            return Response(
                json.dumps({"error": "この操作にはスーパーユーザー権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        data = request.get_json()
        new_limit = data.get('account_limit')

        if not isinstance(new_limit, int) or new_limit < 0:
            return Response(
                json.dumps({"error": "有効なアカウント制限数を指定してください"}),
                status=400,
                mimetype='application/json'
            )

        # 現在のアクティブユーザー数を取得（削除されていない、かつサブスクリプションが有効なユーザー）
        from datetime import datetime, timezone, timedelta
        # JSTタイムゾーンの定義
        JST = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(JST).date()
        
        # 削除されていないユーザーを取得
        non_deleted_users = User.query.filter_by(is_deleted=False).all()
        
        # サブスクリプションが有効なユーザーをカウント
        active_users_count = 0
        for user in non_deleted_users:
            if user.subscription_start and user.subscription_end:
                start_date = user.subscription_start.date() if user.subscription_start.tzinfo else user.subscription_start.replace(tzinfo=JST).date()
                end_date = user.subscription_end.date() if user.subscription_end.tzinfo else user.subscription_end.replace(tzinfo=JST).date()
                if start_date <= now <= end_date:
                    active_users_count += 1
        
        # 新しい制限が現在のユーザー数より少ない場合はエラー
        if new_limit < active_users_count:
            return Response(
                json.dumps({
                    "error": f"新しい制限数は現在のアクティブユーザー数（{active_users_count}）以上である必要があります"
                }),
                status=400,
                mimetype='application/json'
            )

        # SystemConfigテーブルに設定を保存
        SystemConfig.set_value(
            key='ACCOUNT_LIMIT',
            value=new_limit,
            description='アカウント制限数（システム全体のユーザー制限数および管理者のデフォルト制限数）',
            updated_by=current_user.id
        )

        logger.info(f"Account limit updated by {current_user.email}: {new_limit}")
        return Response(
            json.dumps({
                "message": "アカウント制限数を更新しました",
                "account_limit": new_limit,
                "total_active_users": active_users_count,
                "remaining_capacity": max(0, new_limit - active_users_count)
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in update_system_account_limit: {str(e)}")
        return Response(
            json.dumps({"error": "アカウント制限数の更新中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/default-account-limit', methods=['GET'])
@jwt_required()
def get_default_account_limit():
    """デフォルトのアカウント制限数を取得するエンドポイント"""
    try:
        # スーパーユーザー権限チェック
        current_user = get_current_user()
        if not current_user.is_superuser:
            return Response(
                json.dumps({"error": "この操作にはスーパーユーザー権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        # SystemConfigからアカウント制限値を取得
        account_limit = SystemConfig.get_by_key('ACCOUNT_LIMIT')
        
        # データベースに設定がない場合は環境変数から取得
        if account_limit is None:
            config = get_config()
            account_limit = config.ACCOUNT_LIMIT
            
            # 初期値をデータベースに保存
            SystemConfig.set_value(
                key='ACCOUNT_LIMIT',
                value=account_limit,
                description='アカウント制限数（システム全体のユーザー制限数および管理者のデフォルト制限数）',
                updated_by=current_user.id
            )
        else:
            account_limit = int(account_limit)
        
        return Response(
            json.dumps({
                "default_account_limit": account_limit
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in get_default_account_limit: {str(e)}")
        return Response(
            json.dumps({"error": "デフォルトアカウント制限数の取得中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/admin/default-account-limit', methods=['PUT'])
@jwt_required()
def update_default_account_limit():
    """デフォルトのアカウント制限数を更新するエンドポイント"""
    try:
        # スーパーユーザー権限チェック
        current_user = get_current_user()
        if not current_user.is_superuser:
            return Response(
                json.dumps({"error": "この操作にはスーパーユーザー権限が必要です"}),
                status=403,
                mimetype='application/json'
            )

        data = request.get_json()
        new_limit = data.get('default_account_limit')

        if not isinstance(new_limit, int) or new_limit < 0:
            return Response(
                json.dumps({"error": "有効なデフォルト制限数を指定してください"}),
                status=400,
                mimetype='application/json'
            )

        # 現在のアクティブユーザー数を取得
        active_users_count = User.query.filter_by(is_deleted=False).count()
        
        # 新しい制限が現在のユーザー数より少ない場合はエラー
        if new_limit < active_users_count:
            return Response(
                json.dumps({
                    "error": f"新しい制限数は現在のアクティブユーザー数（{active_users_count}）以上である必要があります"
                }),
                status=400,
                mimetype='application/json'
            )

        # SystemConfigテーブルに設定を保存
        SystemConfig.set_value(
            key='ACCOUNT_LIMIT',
            value=new_limit,
            description='アカウント制限数（システム全体のユーザー制限数および管理者のデフォルト制限数）',
            updated_by=current_user.id
        )

        # 設定オブジェクトも更新
        config = get_config()
        config.ACCOUNT_LIMIT = new_limit

        logger.info(f"Account limit updated by {current_user.email}: {new_limit}")
        return Response(
            json.dumps({
                "message": "アカウント制限数を更新しました",
                "default_account_limit": new_limit
            }),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error in update_default_account_limit: {str(e)}")
        return Response(
            json.dumps({"error": "アカウント制限数の更新中にエラーが発生しました"}),
            status=500,
            mimetype='application/json'
        )

@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    """現在のユーザーの権限を取得"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
            
        # ユーザーの権限を取得
        permissions = [p.to_dict() for p in user.permissions]
        
        # スーパーユーザーまたは管理者の場合は特別な権限を追加
        if user.is_superuser or user.is_admin:
            permissions.append({
                'name': 'admin_access',
                'description': '管理者アクセス権限'
            })
        
        return jsonify({'permissions': permissions}), 200
    except Exception as e:
        logger.error(f"権限取得中にエラーが発生しました: {str(e)}")
        return jsonify({'message': '権限取得中にエラーが発生しました'}), 500

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

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_info():
    """現在のユーザー情報を取得"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
            
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        logger.error(f"ユーザー情報取得中にエラーが発生しました: {str(e)}")
        return jsonify({'message': 'ユーザー情報取得中にエラーが発生しました'}), 500

@auth_bp.route('/permissions/check', methods=['POST'])
@jwt_required()
def check_permissions():
    """複数の権限をチェック"""
    try:
        data = request.get_json()
        permission_names = data.get('permissions', [])
        
        if not permission_names:
            return jsonify({'message': '権限名が指定されていません'}), 400
        
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
        
        # 各権限をチェック
        results = {}
        for perm_name in permission_names:
            results[perm_name] = user.has_permission(perm_name)
        
        return jsonify({
            'results': results,
            'has_all': all(results.values())
        }), 200
    except Exception as e:
        logger.error(f"権限チェック中にエラーが発生しました: {str(e)}")
        return jsonify({'message': '権限チェック中にエラーが発生しました'}), 500

@auth_bp.route('/permissions/check/<permission_name>', methods=['GET'])
@jwt_required()
def check_permission(permission_name):
    """単一の権限をチェック"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
        
        has_permission = user.has_permission(permission_name)
        
        return jsonify({
            'permission': permission_name,
            'has_permission': has_permission
        }), 200
    except Exception as e:
        logger.error(f"権限チェック中にエラーが発生しました: {str(e)}")
        return jsonify({'message': '権限チェック中にエラーが発生しました'}), 500

@auth_bp.route('/permissions/initialize', methods=['POST'])
@jwt_required()
@permission_required('system_config')
def initialize_permissions():
    """権限を初期化する（システム管理者のみ）"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user or not (user.is_superuser or user.is_admin):
            return jsonify({'message': 'この操作を実行する権限がありません'}), 403
        
        # 権限の初期化
        permissions = Permission.initialize_permissions()
        
        # 初期化された権限の数を返す
        return jsonify({
            'message': '権限が正常に初期化されました',
            'count': len(permissions),
            'permissions': [p.to_dict() for p in permissions]
        }), 200
    except Exception as e:
        logger.error(f"権限初期化中にエラーが発生しました: {str(e)}")
        return jsonify({'message': f'権限初期化中にエラーが発生しました: {str(e)}'}), 500

@auth_bp.route('/permissions/assign', methods=['POST'])
@jwt_required()
@permission_required('user_update')
def assign_permission():
    """ユーザーに権限を割り当てる"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        permission_name = data.get('permission_name')
        
        if not user_id or not permission_name:
            return jsonify({'message': 'ユーザーIDと権限名が必要です'}), 400
        
        # ユーザーと権限の存在確認
        user = User.query.get(user_id)
        permission = Permission.query.filter_by(name=permission_name).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
            
        if not permission:
            return jsonify({'message': '権限が見つかりません'}), 404
        
        # 既に割り当てられているか確認
        existing = UserPermission.query.filter_by(
            user_id=user.id, 
            permission_id=permission.id
        ).first()
        
        if existing:
            return jsonify({'message': 'この権限は既にユーザーに割り当てられています'}), 409
        
        # 権限を割り当て
        user_permission = UserPermission(user_id=user.id, permission_id=permission.id)
        db.session.add(user_permission)
        db.session.commit()
        
        return jsonify({
            'message': f'権限 "{permission.name}" がユーザー {user.email} に割り当てられました',
            'user_id': user.id,
            'permission': permission.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"権限割り当て中にエラーが発生しました: {str(e)}")
        return jsonify({'message': '権限割り当て中にエラーが発生しました'}), 500

@auth_bp.route('/permissions/revoke', methods=['POST'])
@jwt_required()
@permission_required('user_update')
def revoke_permission():
    """ユーザーから権限を削除する"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        permission_name = data.get('permission_name')
        
        if not user_id or not permission_name:
            return jsonify({'message': 'ユーザーIDと権限名が必要です'}), 400
        
        # ユーザーと権限の存在確認
        user = User.query.get(user_id)
        permission = Permission.query.filter_by(name=permission_name).first()
        
        if not user:
            return jsonify({'message': 'ユーザーが見つかりません'}), 404
            
        if not permission:
            return jsonify({'message': '権限が見つかりません'}), 404
        
        # 権限割り当ての確認
        user_permission = UserPermission.query.filter_by(
            user_id=user.id, 
            permission_id=permission.id
        ).first()
        
        if not user_permission:
            return jsonify({'message': 'この権限はユーザーに割り当てられていません'}), 404
        
        # 権限を削除
        db.session.delete(user_permission)
        db.session.commit()
        
        return jsonify({
            'message': f'権限 "{permission.name}" がユーザー {user.email} から削除されました',
            'user_id': user.id,
            'permission_name': permission.name
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"権限削除中にエラーが発生しました: {str(e)}")
        return jsonify({'message': '権限削除中にエラーが発生しました'}), 500

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
            
        logger.info(f"ユーザー情報を返します: {user.email}")
        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.error(f"ユーザー情報取得中にエラーが発生しました: {str(e)}")
        return jsonify({'error': 'ユーザー情報取得中にエラーが発生しました'}), 500

def create_auth_bp():
    """認証関連のBlueprint作成関数"""
    return auth_bp
