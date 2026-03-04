"""月盤データのAPIルート"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from core.database import db
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from apps.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
from apps.ninestarki.use_cases.powerstone_recommendation_use_case import PowerStoneRecommendationUseCase
from apps.ninestarki.use_cases.six_layer_powerstone_use_case import SixLayerPowerStoneUseCase
from apps.ninestarki.domain.exceptions import NineStarKiError, NoAuspiciousDirectionError
from apps.ninestarki.domain.value_objects.locale import Locale
from core.models.star_groups import StarGroup
from flask_injector import inject
from core.auth.auth_utils import permission_required
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_monthly_bp():
    """月盤データのBlueprint作成"""
    monthly_bp = Blueprint('monthly', __name__, url_prefix='/api/monthly')
    
    @monthly_bp.route('/directions', methods=['GET'])
    @inject
    def get_monthly_directions(repo: IMonthlyDirectionsRepository):
        """月盤の方位データを取得するAPI
        
        クエリパラメータ:
        - star: 九星番号（1-9）- 指定された場合はその星のグループの方位データを返す
        - group_id: グループID（1-3）- 指定された場合はそのグループの方位データを返す
        - month: 月（1-12）- 指定された場合はその月の方位データを返す
        
        これらパラメータは組み合わせ可能。
        """
        try:
            star_number = request.args.get('star', type=int)
            group_id = request.args.get('group_id', type=int)
            month = request.args.get('month', type=int)
            
            # 星番号が指定された場合はグループを取得
            if star_number and not group_id:
                group_id = StarGroup.get_group_for_star(star_number)
            
            # 特定の星/グループと月の方位データを取得
            if group_id and month:
                direction = repo.get_by_group_and_month(group_id, month)
                if not direction:
                    return jsonify({'error': '指定された条件の方位データが見つかりません'}), 404
                
                return jsonify(direction.to_dict()), 200
                
            # 特定の星/グループの全ての月の方位データを取得
            elif group_id:
                directions = repo.list_by_group(group_id)
                if not directions:
                    return jsonify({'error': '指定されたグループの方位データが見つかりません'}), 404
                
                return jsonify({
                    'group_id': group_id,
                    'directions': [direction.to_dict() for direction in directions]
                }), 200
            
            # 特定の月の全てのグループの方位データを取得
            elif month:
                directions = repo.list_by_month(month)
                if not directions:
                    return jsonify({'error': f'{month}月の方位データが見つかりません'}), 404
                
                return jsonify([direction.to_dict() for direction in directions]), 200
            
            else:
                # 全てのグループ（1-3）の方位データを返す
                result = {}
                for group_id in range(1, 4):
                    directions = repo.list_by_group(group_id)
                    if directions:
                        group = db.session.query(StarGroup).filter_by(group_id=group_id).first()
                        result[group_id] = {
                            'group_id': group_id,
                            'directions': [direction.to_dict() for direction in directions]
                        }
                
                return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"月盤方位データ取得エラー: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @monthly_bp.route('/directions', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def create_monthly_direction():
        """月盤の方位データを登録するAPI"""
        try:
            data = request.get_json()
            
            # 星番号またはグループIDのどちらかが必要
            star_number = data.get('star')
            group_id = data.get('group_id')
            
            # 星番号からグループIDを取得（優先的に使用）
            if star_number and not group_id:
                group_id = StarGroup.get_group_for_star(star_number)
                data['group_id'] = group_id
            
            required_fields = ['group_id', 'month', 'center_star']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'必須フィールド {field} がありません'}), 400
            
            # 既存データの確認
            existing = MonthlyDirections.get_monthly_directions_by_group(
                data['group_id'], data['month']
            )
            
            if existing:
                # 既存データの更新
                for key, value in data.items():
                    if hasattr(existing, key) and key != 'star':  # star_numberは使用しない
                        setattr(existing, key, value)
                
                db.session.commit()
                logger.info(f"月盤方位データを更新しました: グループ={data['group_id']}, 月={data['month']}")
                return jsonify({
                    'message': '月盤方位データを更新しました',
                    'direction': existing.to_dict()
                }), 200
            
            # 新規データの作成
            new_direction = MonthlyDirections(
                group_id=data['group_id'],
                month=data['month'],
                center_star=data['center_star']
            )
            
            # その他のフィールドを設定
            for key, value in data.items():
                if key not in required_fields and key != 'star' and hasattr(new_direction, key):
                    setattr(new_direction, key, value)
            
            db.session.add(new_direction)
            db.session.commit()
            
            logger.info(f"月盤方位データを作成しました: グループ={data['group_id']}, 月={data['month']}")
            return jsonify({
                'message': '月盤方位データを作成しました',
                'direction': new_direction.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"月盤方位データ作成エラー: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @monthly_bp.route('/directions/<int:direction_id>', methods=['PUT'])
    @jwt_required()
    @permission_required('data_management')
    def update_monthly_direction(direction_id):
        """月盤の方位データを更新するAPI"""
        try:
            data = request.get_json()
            direction = MonthlyDirections.query.get(direction_id)
            
            if not direction:
                return jsonify({'error': '指定された方位データが見つかりません'}), 404
            
            # 星番号が指定された場合はグループIDに変換
            if 'star' in data and not 'group_id' in data:
                data['group_id'] = StarGroup.get_group_for_star(data['star'])
            
            # フィールドの更新
            for key, value in data.items():
                if hasattr(direction, key) and key != 'star':  # star_numberは使用しない
                    setattr(direction, key, value)
            
            db.session.commit()
            
            logger.info(f"月盤方位データを更新しました: ID={direction_id}")
            return jsonify({
                'message': '月盤方位データを更新しました',
                'direction': direction.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"月盤方位データ更新エラー: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @monthly_bp.route('/star-groups', methods=['GET'])
    def get_star_groups():
        """星のグループ情報を取得するAPI"""
        try:
            groups = StarGroup.query.order_by(StarGroup.group_id).all()
            result = [group.to_dict() for group in groups]
            return jsonify(result), 200
        
        except Exception as e:
            logger.error(f"星グループ取得エラー: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @monthly_bp.route('/get-star-group/<int:star_number>', methods=['GET'])
    def get_star_group(star_number):
        """特定の星のグループ情報を取得するAPI"""
        try:
            if not 1 <= star_number <= 9:
                return jsonify({'error': '有効な星番号（1-9）を指定してください'}), 400
                
            group_id = StarGroup.get_group_for_star(star_number)
            group = db.session.query(StarGroup).filter_by(group_id=group_id).first()
            
            if not group:
                return jsonify({'error': 'グループが見つかりません'}), 404
            
            return jsonify(group.to_dict()), 200
            
        except Exception as e:
            logger.error(f"星グループ取得エラー: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @monthly_bp.route('/batch-import', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def batch_import_monthly_data():
        """月盤データの一括インポートAPI"""
        try:
            data = request.get_json()
            
            if not data or not isinstance(data, list):
                return jsonify({'error': 'データは配列形式で送信してください'}), 400
            
            created_count = 0
            updated_count = 0
            
            for item in data:
                # 必須フィールドの確認
                required_fields = ['group_id', 'month', 'center_star']
                missing_fields = [field for field in required_fields if field not in item]
                if missing_fields:
                    return jsonify({'error': f'必須フィールドがありません: {", ".join(missing_fields)}'}), 400
                
                # 既存データの確認
                existing = MonthlyDirections.get_monthly_directions_by_group(
                    item['group_id'], item['month']
                )
                
                if existing:
                    # 既存データの更新
                    for key, value in item.items():
                        if hasattr(existing, key) and key != 'star':
                            setattr(existing, key, value)
                    updated_count += 1
                else:
                    # 新規データの作成
                    new_direction = MonthlyDirections(
                        group_id=item['group_id'],
                        month=item['month'],
                        center_star=item['center_star']
                    )
                    
                    # その他のフィールドを設定
                    for key, value in item.items():
                        if key not in required_fields and key != 'star' and hasattr(new_direction, key):
                            setattr(new_direction, key, value)
                    
                    db.session.add(new_direction)
                    created_count += 1
            
            db.session.commit()
            
            return jsonify({
                'message': '月盤データの一括インポートが完了しました',
                'created': created_count,
                'updated': updated_count
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"月盤データ一括インポートエラー: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # ─────────────────────────────────────────────────────────────
    # 新エンドポイント: 연/월 기준 동적 월반 방위 산출 (Phase 1 기반 로직)
    # ─────────────────────────────────────────────────────────────
    @monthly_bp.route('/monthly-board', methods=['GET'])
    @jwt_required()
    @inject
    def get_monthly_board(
        use_case: MonthlyDirectionsUseCase,
        stone_use_case: PowerStoneRecommendationUseCase,
        six_layer_use_case: SixLayerPowerStoneUseCase,
    ):
        """연/월 기준 월반(月盤) 방위 길흉 결과를 반환하는 API.

        Query Parameters:
            main_star (int, 필수): 사용자 본명성 (1~9)
            month_star (int, 필수): 사용자 월명성 (1~9)
            year (int, 필수): 조회 연도 (예: 2026)
            month_index (int, 選択): 조회 절월 인덱스 (1=寅月/立春 … 12=丑月/小寒). 
                None の場合、該当年の全節月について月盤方位を算出する。
            lang (str, 選択): 응답 언어 코드 (ja/ko/en). 기본값: ja.
            birth_date (str, 選択): 생년월일 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM). 제공 시 6-Layer 파워스톤 응답.

        Returns:
            200 OK: {
                "main_star": int,
                "month_star": int,
                "target_year": int,
                "year_center_star": int,
                "year_zodiac": str,
                "monthly_boards": {
                    "setsu_month_1": {
                        "setsu_month_index": int,
                        "center_star": int,
                        "month_zodiac": str,
                        "period_start": str,
                        "period_end": str,
                        "directions": { ... },
                        "power_stones": {            # nullable — 길방위 없는 경우 null
                            # birth_date 미제공 시 (3-Layer):
                            "base_stone": { ... },
                            "monthly_stone": { ... },
                            "protection_stone": { ... }

                            # birth_date 제공 시 (6-Layer):
                            # "overall_stone": { stone_id, stone_name, layer, description, secondary },
                            # "health_stone":  { stone_id, stone_name, layer, description, secondary },
                            # "wealth_stone":  { stone_id, stone_name, layer, description, secondary },
                            # "love_stone":    { stone_id, stone_name, layer, description, secondary },
                            # "monthly_stone": { stone_id, stone_name, layer, gogyo, reason },
                            # "protection_stone": { stone_id, stone_name, layer, gogyo, reason },
                            # "life_path_number": int,
                            # "planet": str
                        } | null
                    },
                    ...
                }
            }
            400 Bad Request: 필수 파라미터 누락
            422 Unprocessable Entity: 파라미터 값이 범위 밖
            500 Internal Server Error
        """
        try:
            main_star = request.args.get('main_star', type=int)
            month_star = request.args.get('month_star', type=int)
            year = request.args.get('year', type=int)
            month_index = request.args.get('month_index', type=int)

            # ── lang 파라미터 파싱 (기본값: ja) ────────────────
            lang_raw = request.args.get('lang', 'ja')
            try:
                locale = Locale(lang_raw)
            except ValueError:
                locale = Locale.JA
            locale_str: str = locale.value

            # ── birth_date 파라미터 (6-Layer 활성화) ──────
            birth_date = request.args.get('birth_date', type=str)
            if birth_date is not None and not birth_date.strip():
                return jsonify({
                    'error': 'birth_date 가 비어 있습니다 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM 필요)',
                }), 422

            # 구형 파라미터인 'month'가 어떤 형태로든 전달되면 요청을 거절한다.
            if request.args.get('month') is not None:
                return jsonify({'error': "파라미터 체계가 변경되었습니다. 'month' 대신 'month_index'를 사용해주세요."}), 400

            # ── 필수 파라미터 검증 ─────────────────────────────
            missing = [k for k, v in {'main_star': main_star, 'month_star': month_star, 'year': year}.items() if v is None]
            if missing:
                return jsonify({'error': f'필수 파라미터 누락: {", ".join(missing)}'}), 400

            # ── 범위 검증 ──────────────────────────────────────
            if not 1 <= main_star <= 9:
                return jsonify({'error': 'main_star は 1~9 の範囲で指定してください'}), 422
            if not 1 <= month_star <= 9:
                return jsonify({'error': 'month_star は 1~9 の範囲で指定してください'}), 422
            if month_index is not None and not 1 <= month_index <= 12:
                return jsonify({'error': 'month_index は 1~12 の範囲で指定してください'}), 422

            # ── 유즈케이스 실행 ────────────────────────────────
            result = use_case.execute(
                main_star=main_star,
                month_star=month_star,
                target_year=year,
                target_month=month_index,
            )

            # ── 파워스톤 추천 추가 ────────────────────────────
            # 수비술 부분은 월에 불변이므로 루프 밖에서 1회만 계산
            numerology_stones = None
            if birth_date:
                try:
                    numerology_stones = six_layer_use_case.compute_numerology_stones(
                        birth_date=birth_date,
                        locale=locale_str,
                    )
                except ValueError:
                    return jsonify({
                        'error': 'birth_date 형식이 올바르지 않습니다 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM 필요)',
                    }), 422

            for key, board in result.get('monthly_boards', {}).items():
                directions = board.get('directions', {})
                if directions:
                    try:
                        gogyo_result = stone_use_case.execute(
                            main_star=main_star,
                            directions=directions,
                            locale=locale_str,
                        )
                        if numerology_stones:
                            # 6-Layer: 수비술 4 + 구성기학 2
                            board['power_stones'] = six_layer_use_case.merge_six_layer(
                                gogyo_result, numerology_stones,
                            )
                        else:
                            board['power_stones'] = gogyo_result
                    except NoAuspiciousDirectionError:
                        logger.info(
                            "monthly-board %s: 길방위 없음 → power_stones=%s",
                            key,
                            "numerology-only" if numerology_stones else "null",
                        )
                        if numerology_stones:
                            board['power_stones'] = six_layer_use_case.merge_six_layer_partial(
                                numerology_stones,
                            )
                        else:
                            board['power_stones'] = None
                else:
                    if numerology_stones:
                        board['power_stones'] = six_layer_use_case.merge_six_layer_partial(
                            numerology_stones,
                        )
                    else:
                        board['power_stones'] = None

            return jsonify(result), 200

        except ValueError as e:
            logger.warning("monthly-board API ValueError: %s", e)
            return jsonify({'error': str(e)}), 422
        except NineStarKiError as e:
            logger.warning("monthly-board API NineStarKiError: %s (code=%s)", e, e.code)
            return jsonify(e.to_dict()), e.status
        except Exception as e:
            logger.error("monthly-board API エラー: %s", e, exc_info=True)
            return jsonify({'error': '内部エラーが発生しました。'}), 500

    return monthly_bp