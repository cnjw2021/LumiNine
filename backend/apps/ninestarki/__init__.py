"""NineStarKi application package."""

from flask import Flask

def create_app():
    # Flaskアプリの作成と設定
    app = Flask(__name__)
    
    # 各ブループリントを登録
    from .routes import (
        create_nine_star_bp, create_admin_bp,
        create_solar_bp, create_monthly_bp, create_db_management_bp,
        create_auspicious_days_report_bp,
    )
    app.register_blueprint(create_nine_star_bp())
    app.register_blueprint(create_admin_bp())
    app.register_blueprint(create_solar_bp())
    app.register_blueprint(create_monthly_bp())
    app.register_blueprint(create_db_management_bp())
    app.register_blueprint(create_auspicious_days_report_bp())
    
    return app 