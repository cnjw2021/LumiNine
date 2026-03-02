from sqlalchemy.orm import Session
from core.database import db, read_only_session

from apps.ninestarki.domain.entities.nine_star import NineStar
from core.utils.logger import get_logger
from apps.ninestarki.domain.repositories.nine_star_repository_interface import INineStarRepository

logger = get_logger(__name__)

class NineStarRepository(INineStarRepository):
    """
    INineStarRepository インターフェースのSQLAlchemy 実装クラスです.
    NineStarエンティティのデータアクセスを担当するリポジトリクラスです.
    """
    def __init__(self, session: Session = db.session):
        self.session = session

    def find_by_star_number(self, star_number: int):
        """星番号でNineStarエンティティを検索します."""
        try:
            with read_only_session() as read_session:
                return read_session.query(NineStar).filter_by(star_number=star_number).first()
        except Exception as e:
            logger.error(f"星番号でNineStarエンティティを検索に失敗しました: {star_number}: {e}")
            return None

    def find_all(self):
        """すべてのNineStarエンティティを検索します."""
        try:
            with read_only_session() as read_session:
                return read_session.query(NineStar).all()
        except Exception as e:
            logger.error(f"すべてのNineStarエンティティを検索に失敗しました: {e}")
            return []