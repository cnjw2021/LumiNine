"""Solar data management routes blueprint for NineStarKi."""

from flask import Blueprint, request, jsonify, Response
import json
from datetime import datetime
from flask_jwt_extended import jwt_required
from core.database import db
from core.models.solar_starts import SolarStarts
from flask_injector import inject
from apps.ninestarki.use_cases.solar_admin_use_cases import ListSolarTermsUseCase, UpdateSolarTermUseCase
from core.utils.logger import get_logger
from core.auth.auth_utils import permission_required

logger = get_logger(__name__)

def create_solar_bp():
    solar_bp = Blueprint('solar', __name__, url_prefix='/api/admin/solar')

    @solar_bp.route('/solar-starts', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    def get_solar_starts():
        """立春データを取得するAPI"""
        try:
            solar_starts = SolarStarts.query.all()
            result = [
                {
                    "id": solar_start.year,
                    "year": solar_start.year,
                    "datetime": datetime.combine(solar_start.solar_starts_date, solar_start.solar_starts_time).isoformat(),
                    "created_at": solar_start.created_at.isoformat(),
                    "updated_at": solar_start.updated_at.isoformat()
                } for solar_start in solar_starts
            ]
            
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"Error getting solar starts: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @solar_bp.route('/solar-starts/<int:year>', methods=['PUT'])
    @jwt_required()
    @permission_required('data_management')
    def update_solar_start(year):
        """立春データを更新するAPI"""
        try:
            solar_start = SolarStarts.query.filter_by(year=year).first()
            if not solar_start:
                return jsonify({'error': '指定された立春データが見つかりません'}), 404
            
            data = request.get_json()
            if 'datetime' in data:
                dt = datetime.fromisoformat(data['datetime'])
                solar_start.solar_starts_date = dt.date()
                solar_start.solar_starts_time = dt.time()
            
            db.session.commit()
            
            return jsonify({
                'message': '立春データを更新しました',
                'solar_start': {
                    'id': solar_start.year,
                    'year': solar_start.year,
                    'datetime': datetime.combine(solar_start.solar_starts_date, solar_start.solar_starts_time).isoformat(),
                    'created_at': solar_start.created_at.isoformat(),
                    'updated_at': solar_start.updated_at.isoformat()
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating solar start: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @solar_bp.route('/solar-terms', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    @inject
    def get_solar_terms(list_uc: ListSolarTermsUseCase):
        """二十四節気データを取得するAPI"""
        try:
            solar_terms = list_uc.execute()
            result = [
                {
                    "year": st["year"],
                    "month": st["month"],
                    "term_name": st["term_name"],
                    "datetime": (f"{st['date']}T{st['time']}" if st["time"] else f"{st['date']}T00:00:00"),
                } for st in solar_terms
            ]
            
            return Response(
                json.dumps(result, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            logger.error(f"Error getting solar terms: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @solar_bp.route('/solar-terms/<int:term_id>', methods=['PUT'])
    @jwt_required()
    @permission_required('data_management')
    @inject
    def update_solar_term(term_id, update_uc: UpdateSolarTermUseCase):
        """二十四節気データを更新するAPI"""
        try:
            # 先に存在確認
            exists = update_uc.execute(term_id)
            if exists is None:
                return jsonify({'error': '指定された節気データが見つかりません'}), 404
            
            data = request.get_json()
            updated = update_uc.execute(
                term_id,
                year=data.get('year'),
                month=data.get('month'),
                term_name=data.get('term_name'),
                dt_iso=data.get('datetime'),
            )
            if not updated:
                return jsonify({'error': '更新に失敗しました'}), 400
            
            return jsonify({
                'message': '節気データを更新しました',
                'solar_term': {
                    'year': updated['year'],
                    'month': updated['month'],
                    'term_name': updated['term_name'],
                    'datetime': (f"{updated['date']}T{updated['time']}" if updated['time'] else f"{updated['date']}T00:00:00"),
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating solar term: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return solar_bp 