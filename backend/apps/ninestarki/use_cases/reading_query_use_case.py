from typing import Optional, Dict, Any, List
from injector import inject

from apps.ninestarki.domain.repositories.reading_query_repository_interface import IReadingQueryRepository
from core.utils.logger import get_logger


logger = get_logger(__name__)


class ReadingQueryUseCase:
    """
    読み系（daily/monthly）の取得/一覧を提供するユースケース。
    ルートは本ユースケースに依存し、インフラ実装には依存しない（クリーンアーキテクチャ）。
    必要に応じてHTTP契約（従来スキーマ）へ整形する責務も担う。
    """

    @inject
    def __init__(self, reading_repo: IReadingQueryRepository) -> None:
        self._reading_repo = reading_repo

    # Monthly Star Readings
    def get_monthly_star_reading(self, star_number: int) -> Optional[Dict[str, Any]]:
        data = self._reading_repo.get_monthly_star_reading(star_number)
        if not data:
            return None
        # 既存契約に合わせた整形（必要最低限）
        return {
            'id': data.get('id'),
            'star_number': data.get('star_number'),
            'title': data.get('title'),
            'keywords': data.get('keywords'),
            'description': data.get('description'),
        }

    def list_monthly_star_readings(self) -> List[Dict[str, Any]]:
        items = self._reading_repo.list_monthly_star_readings()
        return [
            {
                'id': it.get('id'),
                'star_number': it.get('star_number'),
                'title': it.get('title'),
                'keywords': it.get('keywords'),
                'description': it.get('description'),
            }
            for it in items
        ]

    # Daily Star Readings
    def get_daily_star_reading(self, star_number: int) -> Optional[Dict[str, Any]]:
        data = self._reading_repo.get_daily_star_reading(star_number)
        if not data:
            return None
        # 既存契約に合わせ、存在しても 'advice' など余計なフィールドは返却しない
        return {
            'id': data.get('id'),
            'star_number': data.get('star_number'),
            'title': data.get('title'),
            'keywords': data.get('keywords'),
            'description': data.get('description'),
        }

    def list_daily_star_readings(self) -> List[Dict[str, Any]]:
        items = self._reading_repo.list_daily_star_readings()
        return [
            {
                'id': it.get('id'),
                'star_number': it.get('star_number'),
                'title': it.get('title'),
                'keywords': it.get('keywords'),
                'description': it.get('description'),
            }
            for it in items
        ]


