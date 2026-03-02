"""カレンダー関連のユーティリティ関数

方位判定で使用される干支・方位変換ロジックを提供する。
月反中宮星・月干支・日干支・年計算は solar_terms_data / solar_starts_data /
daily_astrology_data の CSV 事前構築データから直接取得するため、
ここには数式ベースの再計算ロジックを置かない。
"""

# 10干（甲〜癸）と12支（子〜亥）
heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


# ──────────────────────────────────────────────
# 干支 ↔ 方位 変換 (direction_rule_engine, star_grid_pattern で使用)
# ──────────────────────────────────────────────

def get_opposite_zodiac(zodiac: str) -> str:
    """干支の向かい側を取得する

    Args:
        zodiac (str): 干支（例: "甲寅"）

    Returns:
        str: 向かい側の支

    Raises:
        ValueError: 無効な干支が指定された場合
    """
    # 干支から支部分を抽出。入力が1文字ならそのまま十二支とみなす
    if len(zodiac) == 1:
        branch = zodiac
    elif len(zodiac) >= 2:
        branch = zodiac[1]
    else:
        raise ValueError(f"不正な干支形式です: {zodiac}")

    opposite_branches = {
        "子": "午",  # 北 <-> 南
        "丑": "未",  # 北東 <-> 南西
        "寅": "申",  # 北東 <-> 南西
        "卯": "酉",  # 東 <-> 西
        "辰": "戌",  # 南東 <-> 北西
        "巳": "亥",  # 南東 <-> 北西
        "午": "子",  # 南 <-> 北
        "未": "丑",  # 南西 <-> 北東
        "申": "寅",  # 南西 <-> 北東
        "酉": "卯",  # 西 <-> 東
        "戌": "辰",  # 北西 <-> 南東
        "亥": "巳"   # 北西 <-> 南東
    }

    opposite_branch = opposite_branches.get(branch)
    if not opposite_branch:
        raise ValueError(f"無効な十二支です: {branch}")

    return opposite_branch


def get_opposite_zodiac_direction(zodiac: str) -> str:
    """干支の向かい側の方位を取得する

    Args:
        zodiac (str): 干支（例: "甲寅"）

    Returns:
        str: 向かい側の方位の名前（"north", "northeast"など）

    Raises:
        ValueError: 無効な干支が指定された場合
    """
    try:
        if len(zodiac) == 1:
            branch = zodiac
        elif len(zodiac) >= 2:
            branch = zodiac[1]
        else:
            raise ValueError(f"不正な干支形式です: {zodiac}")

        opposite_branch = get_opposite_zodiac(zodiac)

        branch_directions = {
            "子": "north",      # 北
            "丑": "northeast",  # 北東
            "寅": "northeast",  # 北東
            "卯": "east",       # 東
            "辰": "southeast",  # 南東
            "巳": "southeast",  # 南東
            "午": "south",      # 南
            "未": "southwest",  # 南西
            "申": "southwest",  # 南西
            "酉": "west",       # 西
            "戌": "northwest",  # 北西
            "亥": "northwest"   # 北西
        }

        direction = branch_directions.get(opposite_branch)
        if not direction:
            raise ValueError(f"向かい側の十二支 {opposite_branch} に対応する方位が見つかりません")

        return direction
    except Exception as e:
        print(f"干支の向かい側の方位計算でエラー: {str(e)}, 干支: {zodiac}")
        raise ValueError(f"干支の向かい側の方位計算でエラー: {str(e)}")