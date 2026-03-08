from datetime import date, datetime
from typing import Union, Optional

from core.database import db
from core.models.pattern_switch_date import PatternSwitchDate

class PatternSwitchService:
    """陽遁/隠遁の切替管理サービス"""

    @staticmethod
    def get_pattern_by_date(target_date: Union[date, str]) -> Optional[str]:
        """指定日の陽遁 (SP_ASC) / 隠遁 (SP_DESC) パターンを返す。

        Args:
            target_date (date | str): 調べたい日付。
                str の場合は "YYYY-MM-DD" 形式を想定。

        Returns:
            str | None: 'SP_ASC' または 'SP_DESC'。該当しない場合 None。
        """
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        # 最新の切替日 (<= target_date) を取得
        switch = (
            PatternSwitchDate.query
            .filter(PatternSwitchDate.date <= target_date)
            .order_by(PatternSwitchDate.date.desc())
            .first()
        )
        if switch:
            return switch.pattern
        return None 