from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from apps.ninestarki.domain.entities.user import User
from core.utils.logger import get_logger
from sqlalchemy import text
from core.database import db

logger = get_logger(__name__)

def permission_required(permission_name):
    """特定の権限を持つユーザーのみアクセス可能なデコレータ"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                current_user_email = get_jwt_identity()
                current_user = User.query.filter_by(email=current_user_email, is_deleted=False).first()
                
                if not current_user:
                    logger.warning(f"ユーザーが見つかりません: {current_user_email}")
                    return jsonify({
                        'error': 'ユーザーが見つかりません',
                        'code': 'user_not_found'
                    }), 404
                
                # スーパーユーザーは常にすべての権限を持つ
                if current_user.is_superuser:
                    logger.info(f"スーパーユーザー {current_user.email} が {permission_name} 権限でアクセスしました")
                    return fn(*args, **kwargs)
                
                # 管理者の基本権限
                if current_user.is_admin and permission_name in ['user_view', 'user_create', 'user_edit', 'user_delete', 'data_management']:
                    logger.info(f"管理者 {current_user.email} が基本権限 {permission_name} でアクセスしました")
                    return fn(*args, **kwargs)
                
                # 権限チェック
                logger.info(f"権限チェック: ユーザー {current_user.email}, 権限 {permission_name}")
                
                # 権限テーブルから権限IDを取得
                try:
                    permission_id_result = db.session.execute(
                        text("SELECT id FROM permissions WHERE name = :name"),
                        {"name": permission_name}
                    ).fetchone()
                    
                    if not permission_id_result:
                        logger.warning(f"権限 {permission_name} はデータベースに存在しません")
                        # 開発環境では権限がなくてもアクセスを許可（オプション）
                        import os
                        if os.environ.get('FLASK_ENV') == 'development':
                            logger.warning(f"開発環境のため、権限 {permission_name} がなくてもアクセスを許可します")
                            return fn(*args, **kwargs)
                        
                        return jsonify({
                            'error': 'この操作に必要な権限がありません',
                            'code': 'permission_denied',
                            'required_permission': permission_name
                        }), 403
                    
                    permission_id = permission_id_result[0]
                    
                    # ユーザーが権限を持っているか確認
                    has_permission = db.session.execute(
                        text("""
                            SELECT COUNT(*) FROM user_permissions 
                            WHERE user_id = :user_id AND permission_id = :permission_id
                        """),
                        {"user_id": current_user.id, "permission_id": permission_id}
                    ).scalar() > 0
                    
                    logger.info(f"権限チェック結果: {has_permission}")
                    
                    if not has_permission:
                        return jsonify({
                            'error': 'この操作に必要な権限がありません',
                            'code': 'permission_denied',
                            'required_permission': permission_name
                        }), 403
                        
                    return fn(*args, **kwargs)
                except Exception as db_error:
                    logger.error(f"権限チェック中にデータベースエラーが発生: {str(db_error)}")
                    # 開発環境では権限チェックエラーでもアクセスを許可（オプション）
                    import os
                    if os.environ.get('FLASK_ENV') == 'development':
                        logger.warning(f"開発環境のため、権限チェックエラーでもアクセスを許可します")
                        return fn(*args, **kwargs)
                    
                    return jsonify({
                        'error': '権限チェック中にエラーが発生しました',
                        'code': 'permission_check_error'
                    }), 500
            except Exception as e:
                logger.error(f"認証エラー: {str(e)}")
                import traceback
                logger.error(f"トレースバック: {traceback.format_exc()}")
                return jsonify({
                    'error': '認証に失敗しました',
                    'code': 'authentication_failed'
                }), 401
        return wrapper
    return decorator 