"""Admin system configuration routes for the auth blueprint."""

from flask import request, Response
from flask_jwt_extended import jwt_required
from apps.reading.shared.domain.entities.user import User
from core.models.system_config import SystemConfig
from core.database import db
from core.utils.logger import get_logger
from core.auth.auth_utils import get_current_user
from config import get_config
from datetime import datetime, timezone, timedelta
import json

logger = get_logger(__name__)


def register_admin_system_routes(bp):
    """Register admin system configuration routes on the given blueprint."""

    @bp.route('/admin/system-stats', methods=['GET'])
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

    @bp.route('/admin/account-limit', methods=['PUT'])
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

            # 現在のアクティブユーザー数を取得
            JST = timezone(timedelta(hours=+9), 'JST')
            now = datetime.now(JST).date()

            non_deleted_users = User.query.filter_by(is_deleted=False).all()

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
