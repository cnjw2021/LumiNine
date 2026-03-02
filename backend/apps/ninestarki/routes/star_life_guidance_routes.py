from flask import Blueprint, request, jsonify
from injector import inject
from apps.ninestarki.use_cases.star_life_guidance_use_case import StarLifeGuidanceUseCase
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_star_life_guidance_bp():
    """星と人生のガイダンス情報のBlueprintを作成する"""
    star_life_guidance_bp = Blueprint('star_life_guidance', __name__, url_prefix='/api/star-life-guidance')

    @star_life_guidance_bp.route('', methods=['GET'])
    @inject
    def get_star_life_guidance(use_case: StarLifeGuidanceUseCase):
        """星と人生のガイダンス情報を取得するAPI"""
        try:
            # クエリパラメータを取得
            main_star = request.args.get('main_star', type=int)
            month_star = request.args.get('month_star', type=int)
            category = request.args.get('category', type=str)

            # 必須パラメータの検証
            if not main_star or not month_star:
                return jsonify({
                    'error': 'main_starとmonth_starは必須パラメータです'
                }), 400

            # カテゴリが指定されている場合は特定のカテゴリのみ取得
            if category:
                result = use_case.get_guidance_by_category(main_star, month_star, category)
                if not result:
                    return jsonify({
                        'error': '指定されたカテゴリのガイダンスが見つかりません'
                    }), 404
                return jsonify(result), 200
            else:
                # すべてのカテゴリを取得
                result = use_case.get_star_life_guidance(main_star, month_star)
                return jsonify(result), 200

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error getting star life guidance: {e}")
            return jsonify({'error': 'ガイダンス情報の取得に失敗しました'}), 500

    return star_life_guidance_bp
