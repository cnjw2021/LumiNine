"""カレンダー関連のユーティリティ関数"""

from datetime import datetime, date
from math import floor
from core.services.solar_calendar_service import SolarCalendarService

# 10干（甲〜癸）と12支（子〜亥）
heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_calculation_year(year: int = None) -> int:
    """指定された年または現在の日付から立春を考慮した計算年を取得する
    
    Args:
        year (int, optional): 指定する年。Noneの場合は現在の年を使用
    
    現在の日付が立春前であれば前年、立春後であれば当年を返す
    
    Returns:
        int: 立春を考慮した計算年
    """
    if year is None:
        # 年が指定されていない場合は現在の日付を使用
        current_date = datetime.now().date()
        current_datetime = datetime.combine(current_date, datetime.min.time())
    else:
        # 指定された年の現在の月日を使用
        current_date = datetime.now().date()
        target_date = datetime(year, current_date.month, current_date.day).date()
        current_datetime = datetime.combine(target_date, datetime.min.time())
    
    # SolarCalendarServiceを使用して立春を考慮した計算年を取得
    return SolarCalendarService.get_calculation_year(current_datetime)

def calculate_day_eto(y: int, m: int, d: int) -> str:
    """西暦から日干支を計算するGaussの公式に類似した暦計算法を活用
    
    Args:
        y: 年
        m: 月
        d: 日
    
    Returns:
        str: 干支（例: "甲子"）
    """
    # ルール1: 1月、2月は前年度として扱う
    if m == 1 or m == 2:
        y -= 1
        m += 12

    c = y // 100      # 世紀
    n = y % 100       # 残りの年

    # 日干計算 (mod 10)
    p = (4 * c + floor(c / 4) + 5 * n + floor(n / 4) + floor((3 * m + 3) / 5) + d + 7) % 10

    # 日支計算 (mod 12)
    q = (8 * c + floor(c / 4) + 5 * n + floor(n / 4) + 6 * m + floor((3 * m + 3) / 5) + d + 1) % 12

    # p=0のときは10番目の癸、q=0のときは12番目の亥
    stem = heavenly_stems[p - 1 if p != 0 else 9]
    branch = earthly_branches[q - 1 if q != 0 else 11]

    return stem + branch

def get_day_eto(target_date: date) -> str:
    """日付から日の干支を取得する
    
    Args:
        target_date (date): 対象日付
        
    Returns:
        str: 日の干支（例: "甲子"）
    """
    # 日の干支計算
    return calculate_day_eto(target_date.year, target_date.month, target_date.day)

# 干支の向かい側を取得する関数
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
    
    # 九星盤における十二支の正確な向かい側のマッピング
    # 「丑・寅：北東、辰・巳：南東、未・申：南西、戌・亥：北西」という対応に基づく
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
    
    # 向かい側の支を取得
    opposite_branch = opposite_branches.get(branch)
    if not opposite_branch:
        raise ValueError(f"無効な十二支です: {branch}")
        
    return opposite_branch

# 干支の向かい側の方位を取得する関数
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
        # 干支から支部分を抽出（1文字の場合はそのまま）
        if len(zodiac) == 1:
            branch = zodiac
        elif len(zodiac) >= 2:
            branch = zodiac[1]
        else:
            raise ValueError(f"不正な干支形式です: {zodiac}")
            
        opposite_branch = get_opposite_zodiac(zodiac)
        
        # 十二支と方位のマッピング
        # 「丑・寅：北東、辰・巳：南東、未・申：南西、戌・亥：北西」という対応関係
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
        # エラーの詳細をログに記録
        print(f"干支の向かい側の方位計算でエラー: {str(e)}, 干支: {zodiac}")
        raise ValueError(f"干支の向かい側の方位計算でエラー: {str(e)}") 