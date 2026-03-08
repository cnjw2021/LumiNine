from typing import List
from sqlalchemy.orm import Session
from core.database import db, read_only_session

from apps.reading.ninestarki.domain.entities.star_attribute import StarAttribute
from core.utils.logger import get_logger
from apps.reading.ninestarki.domain.repositories.star_attribute_repository_interface import IStarAttributeRepository

logger = get_logger(__name__)


class StarAttributeRepository(IStarAttributeRepository):
    """
    IStarAttributeRepository インターフェースのSQLAlchemy 実装クラスです.
    StarAttributeエンティティのデータアクセスを担当するリポジトリクラスです.
    """
    def __init__(self, session: Session = db.session):
        self.session = session

    def find_by_star_and_type(self, star_number: int, attribute_type: str) -> List[str]:
        """指定された星番号と属性タイプに一致する属性値のリストを返します."""
        try:
            with read_only_session() as read_session:
                results = (
                    read_session.query(StarAttribute)
                    .filter_by(star_number=star_number, attribute_type=attribute_type)
                    .all()
                )
                return [r.attribute_value for r in results]
        except Exception as e:
            logger.error(f"StarAttribute検索に失敗しました (star={star_number}, type={attribute_type}): {e}")
            return []
