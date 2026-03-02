from datetime import datetime
from typing import Optional, Dict, Any
from injector import inject

from core.utils.logger import get_logger
from core.models.daily_astrology import DailyAstrology
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository
from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository


logger = get_logger(__name__)


class DailyStarReadingUseCase:
    """
    生年月日から日命星を算出し、星の基本情報と読みデータを返すユースケース。
    ルートは本ユースケースに依存し、インフラ実装には依存しない（ポート経由）。
    """

    @inject
    def __init__(self, nine_repo: INineStarRepository, reading_repo: IReadingQueryRepository) -> None:
        self._nine_repo = nine_repo
        self._reading_repo = reading_repo

    def execute(self, birth_date_str: str) -> Optional[Dict[str, Any]]:
        if not birth_date_str:
            raise ValueError("birth_date is required (YYYY-MM-DD)")

        try:
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            birth_datetime = datetime.combine(birth_date, datetime.min.time())
        except ValueError as e:
            raise ValueError("birth_date must be in format YYYY-MM-DD") from e

        day_astro = DailyAstrology.find_day_astro_info(birth_datetime)
        if not day_astro:
            return None

        # 読みデータはポートから取得（advice含むフルスキーマ）
        reading = self._reading_repo.get_daily_star_reading(getattr(day_astro, 'star_number', None))
        if not reading:
            return None

        # ORMのlazy属性に触れないよう、スカラー項目のみ安全に抽出
        def safe_attr(obj, name):
            try:
                return getattr(obj, name, None)
            except Exception:
                return None

        date_val = safe_attr(day_astro, 'date')
        day_astro_dict = {
            'date': date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else date_val,
            'day': safe_attr(day_astro, 'day'),
            'id': safe_attr(day_astro, 'id'),
            'lunar_date': safe_attr(day_astro, 'lunar_date'),
            'month': safe_attr(day_astro, 'month'),
            'star_number': safe_attr(day_astro, 'star_number'),
            'year': safe_attr(day_astro, 'year'),
            'zodiac': safe_attr(day_astro, 'zodiac'),
            'day_star_reading': {
                'id': reading.get('id'),
                'star_number': reading.get('star_number'),
                'title': reading.get('title'),
                'keywords': reading.get('keywords'),
                'description': reading.get('description'),
                'advice': reading.get('advice'),
            }
        }

        star = self._nine_repo.find_by_star_number(day_astro_dict['star_number'])
        return {
            'birth_date': birth_date_str,
            'day_astro': day_astro_dict,
            'day_star': star.to_dict() if star else None,
            'day_reading': {
                'id': reading.get('id'),
                'star_number': reading.get('star_number'),
                'title': reading.get('title'),
                'keywords': reading.get('keywords'),
                'description': reading.get('description'),
                'advice': reading.get('advice'),
            }
        }


