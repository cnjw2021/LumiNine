"""Nine Star Ki routes blueprint."""

from flask import Blueprint, request, jsonify, Response, current_app
from flask_injector import inject

import json
from apps.ninestarki.domain.entities.nine_star import NineStar
from core.models.daily_astrology import DailyAstrology
from core.utils.logger import get_logger
from core.models.star_attribute import StarAttribute
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from core.models.main_star_acquired_fortune_message import MainStarAcquiredFortuneMessage
from core.models.month_star_acquired_fortune_message import MonthStarAcquiredFortuneMessage
from core.services.solar_calendar_service import SolarCalendarService
from core.models.solar_starts import SolarStarts
from datetime import datetime, date

from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.use_cases.star_catalog_use_case import StarCatalogUseCase

from apps.ninestarki.services.star_attribute_service import StarAttributeService
from apps.ninestarki.use_cases.star_attribute_use_case import StarAttributeUseCase
from apps.ninestarki.services.year_fortune_service import YearFortuneService
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from flask_cors import cross_origin
import os

logger = get_logger(__name__)

def create_nine_star_bp():

    nine_star_bp = Blueprint('nine_star', __name__, 
                           url_prefix='/api/nine-star',
                           static_folder='../static',
                           static_url_path='/static')

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
    

    @nine_star_bp.route('/star-attributes', methods=['GET'])
    @inject
    def get_star_attributes(star_attr_uc: StarAttributeUseCase):
        """
        星の属性データを取得するエンドポイント
        特定の星番号を指定すると、その星の属性情報のみを返す
        """
        try:
            star_number = request.args.get('star_number')
            
            if not star_number:
                return jsonify({
                    'error': 'Missing parameter',
                    'message': 'star_number is required'
                }), 400
            
            star_number = int(star_number)
            
            if not 1 <= star_number <= 9:
                return jsonify({
                    'error': 'Invalid parameter',
                    'message': 'star_number must be between 1 and 9'
                }), 400
            
            result = star_attr_uc.get_star_attributes(star_number)
            
            return jsonify(result)
            
        except ValueError as e:
            logger.error(f"Error parsing parameters: {str(e)}")
            return jsonify({
                'error': 'Invalid parameter format',
                'message': 'star_number should be a valid integer'
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in get_star_attributes: {str(e)}")
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/preview-report', methods=['POST'])
    @inject
    def preview_report(use_case: 'GenerateReportUseCase'):
        """
        九星気学鑑定結果のHTMLプレビューを生成するAPI
        
        リクエスト例:
        {
            "resultData": {
                "result": {
                    "main_star": {...},
                    "month_star": {...},
                    "day_star": {...},
                    "year_star": {...},
                    "birth_datetime": "1980-02-04 15:30",
                    "target_year": 2025
                },
                "fullName": "山田太郎",
                "birthdate": "1980-02-04",
                "birthtime": "15:30",
                "gender": "male",
                "targetYear": 2025
            },
            "templateId": 1,
            "backgroundId": 1
        }
        """
        try:
            data = request.get_json()
            
            if not data or 'resultData' not in data:
                logger.error("Missing resultData in request")
                return jsonify({
                    'error': '鑑定結果データが必要です'
                }), 400
            
            result_data = data['resultData']
            template_id = data.get('templateId', 1)
            background_id = data.get('backgroundId', 1)
            
            # 必須パラメータの検証
            if not all(key in result_data for key in ['result', 'fullName', 'birthdate', 'gender']):
                missing_fields = []
                for field in ['result', 'fullName', 'birthdate', 'gender']:
                    if field not in result_data:
                        missing_fields.append(field)
                
                logger.error(f"Missing required fields: {', '.join(missing_fields)}")
                return jsonify({
                    'error': f'必須パラメータが不足しています: {", ".join(missing_fields)}'
                }), 400
            
            # useSimpleパラメータを取得
            use_simple = data.get('useSimple', False)
            
            # リクエストデータをログに出力
            logger.info(f"Generating HTML preview for: {result_data['fullName']}")
            logger.info(f"Birthdate: {result_data['birthdate']}, Gender: {result_data['gender']}")
            logger.info(f"Template ID: {template_id}, Background ID: {background_id}, Use Simple: {use_simple}")
            
            # HTML生成サービスを呼び出し
            try:
                # HTML 렌더러를 직접 사용
                html_content = use_case.execute_html_preview({
                    'result_data': result_data['result'],
                    'full_name': result_data['fullName'],
                    'birthdate': result_data['birthdate'],
                    'gender': result_data['gender'],
                    'target_year': result_data.get('targetYear'),
                    'template_id': template_id,
                    'background_id': background_id,
                    'use_simple': use_simple
                })
                
                # HTMLコンテンツを直接返す
                return html_content, {'Content-Type': 'text/html; charset=utf-8'}
            except Exception as e:
                logger.error(f"Error in HTML preview generation: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': str(e)}), 500
        
        except Exception as e:
            logger.error(f"Error in HTML preview route: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500

    return nine_star_bp
