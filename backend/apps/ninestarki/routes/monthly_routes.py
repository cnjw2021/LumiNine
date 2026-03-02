"""月盤データのAPIルート"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from core.database import db
from apps.ninestarki.domain.repositories.monthly_directions_repository_interface import IMonthlyDirectionsRepository
from core.models.star_groups import StarGroup
from flask_injector import inject
from core.auth.auth_utils import permission_required
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_monthly_bp():
    """月盤データのBlueprint作成"""
    monthly_bp = Blueprint('monthly', __name__)
    
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
            
    return monthly_bp 