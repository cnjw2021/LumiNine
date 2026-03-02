from typing import Any, Dict, List
from injector import inject
from apps.ninestarki.domain.repositories.star_grid_pattern_repository_interface import IStarGridPatternRepository
from core.utils.calendar_utils import get_opposite_zodiac_direction


class DirectionRuleEngine:
    """
    九星気学のルールに従って方位の吉凶を判断する純粋なロジック。 (Domain Service)
    """
    @inject
    def __init__(self, star_grid_repo: IStarGridPatternRepository) -> None:
        self.star_grid_repo = star_grid_repo

    def get_yearly_fortune_directions(
        self,
        grid_pattern: Any,
        main_star: int,
        month_star: int,
        year_star: int,
        zodiac: str
    ) -> Dict[str, Any]:
        """年命と本命/月命を基に、各方位の吉凶状態を判断します。"""
        fortune_params = {
            'main_star': main_star, 'month_star': month_star,
            'year_star': year_star, 'zodiac': zodiac
        }
        return grid_pattern.get_fortune_status(fortune_params)

    def filter_auspicious_directions(self, fortune_status: Dict[str, Any]) -> List[str]:
        """吉凶状態の結果から'is_auspicious'がtrueの方位のみを抽出します。"""
        return sorted([
            direction for direction, status in fortune_status.items()
            if status.get("is_auspicious", False)
        ])

    def _get_inauspicious_marks(self, center_star_of_board: int, zodiac_of_board: str) -> List[str]:
        """指定された九星盤の凶方位(破、暗剣殺)を取得します。"""
        board_pattern = self.star_grid_repo.get_by_center_star(center_star_of_board)
        if not board_pattern:
            return []

        inauspicious_marks: List[str] = []
        try:  # 破のチェック
            opposite_dir = get_opposite_zodiac_direction(zodiac_of_board)
            if opposite_dir:
                inauspicious_marks.append(opposite_dir)
        except ValueError:
            pass

        dark_sword_dir = board_pattern.get_dark_sword_direction()  # 暗剣殺のチェック
        if dark_sword_dir:
            inauspicious_marks.append(dark_sword_dir)

        return inauspicious_marks

    def check_inauspicious_marks(
        self,
        auspicious_directions: List[str],
        center_star_of_board: int,
        zodiac_of_board: str
    ) -> bool:
        """指定された九星盤で吉方位が凶方位(破、暗剣殺)と重複しているかどうかをチェックします。"""
        inauspicious_marks = self._get_inauspicious_marks(center_star_of_board, zodiac_of_board)
        return not any(direction in inauspicious_marks for direction in auspicious_directions)

    def filter_out_inauspicious_directions(
        self,
        directions: List[str],
        center_star_of_board: int,
        zodiac_of_board: str
    ) -> List[str]:
        """凶方位(破、暗剣殺)と重複する方位を除外して返します。"""
        inauspicious_marks = self._get_inauspicious_marks(center_star_of_board, zodiac_of_board)
        return [direction for direction in directions if direction not in inauspicious_marks]

    def get_directions_with_compatible_stars(
        self,
        day_pattern: Any,
        auspicious_directions: List[str],
        compatible_stars: List[int]
    ) -> List[str]:
        """吉方位に相性の良い星がある方位のみをフィルタリングして返します。"""
        return [
            direction for direction in auspicious_directions
            if getattr(day_pattern, direction, None) in compatible_stars
        ]

    def check_hour_zodiac_marks(self, auspicious_directions: List[str], hour_info_list: List[Dict]) -> bool:
        """ 時盤の時破を正しくチェックします。 """
        try:
            hour_zodiacs = [item['zodiac'] for item in hour_info_list]
            if not hour_zodiacs:  # 時間干支がない場合は常にTrue
                return True

            opposite_directions = []
            for zodiac in hour_zodiacs:
                try:
                    opposite_directions.append(get_opposite_zodiac_direction(zodiac))
                except ValueError:
                    continue

            overlapping_count = sum(1 for d in auspicious_directions if d in opposite_directions)

            # 重複する時破の数は、'全体の時破の数'より"小さくなければなりません。
            # (つまり、重複しない時破が1つでもあれば吉方位です)
            return overlapping_count < len(opposite_directions)

        except Exception:
            return False


