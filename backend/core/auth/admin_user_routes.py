"""Admin user CRUD routes for the auth blueprint."""

from flask import request, Response
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from apps.reading.shared.domain.entities.user import User
from apps.reading.shared.infrastructure.persistence.user_repository import UserRepository
from core.models.exceptions import (
    PermissionError,
    AccountLimitExceededError,
)
from core.models.admin_account_limit import AdminAccountLimit
from core.database import db
from core.utils.logger import get_logger
from core.auth.auth_utils import get_current_user
from datetime import datetime
import json

logger = get_logger(__name__)

# TODO: Usecaseで生成するように修正する
user_repo = UserRepository()


def register_admin_user_routes(bp):
    """Register admin user CRUD routes on the given blueprint."""

    @bp.route('/admin/users', methods=['GET'])
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

    @bp.route('/admin/users', methods=['POST'])
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

    @bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
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

    @bp.route('/admin/users/<int:user_id>', methods=['PUT'])
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

        except ValueError:
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

    @bp.route('/admin/users/<int:user_id>/account-limit', methods=['PUT'])
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
