"""相性レベルの列挙型を定義するモジュール"""

import enum

class CompatibilityLevel(enum.Enum):
    """相性レベルを表す列挙型"""
    BEST = "BEST"    # 大吉
    BETTER = "BETTER"  # 中吉
    GOOD = "GOOD"    # 小吉
    BAD = "BAD"      # 凶 