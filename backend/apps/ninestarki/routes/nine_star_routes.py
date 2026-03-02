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
from apps.ninestarki.use_cases.get_fortune_data_use_case import GetFortuneDataUseCase
from apps.ninestarki.use_cases.reading_query_use_case import ReadingQueryUseCase
from apps.ninestarki.use_cases.star_catalog_use_case import StarCatalogUseCase
from apps.ninestarki.use_cases.daily_star_reading_use_case import DailyStarReadingUseCase

from apps.ninestarki.services.star_attribute_service import StarAttributeService
from apps.ninestarki.use_cases.star_attribute_use_case import StarAttributeUseCase
from apps.ninestarki.services.year_fortune_service import YearFortuneService
from apps.ninestarki.services.month_fortune_service import MonthFortuneService
from apps.ninestarki.domain.services.direction_marks_domain_service import DirectionMarksDomainService
from apps.ninestarki.services.svg_generator_service import SvgGeneratorService
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

    @nine_star_bp.route('/month-star-readings', methods=['GET'])
    @inject
    def get_month_star_readings(reading_uc: ReadingQueryUseCase):
        """月命星の読みデータを取得するAPI"""
        try:
            star_number = request.args.get('star_number', type=int)
            if star_number:
                reading = reading_uc.get_monthly_star_reading(star_number)
                if not reading:
                    return jsonify({'error': 'Not found', 'message': 'No monthly star reading found'}), 404
                # 互換性のため単一でも配列で返却
                return jsonify([reading])
            result = reading_uc.list_monthly_star_readings()
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in get_month_star_readings: {str(e)}")
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/daily-star-reading', methods=['GET'])
    @inject
    def get_daily_star_reading(daily_uc: DailyStarReadingUseCase):
        """
        生年月日から日命星を特定し、その読みデータを取得するエンドポイント
        
        クエリパラメータ:
            birth_date: 生年月日（形式: YYYY-MM-DD）
        """
        try:
            birth_date_str = request.args.get('birth_date')
            if not birth_date_str:
                return jsonify({'error': '生年月日が必要です', 'message': 'birth_date parameter is required (format: YYYY-MM-DD)'}), 400
            try:
                result = daily_uc.execute(birth_date_str)
            except ValueError:
                return jsonify({'error': '日付形式が不正です', 'message': 'birth_date must be in format YYYY-MM-DD'}), 400
            if not result:
                return jsonify({'error': '日命星の計算に失敗しました', 'message': 'Could not calculate daily star for the given birth date'}), 404
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error retrieving daily star reading: {str(e)}")
            return jsonify({
                'error': 'サーバーエラー',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/daily-star-readings', methods=['GET'])
    @inject
    def get_daily_star_readings(reading_uc: ReadingQueryUseCase):
        """
        特定の星番号に対する日命星読みデータを取得するエンドポイント
        
        クエリパラメータ:
            star_number: 星番号（1-9）
        """
        try:
            star_number = request.args.get('star_number', type=int)
            if not star_number:
                result = reading_uc.list_daily_star_readings()
                return jsonify(result)
            if not 1 <= star_number <= 9:
                return jsonify({'error': '不正な星番号です', 'message': 'star_number must be between 1 and 9'}), 400
            reading = reading_uc.get_daily_star_reading(star_number)
            if not reading:
                return jsonify({'error': '日命星読みデータが見つかりません', 'message': f'No reading data found for star number {star_number}'}), 404
            return jsonify(reading)
            
        except Exception as e:
            logger.error(f"Error retrieving daily star readings: {str(e)}")
            return jsonify({
                'error': 'サーバーエラー',
                'message': str(e)
            }), 500

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
    
    @nine_star_bp.route('/direction-fortune', methods=['GET'])
    @inject
    def get_direction_fortune(fortune_use_case: GetFortuneDataUseCase):
        """
        九星盤における方位の吉凶判定を取得するAPI
        
        パラメータ:
        main_star: 本命星の番号（1-9） - ユーザーの本命星
        month_star: 月命星の番号（1-9）
        year: 対象年度（指定がない場合は現在の年を使用）
        
        リクエスト例:
        /api/nine-star/direction-fortune?main_star=3&month_star=4
        /api/nine-star/direction-fortune?main_star=3&month_star=4&year=2025
        
        レスポンス例:
        {
            "north": {"is_auspicious": true, "reason": null, "marks": []},
            "northeast": {"is_auspicious": false, "reason": "暗剣殺", "marks": ["dark_sword"]},
            "east": {"is_auspicious": true, "reason": null, "marks": []},
            ...
        }
        """
        try:
            # ユーザーの本命星を取得
            main_star = request.args.get('main_star', type=int)
            if not main_star or not 1 <= main_star <= 9:
                return jsonify({'error': '有効な本命星番号（1-9）を指定してください'}), 400
            
            # 月命星を取得
            month_star = request.args.get('month_star', type=int)
            if not month_star or not 1 <= month_star <= 9:
                return jsonify({'error': '有効な月命星番号（1-9）を指定してください'}), 400
            
            logger.debug(f"ユーザーの本命星: {main_star}番, 月命星: {month_star}番")

            # 対象年度を取得
            target_year = request.args.get('year', type=int)
            if not target_year:
                return jsonify({'error': '対象年度を指定してください'}), 400
            
            # UseCase経由で年星/干支を取得し、ドメインのコンテキストメソッドで判定
            result = fortune_use_case.get_direction_fortune(main_star, month_star, target_year)
            if not result:
                return jsonify({'error': '方位の吉凶情報の取得に失敗しました'}), 500
                        
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving direction fortune: {str(e)}")
            return jsonify({'error': '方位の吉凶情報の取得に失敗しました', 'detail': str(e)}), 500

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

    @nine_star_bp.route('/year-star', methods=['GET'])
    @inject
    def get_year_star(fortune_use_case: GetFortuneDataUseCase):
        """
        指定された年の年運星（九星盤の中央の星）を取得するエンドポイント
        クエリパラメータ:
            year: 対象年度（指定がない場合は現在の年を使用）
            
        注意:
        - yearパラメータで指定された年の星を計算する際は、現在の月日を維持します
        - 例えば5月1日に2025年を指定した場合、2025年5月1日の星が計算されます
        """
        try:
            # 対象年度を取得
            target_year = request.args.get('year', type=int)
            if not target_year:
                target_year = datetime.now().year
            
            # DirectionFortuneServiceを使用して年運星情報を取得
            result = fortune_use_case.get_year_star_info(target_year)
            
            if not result:
                return jsonify({
                    'error': 'Star not found',
                    'message': f'Failed to get year star information for year {target_year}'
                }), 404
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error retrieving year star: {str(e)}")
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/annual-directions', methods=['GET'])
    @inject
    def get_annual_directions(fortune_use_case: GetFortuneDataUseCase):
        """
        1年分の吉方位情報を取得するAPI
        
        クエリパラメータ:
            main_star: 本命星の番号（1-9）
            month_star: 月命星の番号（1-9）
            year: 鑑定年（デフォルトは現在の年）
        
        戻り値:
            12ヶ月分の吉凶方位情報を含むJSON
        """
        try:
            # クエリパラメータの取得
            main_star = request.args.get('main_star', type=int)
            month_star = request.args.get('month_star', type=int)
            target_year = request.args.get('target_year', type=int)
            
            print(f"main_star: {main_star}, month_star: {month_star}, target_year: {target_year}")

            if not main_star or not 1 <= main_star <= 9:
                return jsonify({'error': '有効な本命星番号（1-9）を指定してください'}), 400
            
            if not month_star or not 1 <= month_star <= 9:
                return jsonify({'error': '有効な月命星番号（1-9）を指定してください'}), 400
            
            # 年の取得（指定がない場合は現在の年を使用）
            if not target_year:
                target_year = datetime.now().year
                
            
            result = fortune_use_case.get_annual_directions(main_star, month_star, target_year)
            return jsonify(result)
            
        except ValueError as e:
            logger.error(f"Validation error in get_annual_directions: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error in get_annual_directions: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/year-acquired-fortune', methods=['GET'])
    @inject
    def get_year_acquired_fortune(fortune_use_case: GetFortuneDataUseCase):
        """
        指定年を含む3年分の運気情報を取得するAPI
        
        クエリパラメータ:
            main_star: 本命星の番号（1-9）
            month_star: 月命星の番号（1-9） 
            target_year: 鑑定年（デフォルトは現在の年）
        
        戻り値:
            指定年を含む3年分の運気情報を含むJSON
        """
        try:
            # クエリパラメータの取得
            main_star = request.args.get('main_star', type=int)
            month_star = request.args.get('month_star', type=int)
            original_year = request.args.get('target_year', type=int)
            
            if not main_star or not 1 <= main_star <= 9:
                return jsonify({'error': '有効な本命星番号（1-9）を指定してください'}), 400
                
            if not month_star or not 1 <= month_star <= 9:
                return jsonify({'error': '有効な月命星番号（1-9）を指定してください'}), 400
            
            # 年の取得（指定がない場合は現在の年を使用）
            if not original_year:
                original_year = datetime.now().year
            
            # UseCase経由で3年分の運気データを取得
            result = fortune_use_case.get_year_acquired_fortune(main_star, month_star, original_year)
            
            return jsonify(result)

        except ValueError as e:
            logger.error(f"Validation error in get_year_acquired_fortune: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error in get_year_acquired_fortune: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Server error',
                'message': str(e)
            }), 500

    @nine_star_bp.route('/month-acquired-fortune', methods=['GET'])
    @inject
    def get_month_acquired_fortune(fortune_use_case: GetFortuneDataUseCase):
        """
        月の運気情報を取得するAPI
        
        クエリパラメータ:
            main_star: 本命星の番号（1-9）
            month_star: 月命星の番号（1-9）
            target_year: 鑑定年（デフォルトは現在の年）
        
        戻り値:
            12ヶ月分の時の運気情報を含むJSON
        """
        try:
            # クエリパラメータの取得
            main_star = request.args.get('main_star', type=int)
            month_star = request.args.get('month_star', type=int)
            target_year = request.args.get('target_year', type=int)
            
            if not main_star or not 1 <= main_star <= 9:
                return jsonify({'error': '有効な本命星番号（1-9）を指定してください'}), 400
            
            if not month_star or not 1 <= month_star <= 9:
                return jsonify({'error': '有効な月命星番号（1-9）を指定してください'}), 400
            
            # 年の取得（指定がない場合は現在の年を使用）
            if not target_year:
                target_year = datetime.now().year
                
            result = fortune_use_case.get_month_acquired_fortune(main_star, month_star, target_year)
            return jsonify(result)

        except ValueError as e:
            logger.error(f"Validation error in get_month_acquired_fortune: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error in get_month_acquired_fortune: {str(e)}")
            import traceback
            traceback.print_exc()
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

    @nine_star_bp.route('/save-svg', methods=['POST'])
    @cross_origin()
    def save_svg():
        """
        SVGを保存するAPI（サービス層を活用）
        
        リクエスト例:
        {
            "centerStar": "一白水星",
            "svgContent": "<svg>...</svg>",
            "size": 600,
            "backgroundGradient": "classic",
            "mode": "save" | "generate" | "auto"
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'リクエストデータが必要です'}), 400
            
            # SvgGeneratorServiceを使用して処理
            svg_service = SvgGeneratorService()
            result = svg_service.process_svg_request(data)
            
            # 結果に応じてレスポンスを返す
            if result.get('success'):
                return jsonify(result), 200
            else:
                return jsonify(result), 400
        
        except Exception as e:
            logger.error(f"Error in save SVG route: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @nine_star_bp.route('/generate-pdf-svg', methods=['POST'])
    @cross_origin()
    def generate_pdf_svg():
        """
        PDF互換の九星盤SVGを生成するAPI
        
        リクエスト例:
        {
            "centerStar": "一白水星",
            "size": 600
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'リクエストデータが必要です'}), 400
            
            center_star = data.get('centerStar', '一白水星')
            size = data.get('size', 600)
            
            # PDF対応SVG生成サービスを使用
            svg_service = SvgGeneratorService()
            svg_content = svg_service.generate_kyusei_board_svg_pdf(center_star, size)
            
            logger.info(f"Generated PDF-compatible SVG for {center_star}, size: {size}")
            
            return jsonify({
                'success': True,
                'svg_content': svg_content,
                'center_star': center_star,
                'size': size,
                'message': f'PDF対応SVGを正常に生成しました: {center_star}'
            }), 200
        
        except Exception as e:
            logger.error(f"Error in generate PDF SVG route: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'PDF対応SVG生成でエラーが発生しました'
            }), 500

    @nine_star_bp.route('/generate-enhanced-pdf-svg', methods=['POST'])
    @cross_origin()
    def generate_enhanced_pdf_svg():
        """
        強化PDF互換の九星盤SVGを生成するAPI（添付画像レベルの品質）
        
        リクエスト例:
        {
            "centerStar": "一白水星",
            "size": 600
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'リクエストデータが必要です'}), 400
            
            center_star = data.get('centerStar', '一白水星')
            size = data.get('size', 600)
            
            # 強化PDF対応SVG生成サービスを使用
            svg_service = SvgGeneratorService()
            svg_content = svg_service.generate_kyusei_board_svg_enhanced_pdf(center_star, size)
            
            logger.info(f"Generated enhanced PDF-compatible SVG for {center_star}, size: {size}")
            
            return jsonify({
                'success': True,
                'svg_content': svg_content,
                'center_star': center_star,
                'size': size,
                'message': f'強化PDF対応SVGを正常に生成しました: {center_star}（添付画像レベル品質）'
            }), 200
        
        except Exception as e:
            logger.error(f"Error in generate enhanced PDF SVG route: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': '強化PDF対応SVG生成でエラーが発生しました'
            }), 500

    @nine_star_bp.route('/generate-step9-pdf-svg', methods=['POST'])
    @cross_origin()
    def generate_step9_pdf_svg():
        """
        Step9の九星盤SVGを生成するAPI（Step1ベース + PDF互換版）
        Step1の美しい要素を保持しつつStep6の成功手法を適用
        
        リクエスト例:
        {
            "centerStar": "一白水星",
            "size": 600
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'リクエストデータが必要です'}), 400
            
            center_star = data.get('centerStar', '一白水星')
            size = data.get('size', 600)
            
            # Step9 PDF対応SVG生成サービスを使用
            svg_service = SvgGeneratorService()
            svg_content = svg_service.generate_kyusei_board_svg_step9_pdf(center_star, size)
            
            logger.info(f"Generated Step9 (Step1-based PDF-compatible) SVG for {center_star}, size: {size}")
            
            return jsonify({
                'success': True,
                'svg_content': svg_content,
                'center_star': center_star,
                'size': size,
                'message': f'Step9 SVGを正常に生成しました: {center_star}（Step1美しさ + PDF互換性）'
            }), 200
        
        except Exception as e:
            logger.error(f"Error in generate Step9 PDF SVG route: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Step9 SVG生成でエラーが発生しました'
            }), 500

    return nine_star_bp
