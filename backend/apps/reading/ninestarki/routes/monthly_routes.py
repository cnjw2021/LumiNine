"""月盤データのAPIルート"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from apps.reading.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
from apps.reading.powerstone.use_cases.powerstone_recommendation_use_case import PowerStoneRecommendationUseCase
from apps.reading.powerstone.use_cases.six_layer_powerstone_use_case import SixLayerPowerStoneUseCase
from apps.reading.shared.domain.exceptions import NineStarKiError
from apps.reading.ninestarki.domain.value_objects.locale import Locale
from flask_injector import inject
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_monthly_bp():
    """月盤データのBlueprint作成"""
    monthly_bp = Blueprint('monthly', __name__, url_prefix='/api/monthly')

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
                        "power_stones": {
                            # (A) birth_date 미제공 + 길방위 있음 → 3-Layer:
                            #   base_stone, monthly_stone, protection_stone
                            #
                            # (B) birth_date 제공 + 길방위 있음 → 6-Layer 완전:
                            #   overall_stone, health_stone, wealth_stone, love_stone,
                            #   monthly_stone, protection_stone,
                            #   life_path_number, planet
                            #
                            # (C) birth_date 제공 + 길방위 없음(흉방위만) → 6-Layer:
                            #   overall_stone, health_stone, wealth_stone, love_stone,
                            #   monthly_stone=null, protection_stone={...},
                            #   life_path_number, planet
                            #
                            # (C') birth_date 미제공 + 길방위 없음(흉방위만) → 3-Layer:
                            #   base_stone, monthly_stone=null, protection_stone
                            #
                            # (D) directions 자체가 비어있음 → null 또는 수비술 전용
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
                        target_year=year,
                    )
                except ValueError:
                    return jsonify({
                        'error': 'birth_date 형식이 올바르지 않습니다 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM 필요)',
                    }), 422

            def _numerology_fallback():
                """월盤 `/monthly-board` 응답에서 `directions`가 비어있을 때의 fallback 헬퍼.

                수비술 스톤이 있으면 수비술 4~5-Layer(target_year 제공 시 yearly 포함)만 반환, 없으면 None.
                이 경로에서 `monthly_stone` / `protection_stone` 은 항상 `null` 이다.
                """
                if numerology_stones:
                    return six_layer_use_case.merge_six_layer_partial(numerology_stones)
                return None

            for key, board in result.get('monthly_boards', {}).items():
                directions = board.get('directions', {})
                if directions:
                    # NoAuspiciousDirectionError는 엔진 내부에서 처리됨
                    # → monthly_stone=None 가능, protection_stone은 정상 반환
                    gogyo_result = stone_use_case.execute(
                        main_star=main_star,
                        directions=directions,
                        locale=locale_str,
                    )
                    if numerology_stones:
                        # 7-Layer: 수비술 5 + 구성기학 2
                        board['power_stones'] = six_layer_use_case.merge_seven_layer(
                            gogyo_result, numerology_stones,
                        )
                    else:
                        board['power_stones'] = gogyo_result
                else:
                    board['power_stones'] = _numerology_fallback()

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