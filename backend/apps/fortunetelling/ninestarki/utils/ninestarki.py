"""Nine Star Ki calculation utilities."""

from datetime import datetime

def calculate_life_path_number(birthdate):
    """Calculate life path number from birthdate."""
    if isinstance(birthdate, str):
        # 文字列の場合はそのまま数字を抽出
        date_str = ''.join(filter(str.isdigit, birthdate))
    else:
        # datetimeオブジェクトの場合はstrftimeを使用
        date_str = birthdate.strftime('%Y%m%d')

    # 各桁の数字を合計
    total = sum(int(digit) for digit in date_str)
    
    # 2桁以上の場合は更に計算
    while total > 9:
        next_total = sum(int(digit) for digit in str(total))
        # 次の合計が11, 22, 33のいずれかの場合はマスターナンバーとして返す
        if next_total in [11, 22, 33]:
            return next_total
        # それ以外の場合は計算を続ける
        total = next_total
    
    return total

def calculate_personal_year(birthdate, target_year=None):
    """Calculate personal year number."""
    if target_year is None:
        target_year = datetime.now().year
    
    # birthdateが文字列の場合はdatetimeオブジェクトに変換
    if isinstance(birthdate, str):
        try:
            birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
        except ValueError:
            # フォーマットが異なる場合は別のフォーマットを試す
            try:
                birthdate = datetime.strptime(birthdate, '%Y/%m/%d')
            except ValueError as e:
                raise ValueError(f"Invalid date format. Expected YYYY-MM-DD or YYYY/MM/DD, got {birthdate}") from e
    
    month = birthdate.month
    day = birthdate.day
    
    date_str = f"{target_year}{month:02d}{day:02d}"
    while len(date_str) > 1:
        total = sum(int(digit) for digit in date_str)
        date_str = str(total)
    return int(date_str) 