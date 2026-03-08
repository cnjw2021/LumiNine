from .nine_star_routes import create_nine_star_bp
from .monthly_routes import create_monthly_bp

# 登録可能なすべてのブループリント
blueprints = {
    "nine_star": create_nine_star_bp,
    "monthly": create_monthly_bp,
}