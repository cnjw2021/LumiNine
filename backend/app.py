from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from core.utils.logger import init_logger, get_logger
from core.config import get_config
from core.database import init_db, db
import os
import sys
import json
from datetime import datetime, date
import logging
from flask_injector import FlaskInjector
from apps.ninestarki.dependency_module import AppModule
from injector import Injector

from apps.ninestarki.use_cases.permission_use_case import PermissionUseCase
from apps.ninestarki.use_cases.generate_report_use_case import GenerateReportUseCase

# パスを追加
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 絶対パスでインポート
from apps.ninestarki.routes.nine_star_routes import create_nine_star_bp
from apps.ninestarki.routes.admin_routes import create_admin_bp
from apps.ninestarki.routes.monthly_routes import create_monthly_bp
from apps.ninestarki.routes.solar_routes import create_solar_bp
from apps.ninestarki.routes.db_management_routes import create_db_management_bp
from apps.ninestarki.routes.compatibility_routes import create_compatibility_bp
from apps.ninestarki.routes.auspicious_days import create_auspicious_days_report_bp
from apps.ninestarki.routes.star_life_guidance_routes import create_star_life_guidance_bp
from apps.ninestarki.routes.pdf_job_routes import create_pdf_jobs_bp
from core.exceptions import AppError

from core.auth import auth_bp
from core.auth.permission_routes import create_permission_bp

# JSONエンコーダーをカスタマイズ
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

    def encode(self, obj):
        """オブジェクトをUTF-8でエンコード"""
        if isinstance(obj, str):
            return super().encode(obj)
        if isinstance(obj, dict):
            return super().encode({k: v.encode('utf-8').decode('utf-8') if isinstance(v, str) else v for k, v in obj.items()})
        if isinstance(obj, list):
            return super().encode([v.encode('utf-8').decode('utf-8') if isinstance(v, str) else v for v in obj])
        return super().encode(obj)

# テンプレートディレクトリを含むパスを計算
template_folder_path = os.path.join(PROJECT_ROOT, 'apps', 'ninestarki', 'templates')

def create_app() -> Flask:
    # DIコンテナを作成し、必要なユースケースを取得
    injector = Injector([AppModule()])
    generate_report_use_case = injector.get(GenerateReportUseCase)

    app = Flask(__name__, 
               static_folder='static',
               static_url_path='/static',
               template_folder=template_folder_path)

    # 設定
    app.config.from_object(get_config())
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.json_encoder = CustomJSONEncoder
    app.json.ensure_ascii = False

    # DB 초기화
    init_db(app)

    # CORS 설정
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3000", "http://localhost", "http://localhost:80", "https://831shop.site", "https://www.831shop.site"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }},
         supports_credentials=True)

    # JWT 초기화
    JWTManager(app)

    # 로거 초기화
    init_logger()
    logger = get_logger('app')
    logger.setLevel(logging.DEBUG)

    # after_request 헤더 설정
    @app.after_request
    def add_header(response):
        if response.mimetype == 'application/json':
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    # 블루프린트 등록
    app.register_blueprint(create_nine_star_bp())
    app.register_blueprint(create_admin_bp())
    app.register_blueprint(create_monthly_bp())
    app.register_blueprint(create_solar_bp())
    app.register_blueprint(create_db_management_bp())
    app.register_blueprint(create_compatibility_bp())
    app.register_blueprint(create_auspicious_days_report_bp())
    app.register_blueprint(create_star_life_guidance_bp())
    app.register_blueprint(create_pdf_jobs_bp(generate_report_use_case))
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 権限ユースケースもDIから取得
    perm_use_case = injector.get(PermissionUseCase)
    app.register_blueprint(create_permission_bp(perm_use_case))

    # DI 설정（同一InjectorをFlaskに紐付け）
    FlaskInjector(app=app, injector=injector)

    # 전역 에러 핸들러
    @app.errorhandler(AppError)
    def handle_app_error(e: AppError):
        request_id = request.headers.get('X-Request-ID') or 'n/a'
        return jsonify({"error": e.to_dict(), "request_id": request_id}), e.status

    @app.errorhandler(Exception)
    def handle_unexpected_error(e: Exception):
        request_id = request.headers.get('X-Request-ID') or 'n/a'
        logger.exception(f"unhandled_exception | request_id={request_id} | {e}")
        return jsonify({
            "error": {"code": "INTERNAL_ERROR", "message": "서버 내부 오류가 발생했습니다."},
            "request_id": request_id
        }), 500

    @app.route('/')
    def index():
        return Response(
            json.dumps({
                "message": "九星気学API",
                "version": "1.0.0",
                "endpoints": [
                    "/api/nine-star/calculate",
                    "/api/nine-star/compatibility",
                    "/api/nine-star/monthly-chart",
                    "/api/auth/login",
                    "/api/auth/me",
                    "/api/admin/stars",
                    "/api/admin/solar/solar-starts",
                    "/api/admin/solar/solar-terms",
                    "/api/monthly/directions",
                    "/api/star-life-guidance"
                ]
            }, cls=CustomJSONEncoder, ensure_ascii=False),
            status=200,
            mimetype='application/json; charset=utf-8'
        )

    @app.route('/auth/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)