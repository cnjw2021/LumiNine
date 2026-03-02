from typing import Optional, List, Dict, Any
from injector import inject

from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository


class StarCatalogUseCase:
    """
    九星カタログ取得（一覧/単一）を提供するユースケース。
    ルートは本ユースケースに依存し、インフラ実装には依存しない。
    """

    @inject
    def __init__(self, nine_repo: INineStarRepository) -> None:
        self._nine_repo = nine_repo

    def list_stars(self) -> List[Dict[str, Any]]:
        stars = self._nine_repo.find_all()
        return [star.to_dict() for star in stars]

    def get_star(self, star_number: int) -> Optional[Dict[str, Any]]:
        star = self._nine_repo.find_by_star_number(star_number)
        return star.to_dict() if star else None


