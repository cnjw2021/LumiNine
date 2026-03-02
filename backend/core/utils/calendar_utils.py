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


# ──────────────────────────────────────────────
# 月盤ユーティリティ (月単位の中宮/干支計算)
# ──────────────────────────────────────────────

# 絶月(節月)インデックス → 地支 (1=寅月 〜 12=丑月)
_SETSU_MONTH_BRANCHES = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

# 五虎遁: 年干インデックス(0=甲 〜 9=癸) → 1月(寅月)の天干インデックス(0=甲)
_GOKOTON_MAP: dict[int, int] = {
    0: 2,  # 甲 → 丙
    1: 4,  # 乙 → 戊
    2: 6,  # 丙 → 庚
    3: 8,  # 丁 → 壬
    4: 0,  # 戊 → 甲
    5: 2,  # 己 → 丙
    6: 4,  # 庚 → 戊
    7: 6,  # 辛 → 庚
    8: 8,  # 壬 → 壬
    9: 0,  # 癸 → 甲
}

# 年盤中宮グループ → 1月(寅月)の月盤中宮星
_GROUP_START_STAR: dict[frozenset[int], int] = {
    frozenset({1, 4, 7}): 8,  # 上元
    frozenset({2, 5, 8}): 5,  # 中元
    frozenset({3, 6, 9}): 2,  # 下元
}


def get_monthly_center_star(year_center_star: int, setsu_month_index: int) -> int:
    """月盤の中宮星を算出する (逆行公式).

    구성기학의 월반 중궁성은 연반 중궁성의 그룹(上元/中元/下元)에 따라
    1월(寅月) 시작값이 결정되고, 이후 월이 진행될수록 역행(감소)한다.

    Args:
        year_center_star: 해당 연도의 연반 중궁성 (1~9)
        setsu_month_index: 절월(節月) 인덱스 (1=寅月/立春~ … 12=丑月/小寒~)

    Returns:
        월반 중궁성 (1~9)

    Raises:
        ValueError: year_center_star가 1~9 범위 밖일 경우
        ValueError: setsu_month_index가 1~12 범위 밖일 경우
    """
    if not 1 <= year_center_star <= 9:
        raise ValueError(f"year_center_star は 1~9 の範囲でなければなりません。got: {year_center_star}")
    if not 1 <= setsu_month_index <= 12:
        raise ValueError(f"setsu_month_index は 1~12 の範囲でなければなりません。got: {setsu_month_index}")

    # 1월(寅月) 시작 중궁성 결정
    start: int | None = None
    for group, first_star in _GROUP_START_STAR.items():
        if year_center_star in group:
            start = first_star
            break
    if start is None:
        raise ValueError(f"年中宮 {year_center_star} のグループが特定できません。")

    # 역행: 월이 진행될수록 1씩 감소 → (start - offset) % 9 (1-indexed)
    offset = setsu_month_index - 1
    result = ((start - 1 - offset) % 9) + 1
    return result


def get_monthly_kanshi(year_stem_index: int, setsu_month_index: int) -> tuple[str, str]:
    """월간지(月干支)를 산출한다 (五虎遁 원칙).

    Args:
        year_stem_index: 해당 연도의 천간 인덱스 (0=甲 ~ 9=癸)
        setsu_month_index: 절월(節月) 인덱스 (1=寅月 ~ 12=丑月)

    Returns:
        (천간 문자, 지지 문자) 튜플. 예: ('丙', '寅')

    Raises:
        ValueError: 범위 밖의 인수가 입력될 경우
    """
    if not 0 <= year_stem_index <= 9:
        raise ValueError(f"year_stem_index は 0~9 の範囲でなければなりません。got: {year_stem_index}")
    if not 1 <= setsu_month_index <= 12:
        raise ValueError(f"setsu_month_index は 1~12 の範囲でなければなりません。got: {setsu_month_index}")

    # 五虎遁: 연도 천간 → 1월(寅月) 천간 인덱스
    first_month_stem_index = _GOKOTON_MAP[year_stem_index]

    # 월이 진행될수록 천간이 순행 (+1)
    stem_index = (first_month_stem_index + (setsu_month_index - 1)) % 10
    branch_index = setsu_month_index - 1  # 0=寅, 1=卯, …

    return heavenly_stems[stem_index], _SETSU_MONTH_BRANCHES[branch_index]


def get_year_stem_index_from_zodiac(year_zodiac: str) -> int:
    """연도 간지(干支) 문자열에서 천간 인덱스를 추출한다.

    Args:
        year_zodiac: 연간지 문자열 (예: '甲子', 或いは天干のみ '甲')

    Returns:
        천간 인덱스 (0=甲 ~ 9=癸)

    Raises:
        ValueError: 無効な干支が渡された場合
    """
    stem_char = year_zodiac[0] if year_zodiac else ""
    if stem_char not in heavenly_stems:
        raise ValueError(f"無効な年干: '{stem_char}'. 有効値: {heavenly_stems}")
    return heavenly_stems.index(stem_char)
 