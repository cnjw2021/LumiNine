"""Nine Star Ki routes blueprint."""

from flask import Blueprint, request, jsonify
from flask_injector import inject
from datetime import datetime
from core.utils.logger import get_logger
from apps.fortunetelling.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase

logger = get_logger(__name__)

def create_nine_star_bp():

    nine_star_bp = Blueprint('nine_star', __name__, 
                           url_prefix='/api/nine-star')

    @nine_star_bp.route('/calculate', methods=['POST'])
    @inject
    def calculate(calculate_stars_use_case: CalculateStarsUseCase):
        """生年月日からすべての九星を計算するAPI"""
        try:
            data = request.get_json()
            if not data or 'birth_datetime' not in data:
                return jsonify({'error': '生年月日時が必要です。形式: YYYY-MM-DD HH:MM'}), 400
            
            result = calculate_stars_use_case.execute(
                birth_datetime_str=data['birth_datetime'],
                gender=data.get('gender', 'male'),
                target_year=data.get('target_year', datetime.now().year)
            )
            return jsonify(result)
        except ValueError as ve:
            logger.warning(f"Validation error in /calculate: {str(ve)}")
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error in /calculate: {e}", exc_info=True)
            return jsonify({'error': 'サーバー内部でエラーが発生しました'}), 500


    return nine_star_bp
