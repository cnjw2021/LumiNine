"""
吉日APIルート

このディレクトリには吉日計算と関連するすべてのAPIエンドポイントが含まれています。
"""

from .auspicious_days_report import create_auspicious_days_report_bp

__all__ = [
    'create_auspicious_days_report_bp',
]
