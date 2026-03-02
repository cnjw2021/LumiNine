"""引越し吉日と水取り吉日の総合レポートAPIルート"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from core.utils.logger import get_logger
from apps.ninestarki.use_cases.auspicious_dates_use_case import AuspiciousDatesUseCase
from flask_injector import inject

logger = get_logger(__name__)

def create_auspicious_days_report_bp():
    """総合吉日レポートBlueprintの作成"""
    # Blueprintの名前とURL接頭辞を'レポート'の役割に合わせて変更
    report_bp = Blueprint('auspicious_days_report', __name__, url_prefix='/api/reports/auspicious-days')

    @report_bp.route('', methods=['GET'])
    @inject
    def get_auspicious_days_report(use_case: AuspiciousDatesUseCase):
        """引越し吉日と水取り吉日が含まれる総合レポートを返すAPI"""
        try:
            year = request.args.get('year', type=int)
            main_star = request.args.get('mainStar', type=int)
            month_star = request.args.get('monthStar', type=int)

            logger.debug(f"Auspicious days report request: year={year}, mainStar={main_star}, monthStar={month_star}")

            if not all([year, main_star, month_star]):
                return jsonify({'error': 'year, mainStar, monthStarパラメータは必須です'}), 400
            
            result = use_case.execute(main_star, month_star, year)
            
            return jsonify(result)
            
        except ValueError as ve:
            logger.warning(f"Invalid input for auspicious days report: {ve}")
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error getting auspicious days report: {e}", exc_info=True)
            return jsonify({'error': 'サーバー内部エラーが発生しました.'}), 500
    
    return report_bp