from .nine_star_routes import create_nine_star_bp
from .admin_routes import create_admin_bp
from .solar_routes import create_solar_bp
from .monthly_routes import create_monthly_bp
from .db_management_routes import create_db_management_bp
from .auspicious_days import create_auspicious_days_report_bp

# 登録可能なすべてのブループリント
blueprints = {
    "nine_star": create_nine_star_bp,
    "admin": create_admin_bp,
    "solar": create_solar_bp,
    "monthly": create_monthly_bp,
    "db_management": create_db_management_bp,
    "auspicious_days_report": create_auspicious_days_report_bp,
} 