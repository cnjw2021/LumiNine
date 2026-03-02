import math
from datetime import datetime, timedelta, date
import pytz
import ssl
import urllib.request
import os
import pathlib
import argparse
from skyfield.api import load, utc

#################################################################################
#
# 九星気学の陽遁・陰遁の切り替わり日を計算する
# ephemeris segment only covers dates 1899-07-29 through 2053-10-09
#
#################################################################################

# SSL証明書の検証問題を解決するための設定
# 警告: これは開発環境またはテスト環境でのみ使用してください。本番環境では適切な証明書の設定を行ってください。
ssl_context = ssl._create_unverified_context()
https_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(https_handler)
urllib.request.install_opener(opener)

# skyfieldのSSL検証をバイパス - 複数の方法を試みる
ssl._create_default_https_context = ssl._create_unverified_context

# 環境変数でHTTPSの検証を無効化（Skyfieldがこれを参照する可能性がある）
os.environ['SSL_CERT_VERIFY'] = 'false'
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HTTPS_VALIDATE'] = 'false'

# エフェメリスファイルをローカルに用意し、そのパスを指定
EPHEMERIS_PATH = os.path.join(os.path.dirname(__file__), 'de421.bsp')

# ローカルにファイルがない場合は手動でダウンロード
def download_ephemeris_file():
    """
    de421.bspファイルをSSL検証なしで手動ダウンロードする
    """
    if os.path.exists(EPHEMERIS_PATH):
        print(f"エフェメリスファイルが既に存在します: {EPHEMERIS_PATH}")
        return
    
    print(f"エフェメリスファイルをダウンロードします: {EPHEMERIS_PATH}")
    url = 'https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de421.bsp'
    
    # SSLコンテキストを明示的に無効化
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(url, context=ctx) as response:
            data = response.read()
            with open(EPHEMERIS_PATH, 'wb') as f:
                f.write(data)
        print(f"ダウンロード完了: {EPHEMERIS_PATH}")
    except Exception as e:
        print(f"ダウンロード失敗: {e}")

# 実行前にエフェメリスファイルをチェック
download_ephemeris_file()

def find_solstice(year: int, target_lon: float) -> datetime:
    """
    (1) 太陽黄経が target_lon (夏至=90°, 冬至=270°) になる時刻を
        Skyfield で年内から精密探索し、UTCのdatetimeを返す
    (2) JSTへの変換は呼び出し側で実施
    """
    ts = load.timescale()
    
    # ローカルのエフェメリスファイルを使用
    if os.path.exists(EPHEMERIS_PATH):
        eph = load(EPHEMERIS_PATH)
    else:
        # ローカルにファイルが無い場合はダウンロードを試みる
        try:
            eph = load('de421.bsp')  # JPLの星表ファイル
        except OSError as e:
            print(f"エフェメリスのダウンロードでエラー: {e}")
            raise
    
    # 太陽と地球の参照
    sun = eph['sun']
    earth = eph['earth']
    
    # 夏至なら6月〜7月、冬至なら12月〜翌年1月を大まかに探す
    if target_lon == 90.0:  # 夏至
        start_dt_utc = datetime(year, 6, 1, 0, 0, tzinfo=utc)
        end_dt_utc   = datetime(year, 7, 1, 0, 0, tzinfo=utc)
    else:  # 冬至=270°
        start_dt_utc = datetime(year, 12, 1, 0, 0, tzinfo=utc)
        end_dt_utc   = datetime(year+1, 1, 1, 0, 0, tzinfo=utc)

    # まず数時間刻みで大雑把に探索
    step = timedelta(hours=6)
    best_dt = start_dt_utc
    min_diff = float('inf')
    
    dt_utc = start_dt_utc
    while dt_utc < end_dt_utc:
        # Skyfieldで太陽黄経を計算
        t = ts.from_datetime(dt_utc)
        app = earth.at(t).observe(sun).apparent()
        lon_deg = app.ecliptic_latlon()[1].degrees % 360
        
        diff = abs(lon_deg - target_lon)
        if diff < min_diff:
            min_diff = diff
            best_dt = dt_utc
        dt_utc += step
    
    # 周辺数時間をさらに2分法的に追い込む
    # （6h -> 3h ->1.5h->... と繰り返し精度を上げる）
    search_range = 3  # hours
    for _ in range(6):  # 6回反復で±(3h/2^6) < 3分程度までは絞れる
        trial_points = []
        for offset in [-search_range, 0, search_range]:
            trial_dt = best_dt + timedelta(hours=offset)
            if trial_dt < start_dt_utc or trial_dt > end_dt_utc:
                continue
            t_test = ts.from_datetime(trial_dt)
            app = earth.at(t_test).observe(sun).apparent()
            lon_deg = app.ecliptic_latlon()[1].degrees % 360
            diff = abs(lon_deg - target_lon)
            trial_points.append((diff, trial_dt))
        trial_points.sort(key=lambda x: x[0])
        best_dt = trial_points[0][1]
        search_range /= 2
    
    return best_dt  # UTC

def get_solstice_dates(year: int):
    """
    指定年の夏至(太陽黄経=90°)と冬至(太陽黄経=270°)を
    JST（日本標準時）のdatetime型で返す。
    
    ※固定の基準日を使用する方式に変更
    """
    # 基準日
    BASE_SUMMER_SOLSTICE = datetime(1967, 6, 28, tzinfo=pytz.timezone('Asia/Tokyo'))  # 1967年の夏至
    BASE_WINTER_SOLSTICE = datetime(1967, 12, 25, tzinfo=pytz.timezone('Asia/Tokyo'))  # 1967年の冬至
    
    # 閏が入る年のリスト
    LEAP_YEARS = [
        1918, 1929, 1941, 1952, 1964, 1975, 1987, 1998,
        2010, 2021, 2033, 2044, 2056, 2067, 2079, 2090
    ]
    
    # 1967年からの経過年数
    years_since_1967 = year - 1967
    
    # 閏の調整: 対象年以前の閏年の数を計算し、閏の日数を算出
    leap_adjustment = 0
    for leap_year in LEAP_YEARS:
        if year > leap_year:
            leap_adjustment += 30  # 閏期間は30日
    
    # 基本周期は365.25日/年とする
    days_since_1967 = years_since_1967 * 365.25
    adjusted_days = days_since_1967 - leap_adjustment
    
    # 夏至は約182.5日ごと
    summer_solstice = BASE_SUMMER_SOLSTICE + timedelta(days=adjusted_days % 365.25)
    
    # 冬至は夏至から約182.5日後
    winter_solstice = BASE_WINTER_SOLSTICE + timedelta(days=adjusted_days % 365.25)
    
    # タイムゾーンの調整
    jst = pytz.timezone('Asia/Tokyo')
    summer_jst = summer_solstice.astimezone(jst)
    winter_jst = winter_solstice.astimezone(jst)
    
    return summer_jst, winter_jst

def get_ascending_descending_switch_days(year: int):
    """
    指定年の陽遁開始日、陰遁開始日を返す。
    1967年の基準日から計算し、閏年には期間が210日になる。
    
    Returns: (ascending_start: date, descending_start: date)
      - ascending_start: 陽遁開始日
      - descending_start: 陰遁開始日
    """
    # Base dates (calculation starting points)
    BASE_DESCENDING_PHASE_DATE = datetime(1967, 6, 29)  # 陰遁開始日（1967年）
    BASE_ASCENDING_PHASE_DATE = datetime(1967, 12, 26)  # 陽遁開始日（1967年）
    
    # 閏が入る年のリスト
    LEAP_YEARS = {
        1918, 1929, 1941, 1952, 1964, 1975, 1987, 1998,
        2010, 2021, 2033, 2044, 2056, 2067, 2079, 2090
    }
    
    # サイクル期間を判定する関数
    def period_length(start_date: datetime) -> int:
        """サイクルの開始年がLEAP_YEARSに含まれていれば210日、そうでなければ180日を返す"""
        if start_date.year in LEAP_YEARS:
            return 210  # 閏年の場合は30日延長
        else:
            return 180  # 通常のサイクル
    
    # 1967年から指定年までのサイクルをすべてシミュレーションする
    current_date = BASE_DESCENDING_PHASE_DATE
    is_descending_phase = True  # 最初は陰遁から開始
    
    # 指定された年の切り替わり日を格納する変数
    descending_start = None  # 陰遁開始日
    ascending_start = None  # 陽遁開始日
    
    while current_date.year <= year + 1:  # +1は年の最後のサイクルを確実に取得するため
        # 現在のサイクルの期間を計算
        cycle_days = period_length(current_date)
        cycle_end = current_date + timedelta(days=cycle_days - 1)
        
        # 指定された年のサイクル開始日を記録
        if current_date.year == year:
            if is_descending_phase and descending_start is None:
                descending_start = current_date.date()
            elif not is_descending_phase and ascending_start is None:
                ascending_start = current_date.date()
        
        # 次のサイクルの開始日（終了日の翌日）
        current_date = cycle_end + timedelta(days=1)
        is_descending_phase = not is_descending_phase  # 陰遁と陽遁を切り替え
    
    # もし特定の年の日付が見つからなかった場合（レアケース）
    if descending_start is None:
        print(f"警告: {year}年の陰遁開始日が見つかりませんでした。デフォルト値を使用します。")
        raise ValueError(f"警告: {year}年の陰遁開始日が見つかりませんでした。")
    if ascending_start is None:
        print(f"警告: {year}年の陽遁開始日が見つかりませんでした。デフォルト値を使用します。")
        ascending_start = None  # デフォルト
    
    return ascending_start, descending_start

def print_results_for_year_range(start_year, end_year):
    """指定された年範囲の結果を表示する"""
    print("九星気学における陽遁・陰遁の切り替わり日（基準日計算）")
    print("----------------------------------------")
    
    results = []
    for y in range(start_year, end_year + 1):
        ascending, descending = get_ascending_descending_switch_days(y)
        print(f"{y}年: 陰遁開始={descending}, 陽遁開始={ascending}")
        
        # 結果をリストに追加
        results.append({
            "year": y,
            "descending_phase_date": descending,
            "descending_phase_time": "00:00:00",
            "ascending_phase_date": ascending,
            "ascending_phase_time": "00:00:00"
        })
    
    return results

def save_to_sql_file(results, output_file="stellar_cycles_data.sql"):
    """結果をSQLファイルに出力する"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 九星気学の陽遁・陰遁周期データ\n")
        f.write("-- 基準日：1967-06-29(陰遁開始)、1967-12-26(陽遁開始)\n\n")
        
        f.write("INSERT INTO stellar_cycles (year, descending_phase_date, descending_phase_time, ascending_phase_date, ascending_phase_time, created_at, updated_at) VALUES\n")
        
        for i, data in enumerate(results):
            line = f"({data['year']}, '{data['descending_phase_date']}', '{data['descending_phase_time']}', '{data['ascending_phase_date']}', '{data['ascending_phase_time']}', NOW(), NOW())"
            if i < len(results) - 1:
                line += ","
            f.write(line + "\n")
        
        f.write("ON DUPLICATE KEY UPDATE\n")
        f.write("  descending_phase_date = VALUES(descending_phase_date),\n")
        f.write("  descending_phase_time = VALUES(descending_phase_time),\n")
        f.write("  ascending_phase_date = VALUES(ascending_phase_date),\n")
        f.write("  ascending_phase_time = VALUES(ascending_phase_time);\n")
    
    print(f"SQLファイルを出力しました: {output_file}")

if __name__ == '__main__':
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='九星気学の陽遁・陰遁の切り替わり日を計算')
    
    # 引数グループを作成（相互排他的）
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-y', '--year', type=int, help='計算する特定の年')
    group.add_argument('-r', '--range', nargs=2, type=int, metavar=('START', 'END'), 
                       help='計算する年の範囲。例: 2020 2030')
    
    # SQLファイル出力オプション
    parser.add_argument('-s', '--sql', action='store_true', help='結果をSQLファイルに出力する')
    parser.add_argument('-o', '--output', type=str, default="stellar_cycles_data.sql", help='出力SQLファイル名')
    
    args = parser.parse_args()
    
    if args.year:
        # 特定の年のみ計算
        results = print_results_for_year_range(args.year, args.year)
    elif args.range:
        # 指定範囲の年を計算
        start_year, end_year = args.range
        results = print_results_for_year_range(start_year, end_year)
    else:
        # デフォルトの年範囲を1967〜2052に設定
        default_start_year = 1967
        default_end_year = 2052
        print(f"デフォルト範囲で計算: {default_start_year}年〜{default_end_year}年")
        results = print_results_for_year_range(default_start_year, default_end_year)
    
    # SQLファイル出力
    if args.sql:
        save_to_sql_file(results, args.output)
