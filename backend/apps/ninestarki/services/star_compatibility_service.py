"""九星間の相性判定に関するサービス"""

from typing import Dict, List
from core.models.star_compatibility_matrix import StarCompatibilityMatrix

class StarCompatibilityService:
    """九星間の相性判定を行うサービスクラス"""

    @staticmethod
    def get_compatible_stars_for_main_and_month(main_star: int, month_star: int) -> Dict[str, List[int]]:
        """本命星と月命星それぞれに対して、相性の良い星（GOOD/BETTER/BEST）のリストを返す

        Args:
            main_star (int): 本命星の数字 (1-9)
            month_star (int): 月命星の数字 (1-9)

        Returns:
            Dict[str, List[int]]: {
                "main_star": [相性の良い星（GOOD/BETTER/BEST）の番号のリスト],
                "month_star": [相性の良い星（GOOD/BETTER/BEST）の番号のリスト]
            }
        """
        result = {
            "main_star": [],
            "month_star": []
        }

        # 本命星の相性を取得
        main_star_matrix = StarCompatibilityMatrix.get_by_base_star(main_star)
        if main_star_matrix:
            result["main_star"].extend(main_star_matrix.get_good_stars())
            result["main_star"].extend(main_star_matrix.get_better_stars())
            result["main_star"].extend(main_star_matrix.get_best_stars())
            # 重複を除去してソート
            result["main_star"] = sorted(list(set(result["main_star"])))

        # 月命星の相性を取得
        month_star_matrix = StarCompatibilityMatrix.get_by_base_star(month_star)
        if month_star_matrix:
            result["month_star"].extend(month_star_matrix.get_good_stars())
            result["month_star"].extend(month_star_matrix.get_better_stars())
            result["month_star"].extend(month_star_matrix.get_best_stars())
            # 重複を除去してソート
            result["month_star"] = sorted(list(set(result["month_star"])))

        return result

    @staticmethod
    def get_best_common_and_main_compatible_stars(main_star: int, month_star: int) -> Dict[str, List[int]]:
        """本命星と月命星の両方に共通する相性の良い星と、本命星の相性の良い星を返す

        Args:
            main_star (int): 本命星の数字 (1-9)
            month_star (int): 月命星の数字 (1-9)

        Returns:
            Dict[str, List[int]]: {
                "common_best": [本命星と月命星の両方で相性が良い（GOOD/BETTER/BEST）星のリスト],
                "main_star_good": [本命星との相性が良い星のリスト]
            }
        """
        # 両方の星の相性の良い星を取得
        all_compatibles = StarCompatibilityService.get_compatible_stars_for_main_and_month(main_star, month_star)
        
        result = {
            "common_best": [],  # 両方に共通する相性の良い星
            "main_only_good": []  # 本命星にのみ残った相性の良い星
        }

        # 両方のリストに存在する星を抽出
        main_set = set(all_compatibles["main_star"])
        month_set = set(all_compatibles["month_star"])
        common_stars = main_set.intersection(month_set)
        main_only_stars = main_set.difference(month_set)
        
        result["common_best"] = sorted(list(common_stars))
        result["main_only_good"] = sorted(list(main_only_stars))

        return result
