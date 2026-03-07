"""Nine Star Ki routes blueprint."""

from flask import Blueprint, request, jsonify, Response, current_app
from flask_injector import inject

import json
from apps.ninestarki.domain.entities.nine_star import NineStar
from core.models.daily_astrology import DailyAstrology
from core.utils.logger import get_logger
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from core.services.solar_calendar_service import SolarCalendarService
from datetime import datetime, date

from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.use_cases.star_catalog_use_case import StarCatalogUseCase


from flask_cors import cross_origin
import os

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


    @nine_star_bp.route('/stars', methods=['GET'])
    @inject
    def get_stars(star_uc: StarCatalogUseCase):
        """九星一覧を取得するAPI"""
        try:
            star_number = request.args.get('star_number', type=int)
            if star_number:
                star = star_uc.get_star(star_number)
                if not star:
                    return jsonify({'error': '指定された星が見つかりません'}), 404
                return jsonify([star])
            results = star_uc.list_stars()
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error retrieving stars: {str(e)}")
            return jsonify({'error': '星データの取得に失敗しました'}), 500
    



    return nine_star_bp
