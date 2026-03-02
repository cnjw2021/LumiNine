"""Admin routes blueprint for NineStarKi."""

from flask import Blueprint, request, jsonify, Response
import json
from flask_jwt_extended import jwt_required
from core.database import db
from apps.ninestarki.domain.entities.nine_star import NineStar
from core.models.star_attribute import StarAttribute
from core.utils.logger import get_logger
from core.auth.auth_utils import permission_required
from core.models.daily_astrology import DailyAstrology
from core.models.stellar_cycle import StellarCycle
from datetime import datetime, date, timedelta
from sqlalchemy import text

logger = get_logger(__name__)

def create_admin_bp():
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

    @admin_bp.route('/stars', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    def get_stars():
        """九星データを取得するAPI"""
        try:
            stars = NineStar.query.all()
            result = {
                "stars": [
                    {
                        "id": star.star_number,
                        "star_number": star.star_number,
                        "name": star.name_jp,
                        "element": star.element,
                        "created_at": star.created_at.isoformat(),
                        "updated_at": star.updated_at.isoformat()
                    } for star in stars
                ]
            }
            
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"Error getting stars: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/star-attribute', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def create_star_attribute():
        """九星属性データを作成するAPI"""
        try:
            data = request.get_json()
            
            # 必須フィールドの確認
            required_fields = ['star_number', 'attribute_type', 'attribute_value']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # 九星番号の検証
            star_number = int(data['star_number'])
            if not (1 <= star_number <= 9):
                return jsonify({'error': 'star_number must be between 1 and 9'}), 400
            
            # 既存のデータがあるかチェック
            existing_attribute = StarAttribute.query.filter_by(
                star_number=star_number,
                attribute_type=data['attribute_type'],
                attribute_value=data['attribute_value']
            ).first()
            
            if existing_attribute:
                # 既存データの更新
                existing_attribute.description = data.get('description')
                existing_attribute.weight = data.get('weight', 1)
                
                db.session.commit()
                
                return jsonify({
                    'message': '九星属性データを更新しました',
                    'attribute': existing_attribute.to_dict()
                }), 200
            else:
                # 新規データの作成
                new_attribute = StarAttribute(
                    star_number=star_number,
                    attribute_type=data['attribute_type'],
                    attribute_value=data['attribute_value'],
                    description=data.get('description'),
                    weight=data.get('weight', 1)
                )
                
                db.session.add(new_attribute)
                db.session.commit()
                
                return jsonify({
                    'message': '九星属性データを作成しました',
                    'attribute': new_attribute.to_dict()
                }), 201
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating star attribute: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/star-attribute-batch', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def batch_create_star_attribute():
        """九星属性データを一括作成するAPI"""
        try:
            data = request.get_json()
            
            if not data or 'attributes' not in data or not isinstance(data['attributes'], list):
                return jsonify({'error': 'Invalid data format. Expected "attributes" as a list.'}), 400
            
            # 結果を追跡
            results = {
                'created': 0,
                'updated': 0,
                'failed': 0,
                'errors': []
            }
            
            # 各属性データを処理
            for item in data['attributes']:
                try:
                    # 必須フィールドの確認
                    required_fields = ['star_number', 'attribute_type', 'attribute_value']
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f'Missing required field: {field}')
                    
                    # 九星番号の値を検証
                    star_number = int(item['star_number'])
                    
                    if not (1 <= star_number <= 9):
                        raise ValueError('star_number must be between 1 and 9')
                    
                    # 既存のデータがあるかチェック
                    existing_attribute = StarAttribute.query.filter_by(
                        star_number=star_number,
                        attribute_type=item['attribute_type'],
                        attribute_value=item['attribute_value']
                    ).first()
                    
                    if existing_attribute:
                        # 既存データの更新
                        existing_attribute.description = item.get('description')
                        existing_attribute.weight = item.get('weight', 1)
                        results['updated'] += 1
                    else:
                        # 新規データの作成
                        new_attribute = StarAttribute(
                            star_number=star_number,
                            attribute_type=item['attribute_type'],
                            attribute_value=item['attribute_value'],
                            description=item.get('description'),
                            weight=item.get('weight', 1)
                        )
                        
                        db.session.add(new_attribute)
                        results['created'] += 1
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'data': item,
                        'error': str(e)
                    })
            
            # トランザクション完了
            db.session.commit()
            
            logger.info(f"Batch process completed: {results['created']} created, {results['updated']} updated, {results['failed']} failed")
            return jsonify({
                'message': 'Batch process completed',
                'results': results
            }), 200
                
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/stars/<int:star_id>', methods=['PUT'])
    @jwt_required()
    @permission_required('data_management')
    def update_star(star_id):
        """九星データを更新するAPI"""
        try:
            star = NineStar.query.filter_by(star_number=star_id).first()
            if not star:
                return jsonify({'error': '指定された九星が見つかりません'}), 404
            
            data = request.get_json()
            if 'name' in data:
                star.name_jp = data['name']
            if 'element' in data:
                star.element = data['element']
            
            db.session.commit()
            
            return jsonify({
                'message': '九星データを更新しました',
                'star': {
                    'id': star.star_number,
                    'star_number': star.star_number,
                    'name': star.name_jp,
                    'element': star.element,
                    'created_at': star.created_at.isoformat(),
                    'updated_at': star.updated_at.isoformat()
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating star: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/star-attributes', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    def get_star_attributes():
        """九星属性データを取得するAPI"""
        try:
            star_number = request.args.get('star_number')
            attribute_type = request.args.get('type')
            
            # クエリの構築
            query = StarAttribute.query
            
            if star_number:
                try:
                    star_number = int(star_number)
                    query = query.filter(StarAttribute.star_number == star_number)
                except ValueError:
                    return jsonify({'error': 'star_number must be an integer'}), 400
                    
            if attribute_type:
                query = query.filter(StarAttribute.attribute_type == attribute_type)
                
            # 重要度順でソート
            query = query.order_by(StarAttribute.weight.desc())
            
            attributes = query.all()
            result = [attr.to_dict() for attr in attributes]
            
            return jsonify({
                'attributes': result,
                'count': len(result)
            }), 200
                
        except Exception as e:
            logger.error(f"Error getting star attributes: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @admin_bp.route('/star-attributes/<int:attribute_id>', methods=['PUT'])
    @jwt_required()
    @permission_required('data_management')
    def update_star_attribute(attribute_id):
        """九星属性データを更新するAPI"""
        try:
            attribute = StarAttribute.query.get(attribute_id)
            if not attribute:
                return jsonify({'error': '指定された属性データが見つかりません'}), 404
                
            data = request.get_json()
            
            # 更新可能なフィールド
            updateable_fields = ['attribute_type', 'attribute_value', 'description', 'weight']
            
            for field in updateable_fields:
                if field in data:
                    setattr(attribute, field, data[field])
            
            db.session.commit()
            
            return jsonify({
                'message': '九星属性データを更新しました',
                'attribute': attribute.to_dict()
            }), 200
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating star attribute: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    @admin_bp.route('/star-attributes/<int:attribute_id>', methods=['DELETE'])
    @jwt_required()
    @permission_required('data_management')
    def delete_star_attribute(attribute_id):
        """九星属性データを削除するAPI"""
        try:
            attribute = StarAttribute.query.get(attribute_id)
            if not attribute:
                return jsonify({'error': '指定された属性データが見つかりません'}), 404
                
            db.session.delete(attribute)
            db.session.commit()
            
            return jsonify({
                'message': '九星属性データを削除しました',
                'id': attribute_id
            }), 200
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting star attribute: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @admin_bp.route('/initialize-astrology-data/<int:start_year>/<int:end_year>', methods=['POST'])
    @jwt_required()
    def initialize_astrology_data(start_year, end_year):
        """指定された年の日付ごとの干支と九星のデータを初期化する"""
        try:
            # 失敗した年度を記録するリスト
            failed_years = []
            
            for year in range(start_year, end_year + 1):
                cycle_data = StellarCycle.get_cycle_by_year_sync(year)
                if not cycle_data:
                    logger.error(f"{year}年の周期データの取得に失敗しました")
                    failed_years.append(year)
                    continue

                # 新しいテーブル構造からデータを取得
                first_ascending_date = cycle_data.get('first_ascending_phase_date')
                first_descending_date = cycle_data.get('first_descending_phase_date')
                second_ascending_date = cycle_data.get('second_ascending_phase_date')

                # ログ出力
                logger.info(f"{year}年の周期データ取得: 初回陽遁日={first_ascending_date}, 隠遁日={first_descending_date}, 二回目陽遁日={second_ascending_date}")

                # データ整合性チェック
                if not first_descending_date:
                    logger.error(f"{year}年の隠遁開始日データがありません")
                    failed_years.append(year)
                    continue

                # 1月1日から12月31日までのデータを登録
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
                current_date = start_date

                # 既存のデータを削除
                DailyAstrology.query.filter(
                    DailyAstrology.year == year
                ).delete()

                while current_date <= end_date:
                    # 干支を計算
                    eto = calculate_ilgan_ilsi(current_date)
                
                    # 九星を計算（新しい引数構造に合わせて）
                    nine_star = calculate_nine_star(
                        current_date,
                        first_ascending_date,
                        first_descending_date,
                        second_ascending_date
                    )

                    # データベースに登録
                    astrology = DailyAstrology(
                        date=current_date,
                        zodiac=eto,
                        star_number=nine_star
                    )
                    db.session.add(astrology)

                    # 次の日へ
                    current_date += timedelta(days=1)

                # 各年ごとにコミット
                db.session.commit()
                logger.info(f"{year}年のデータの初期化が完了しました")

            # すべての年の処理完了後にレスポンスを返す
            return jsonify({
                'status': 'success',
                'message': f"{start_year}~{end_year}年のデータの初期化が完了しました",
                'failed_years': failed_years
            })

        except Exception as e:
            logger.error(f"データの初期化中にエラーが発生しました: {str(e)}")
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'データの初期化中にエラーが発生しました: {str(e)}'
            }), 500

    @admin_bp.route('/daily-astrology', methods=['GET'])
    @jwt_required()
    def get_daily_astrology():
        """日付ごとの干支と九星のデータを取得するAPI"""
        try:
            year = request.args.get('year', type=int)
            month = request.args.get('month', type=int)
            day = request.args.get('day', type=int)
            limit = request.args.get('limit', 100, type=int)  # デフォルトは100件
            
            # クエリの構築
            query = DailyAstrology.query
            
            if year:
                query = query.filter(DailyAstrology.year == year)
            if month:
                query = query.filter(DailyAstrology.month == month)
            if day:
                query = query.filter(DailyAstrology.day == day)
                
            # 日付順に並べ替え
            query = query.order_by(DailyAstrology.date)
            
            # 件数制限
            if limit:
                query = query.limit(limit)
                
            daily_data = query.all()
            result = [data.to_dict() for data in daily_data]
            
            return jsonify(result)
                
        except Exception as e:
            logger.error(f"Error getting daily astrology data: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def calculate_ilgan_ilsi(target_date: date) -> str:
        """指定された日付の干支を計算する（韓国式）
        
        Args:
            target_date: 計算対象の日付
            
        Returns:
            str: 干支（例：甲子）
        """
        # 天干（10個）
        heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        # 地支（12個）
        earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 基準日（1900年1月31日）の干支は甲午
        base_date = date(1900, 1, 31)
        base_stem_index = 0  # 甲
        base_branch_index = 6  # 午
        
        # 基準日からの経過日数を計算
        days_diff = (target_date - base_date).days
        
        # 天干と地支のインデックスを計算
        stem_index = (base_stem_index + days_diff) % 10
        branch_index = (base_branch_index + days_diff) % 12
        
        # 干支を組み合わせて返す
        return heavenly_stems[stem_index] + earthly_branches[branch_index]

    def calculate_nine_star(date_to_calculate, first_ascending_date, first_descending_date, second_ascending_date):
        """
        日付から九星を計算する関数
    
        ルール：
        1. first_ascending_phase_date (初回目の陽遁開始日: Nullable)
           1/1〜初回目の陽遁開始日: 初回目の陽遁日前日を起点にして、1/1向けに 1→2→...→9→1...と増加
           初回目の陽遁開始日〜初回目の隠遁開始前日: 初回目の陽遁日起点にして、1→2→...→9→1...と増加
        2. first_descending_phase_date (隠遁開始日: Not Null)
           1) first_ascending_phase_dateが存在しない場合
              1/1〜隠遁開始日前日: 隠遁日前日を起点として、1/1向けに 1→2→...→9→1...と増加
           2) second_ascending_phase_dateが存在する場合
              隠遁開始日〜2回目の陽遁開始前日: 隠遁日起点として、9→8→...→1→9...と減少
           3) second_ascending_phase_dateが存在しない場合
              隠遁開始日〜12/31: 隠遁日起点として、9→8→...→1→9...と減少
        3. second_ascending_phase_date (2回目の陽遁開始日: Nullable)
           陽遁開始日〜12/31: 2回目陽遁日起点として、1→2→...→9→1...と増加
        
        パターン1)
          first_ascending_phase_date: null
          first_descending_phase_date: 1980/06/20
          second_ascending_phase_date: 1980/12/17

          ...
          1980/06/17: 7
          1980/06/18: 8
          1980/06/19: 9
          1980/06/20: 9
          1980/06/21: 8
          1980/06/22: 7
          ...
          1980/12/14: 3
          1980/12/15: 2
          1980/12/16: 1
          1980/12/17: 1
          1980/12/18: 2
          1980/12/19: 3
  
        パターン2)
          first_ascending_phase_date: 1976/01/13
          first_descending_phase_date: 1976/07/11
          second_ascending_phase_date: null
  
          ...
          1976/01/10: 3
          1976/01/11: 2
          1976/01/12: 1
          1976/01/13: 1
          1976/01/14: 2
          1976/01/15: 3
          ...
          1976/07/09: 8
          1976/07/10: 9
          1976/07/11: 9
          1976/07/12: 8
          1976/07/13: 7
          ...
          1976/12/29: 9
          1976/12/30: 8
          1976/12/31: 7
  
        パターン3)
          first_ascending_phase_date: 1978/01/02
          first_descending_phase_date: 1978/07/01
          second_ascending_phase_date: 1978/12/28
  
          ...
          1978/01/01: 1
          1978/01/02: 1
          1978/01/03: 2
          1978/01/04: 3
          ...
          1978/06/29: 8
          1978/06/30: 9
          1978/07/01: 9
          1978/07/02: 8
          1978/07/03: 7
          ...
          1978/12/25: 3
          1978/12/26: 2
          1978/12/27: 1
          1978/12/28: 1
          1978/12/29: 2
          1978/12/30: 3
        """
        # 年の最初と最後の日を取得
        target_year = date_to_calculate.year
        year_start = date(target_year, 1, 1)
        
        # 特別な日の前日を計算
        day_before_first_descending = first_descending_date - timedelta(days=1)
        day_before_first_ascending = first_ascending_date - timedelta(days=1) if first_ascending_date else None
        day_before_second_ascending = second_ascending_date - timedelta(days=1) if second_ascending_date else None

        # 特別な日チェック
        # 隠遁開始日前日は必ず9
        if date_to_calculate == day_before_first_descending:
            return 9
        
        # 期間判定
        # パターン3: 初回陽遁日あり、隠遁日あり、二回目陽遁日あり
        if first_ascending_date and first_descending_date and second_ascending_date:
            if year_start <= date_to_calculate < first_ascending_date:
                # 1/1～初回陽遁開始日前日: 初回目の陽遁日前日を起点にして、1/1向けに 1→2→...→9→1...と増加
                days_before = (day_before_first_ascending - date_to_calculate).days
                star_number = (days_before % 9) + 1
                return star_number
            elif first_ascending_date <= date_to_calculate < first_descending_date:
                # 初回陽遁開始日～隠遁開始日前日: 初回陽遁日起点で増加
                days_from_ascending = (date_to_calculate - first_ascending_date).days
                return (days_from_ascending % 9) + 1
            elif first_descending_date <= date_to_calculate < second_ascending_date:
                # 隠遁開始日～2回目陽遁開始日前日: 隠遁日起点で減少
                days_from_descending = (date_to_calculate - first_descending_date).days
                star_number = 9 - (days_from_descending % 9)
                if star_number == 0:
                    star_number = 9
                return star_number
            else:  # second_ascending_date <= date_to_calculate
                # 2回目陽遁開始日～12/31: 2回目陽遁日起点で増加
                days_from_ascending = (date_to_calculate - second_ascending_date).days
                return (days_from_ascending % 9) + 1
        
        # パターン2: 初回陽遁日あり、隠遁日あり、二回目陽遁日なし 
        elif first_ascending_date and first_descending_date and not second_ascending_date:
            if year_start <= date_to_calculate < first_ascending_date:
                # 1/1～初回陽遁開始日前日: 初回目の陽遁日前日を起点にして、1/1向けに 1→2→...→9→1...と増加
                days_before = (day_before_first_ascending - date_to_calculate).days
                star_number = (days_before % 9) + 1
                return star_number
            elif first_ascending_date <= date_to_calculate < first_descending_date:
                # 初回陽遁開始日～隠遁開始日前日: 初回陽遁日起点で増加
                days_from_ascending = (date_to_calculate - first_ascending_date).days
                return (days_from_ascending % 9) + 1
            else:  # first_descending_date <= date_to_calculate
                # 隠遁開始日～12/31: 隠遁日起点で減少
                days_from_descending = (date_to_calculate - first_descending_date).days
                star_number = 9 - (days_from_descending % 9)
                if star_number == 0:
                    star_number = 9
                return star_number
        
        # パターン1: 初回陽遁日なし、隠遁日あり、二回目陽遁日あり
        elif not first_ascending_date and first_descending_date and second_ascending_date:
            if year_start <= date_to_calculate < first_descending_date:
                # 1/1～隠遁開始日前日: 隠遁日前日起点で1/1に向かって減少
                days_before = (day_before_first_descending - date_to_calculate).days
                star_number = 9 - (days_before % 9)
                if star_number == 0:
                    star_number = 9
                return star_number
            elif first_descending_date <= date_to_calculate < second_ascending_date:
                # 隠遁開始日～2回目陽遁開始日前日: 隠遁日起点で減少
                days_from_descending = (date_to_calculate - first_descending_date).days
                star_number = 9 - (days_from_descending % 9)
                if star_number == 0:
                    star_number = 9
                return star_number
            else:  # second_ascending_date <= date_to_calculate
                # 2回目陽遁開始日～12/31: 2回目陽遁日起点で増加
                days_from_ascending = (date_to_calculate - second_ascending_date).days
                return (days_from_ascending % 9) + 1
        
        # その他のパターン: 少なくとも隠遁日はある前提
        else:
            if year_start <= date_to_calculate < first_descending_date:
                # 1/1～隠遁開始日前日: 隠遁日前日起点で1/1に向かって減少
                days_before = (day_before_first_descending - date_to_calculate).days
                star_number = 9 - (days_before % 9)
                if star_number == 0:
                    star_number = 9
                return star_number
            else:  # first_descending_date <= date_to_calculate
                # 隠遁開始日～12/31: 隠遁日起点で減少
                days_from_descending = (date_to_calculate - first_descending_date).days
                star_number = 9 - (days_from_descending % 9)
                if star_number == 0:
                    star_number = 9
                return star_number

    return admin_bp 