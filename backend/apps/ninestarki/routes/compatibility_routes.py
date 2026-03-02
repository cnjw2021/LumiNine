"""九星気学相性鑑定ルートモジュール"""

from flask import Blueprint, request, jsonify, Response
import json
import traceback
from core.utils.logger import get_logger
from apps.ninestarki.services.compatibility_service import CompatibilityService
from apps.ninestarki.use_cases.calculate_stars_use_case import CalculateStarsUseCase
from apps.ninestarki.infrastructure.persistence.nine_star_repository import NineStarRepository
from datetime import datetime
from core.config import get_config

logger = get_logger(__name__)

def create_compatibility_bp():
    """相性鑑定用のブループリントを作成"""
    compatibility_bp = Blueprint('compatibility', __name__, 
                               url_prefix='/api/compatibility',
                               static_folder='../static',
                               static_url_path='/static')

    @compatibility_bp.route('', methods=['POST'])
    def get_compatibility():
        """
        二人の本命星と生まれ月から相性鑑定結果を取得するAPI
        
        リクエスト例:
        {
            "main_star": 1,
            "target_star": 4,
            "main_birth_month": 3,
            "target_birth_month": 7,
            "is_male": true
        }
        
        もしくは最小ペイロード:
        {
            "main": {"birthdate": "1984-10-14", "gender": "male"},
            "partner": {"birthdate": "1986-05-03", "gender": "female"}
        }
        （名前は任意）
        
        レスポンス例:
        {
            "main_star": 1,
            "target_star": 4,
            "main_birth_month": 3,
            "target_birth_month": 7,
            "is_male": true,
            "symbols": "★○",
            "pattern_code": "PATTERN_12",
            "reading": {
                "id": 12,
                "pattern_code": "PATTERN_12",
                "title": "相性抜群の最高カップル",
                "content": "お互いの存在を高め合える理想的な関係です...",
                "created_at": "2025-05-01T10:00:00+00:00",
                "updated_at": "2025-05-01T10:00:00+00:00"
            }
        }
        """
        try:
            data = request.get_json()
            
            # 1) 互換：既存フォーマット（星番号＋月）
            if all(k in data for k in ['main_star', 'target_star', 'main_birth_month', 'target_birth_month']):
                main_star = int(data['main_star'])
                target_star = int(data['target_star'])
                main_birth_month = int(data['main_birth_month'])
                target_birth_month = int(data['target_birth_month'])
                is_male = data.get('is_male', True)  # デフォルトは男性視点
            else:
                # 2) 最小ペイロード（生年月日＋性別）から算出
                main_info = data.get('main') or {}
                partner_info = data.get('partner') or {}
                if not (main_info.get('birthdate') and main_info.get('gender') and partner_info.get('birthdate') and partner_info.get('gender')):
                    return jsonify({'error': 'main/partnerのbirthdateとgenderが必要です'}), 400

                # 設定から既定の時刻を取得して計算
                calc = CalculateStarsUseCase(NineStarRepository())
                main_birth_norm = (datetime.strptime(main_info['birthdate'].replace('/', '-'), '%Y-%m-%d')).strftime('%Y-%m-%d')
                partner_birth_norm = (datetime.strptime(partner_info['birthdate'].replace('/', '-'), '%Y-%m-%d')).strftime('%Y-%m-%d')
                cfg = get_config()
                noon = getattr(cfg, 'DEFAULT_NOON_TIME', '12:00')
                main_calc = calc.execute(f"{main_birth_norm} {noon}", main_info['gender'], datetime.now().year)
                partner_calc = calc.execute(f"{partner_birth_norm} {noon}", partner_info['gender'], datetime.now().year)

                main_star = int(main_calc.get('main_star', {}).get('star_number'))
                target_star = int(partner_calc.get('main_star', {}).get('star_number'))
                # 生まれ月は暦の月でよい（互換）：生年月日のMM
                main_birth_month = int(main_birth_norm.split('-')[1])
                target_birth_month = int(partner_birth_norm.split('-')[1])
                is_male = True if str(main_info['gender']).lower() == 'male' else False
            
            # パラメータの検証
            if not (1 <= main_star <= 9) or not (1 <= target_star <= 9):
                return jsonify({
                    'error': '本命星は1から9の範囲内である必要があります'
                }), 400
                
            if not (1 <= main_birth_month <= 12) or not (1 <= target_birth_month <= 12):
                return jsonify({
                    'error': '生まれ月は1から12の範囲内である必要があります'
                }), 400
            
            # 相性鑑定結果を取得
            compatibility_result = CompatibilityService.get_compatibility(
                main_star=main_star,
                target_star=target_star,
                main_birth_month=main_birth_month,
                target_birth_month=target_birth_month,
                is_male=is_male
            )
            
            # レスポンスヘッダーとエンコーディングを設定
            response = Response(
                json.dumps(compatibility_result, ensure_ascii=False, indent=2),
                status=200,
                content_type='application/json'
            )
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
        except ValueError as e:
            logger.error(f"Validation error in get_compatibility: {str(e)}")
            return jsonify({
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in get_compatibility: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f'エラーが発生しました: {str(e)}'
            }), 500
            
    return compatibility_bp 