from typing import List, Optional
from sqlalchemy.orm import Session
from core.database import db
from core.database import read_only_session
from apps.ninestarki.domain.entities.star_life_guidance import StarLifeGuidance, CategoryEnum
from apps.ninestarki.domain.repositories.star_life_guidance_repository_interface import IStarLifeGuidanceRepository
from core.utils.logger import get_logger

logger = get_logger(__name__)

class StarLifeGuidanceRepository(IStarLifeGuidanceRepository):
    """星と人生のガイダンス情報のリポジトリ実装クラス"""

    def __init__(self, session: Session = db.session):
        self.session = session

    def find_by_stars_and_category(self, main_star: int, month_star: int, category: CategoryEnum) -> Optional[StarLifeGuidance]:
        """本命星、月命星、カテゴリで星と人生のガイダンス情報を取得する"""
        try:
            with read_only_session() as read_session:
                return read_session.query(StarLifeGuidance).filter_by(
                    main_star=main_star,
                    month_star=month_star,
                    category=category
                ).first()
        except Exception as e:
            logger.error(f"Failed to find StarLifeGuidance by stars and category: {e}")
            return None

    def find_by_stars(self, main_star: int, month_star: int) -> List[StarLifeGuidance]:
        """本命星、月命星で星と人生のガイダンス情報を取得する"""
        try:
            with read_only_session() as read_session:
                return read_session.query(StarLifeGuidance).filter_by(
                    main_star=main_star,
                    month_star=month_star
                ).all()
        except Exception as e:
            logger.error(f"Failed to find StarLifeGuidance by stars: {e}")
            return []
