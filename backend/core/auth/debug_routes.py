"""Debug and health check routes for the auth blueprint."""

from flask import Response
from core.database import db
from core.utils.logger import get_logger
from datetime import datetime, timezone
import json

logger = get_logger(__name__)


def register_debug_routes(bp):
    """Register debug and health check routes on the given blueprint."""

    @bp.route('/health', methods=['GET'])
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
