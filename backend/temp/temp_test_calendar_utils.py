#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import os
import ssl
import urllib.request

# パスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

##############################################################################################
#
# 期待の干支とは異なるが、Skyfieldの利用法を念の為おいておく (Line.186-195)
# https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp'
#
##############################################################################################

# 九星気学の計算用モジュールをインポート
try:
    from apps.ninestarki.domain.services.star_calculator_service import StarCalculatorService
    HAS_NINE_STAR = True
except ImportError:
    HAS_NINE_STAR = False
    print("警告: core.models.nine_star モジュールが見つかりません。一部の九星気学機能が使用できません。")

# 太陽黄経に基づく二十四節気の定義
SOLAR_TERMS = [
    ("立春", 315), ("雨水", 330), ("啓蟄", 345), ("春分", 0), 
    ("清明", 15), ("穀雨", 30), ("立夏", 45), ("小満", 60),
    ("芒種", 75), ("夏至", 90), ("小暑", 105), ("大暑", 120),
    ("立秋", 135), ("処暑", 150), ("白露", 165), ("秋分", 180),
    ("寒露", 195), ("霜降", 210), ("立冬", 225), ("小雪", 240),
    ("大雪", 255), ("冬至", 270), ("小寒", 285), ("大寒", 300)
]

# 60干支のリスト(甲子をindex=0として順番に並べる)
ETO_LIST = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳",
    "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯",
    "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑",
    "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥",
    "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉",
    "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未",
    "庚申", "辛酉", "壬戌", "癸亥"
]

# 九星の配列（番号順）
NINE_STARS = [
    "一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
    "六白金星", "七赤金星", "八白土星", "九紫火星"
]

# 干支の五行属性
ETO_GOGYO = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 「1900/1/31 23:00」を甲子として定義 (ローカルタイム想定)
REF_DATETIME = datetime(1900, 1, 31, 23, 0)

def get_eto(d: date) -> str:
    """
    入力日付から干支を計算する
    
    Args:
        d (date): 干支を計算したい日付
        
    Returns:
        str: 干支（例: "甲子"）
    """
    # ユーザーが時刻を指定しない場合、当日の 0:00 と仮定
    target_datetime = datetime(d.year, d.month, d.day, 0, 0)

    # 差分(秒)を求める → 日数に換算
    delta_seconds = (target_datetime - REF_DATETIME).total_seconds()
    # 1日 = 24h * 3600s = 86400s
    day_count = int(delta_seconds // 86400)  # 切り捨て

    # 干支リストのインデックスは 0～59 → mod 60 で巡回
    idx = day_count % 60
    return ETO_LIST[idx]

def get_kyusei_from_eto(eto: str) -> Optional[str]:
    """
    干支から九星を求める
    
    Args:
        eto (str): 干支（例: "甲子"）
        
    Returns:
        Optional[str]: 九星名（例: "一白水星"）またはNone
    """
    if HAS_NINE_STAR:
        # 九星気学モジュールが利用可能ならそちらを使用
        kyusei_short = get_day_kyusei_by_eto(eto)
        if kyusei_short:
            # 短い名前（例: "一白"）から完全な名前へ変換
            for star in NINE_STARS:
                if star.startswith(kyusei_short):
                    return star
            return kyusei_short
    
    # 簡易版マッピング（独自実装)
    try:
        # 干支のインデックスを取得
        idx = ETO_LIST.index(eto)
        
        # 日命星のパターン（これは簡易版なので、より正確な計算は九星気学の専門書を参照）
        kyusei_pattern = [
            1, 9, 8, 7, 6, 5, 4, 3, 2, 1,  # 甲子～癸酉
            9, 8, 7, 6, 5, 4, 3, 2, 1, 9,  # 甲戌～癸未
            8, 7, 6, 5, 4, 3, 2, 1, 9, 8,  # 甲申～癸巳
            7, 6, 5, 4, 3, 2, 1, 9, 8, 7,  # 甲午～癸卯
            6, 5, 4, 3, 2, 1, 9, 8, 7, 6,  # 甲辰～癸丑
            5, 4, 3, 2, 1, 9, 8, 7, 6, 5   # 甲寅～癸亥
        ]
        
        kyusei_num = kyusei_pattern[idx]
        return NINE_STARS[kyusei_num - 1]
    except ValueError:
        return None

def get_gogyo(eto: str) -> Optional[str]:
    """
    干支から五行を取得する
    
    Args:
        eto (str): 干支（例: "甲子"）
        
    Returns:
        Optional[str]: 五行（例: "木"）またはNone
    """
    if not eto or len(eto) < 1:
        return None
    
    # 天干（最初の文字）から五行を取得
    tiangan = eto[0]
    return ETO_GOGYO.get(tiangan)

try:
    # skyfieldが利用可能な場合は天体計算を使用
    from skyfield.api import load, Topos
    import os
    import ssl
    import urllib.request
    HAS_SKYFIELD = True
    
    # SSL証明書の検証問題を解決するための設定
    # 警告: これは開発環境またはテスト環境でのみ使用してください。本番環境では適切な証明書の設定を行ってください。
    ssl_context = ssl._create_unverified_context()
    https_handler = urllib.request.HTTPSHandler(context=ssl_context)
    opener = urllib.request.build_opener(https_handler)
    urllib.request.install_opener(opener)
    
    # 天体データのローカルディレクトリ設定
    # ユーザーのホームディレクトリに .skyfield ディレクトリを作成
    skyfield_data_dir = os.path.join(os.path.expanduser('~'), '.skyfield')
    os.makedirs(skyfield_data_dir, exist_ok=True)
    
    # 太陽・月の位置計算の準備
    ts = load.timescale()
    try:
        # ローカルディレクトリに星表を保存
        try:
            # まずローカルに保存されているか確認
            eph = load('de421.bsp')  # 自動的にキャッシュされる
        except Exception as e:
            print(f"星表のロードに失敗しました: {e}")
            # ローカルにない場合はダウンロード（SSL検証なし）
            try:
                # 別のソースからのダウンロード試行
                url = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp'
                local_path = os.path.join(skyfield_data_dir, 'de421.bsp')
                print(f"星表をダウンロード中: {url}")
                
                # SSLコンテキストを使用してダウンロード
                with urllib.request.urlopen(url, context=ssl_context) as response, open(local_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                print(f"ダウンロード完了: {local_path}")
                eph = load(local_path)
            except Exception as download_error:
                print(f"星表のダウンロードに失敗しました: {download_error}")
                # 内蔵の簡易版を使用
                print("天体計算は使用できません")
                raise ImportError("星表のダウンロードに失敗しました")
        
        # JPL星表から天体を取得
        sun = eph['sun']
        moon = eph['moon']
        earth = eph['earth']
        print("天体計算の準備が完了しました")
        
    except (ImportError, Exception) as e:
        print(f"天体計算機能を無効化します: {e}")
        HAS_SKYFIELD = False

    if HAS_SKYFIELD:
        def solar_longitude_jst(d: date) -> float:
            """ 指定日(日本標準時0:00相当)での太陽黄経(度)を返す """
            # JST(UTC+9)で 0:00 をUTC に直す → 15:00前日(UTC) 
            t = ts.utc(d.year, d.month, d.day, 0 - 9)
            position = earth.at(t).observe(sun).apparent()
            # ecliptic座標に変換 → 黄経(l) を度で取得
            eclip = position.ecliptic_latlon()
            lon_deg = eclip[1].degrees
            return lon_deg % 360
        
        def moon_sun_diff_jst(d: date) -> float:
            """ 指定日の月と太陽の黄経差を返す """
            # 同様にJSTの日時を計算
            t = ts.utc(d.year, d.month, d.day, 0 - 9)
            sun_pos = earth.at(t).observe(sun).apparent().ecliptic_latlon()
            moon_pos = earth.at(t).observe(moon).apparent().ecliptic_latlon()
            # 黄経差(0度付近が新月)
            diff = (moon_pos[1].degrees - sun_pos[1].degrees) % 360
            return diff
        
        def find_solar_term(d: date) -> Optional[str]:
            """指定日が節気に該当するか判定し、節気名を返す"""
            sol_lon = solar_longitude_jst(d)
            
            for term_name, term_lon in SOLAR_TERMS:
                # 黄経の差が1度以内なら該当する節気とみなす
                if abs((sol_lon - term_lon) % 360) < 1:
                    return term_name
            return None
        
        def is_new_moon(d: date) -> bool:
            """指定日が朔（新月）かどうかを判定"""
            diff_ms = moon_sun_diff_jst(d)
            # 黄経差が3度以内なら朔（新月）とみなす
            return abs(diff_ms) < 3
        
        def is_full_moon(d: date) -> bool:
            """指定日が望（満月）かどうかを判定"""
            diff_ms = moon_sun_diff_jst(d)
            # 黄経差が180度±3度以内なら望（満月）とみなす
            return abs((diff_ms - 180) % 360) < 3
    else:
        # スカイフィールド機能が無効の場合のダミー関数
        def solar_longitude_jst(d: date) -> float:
            return 0.0
        
        def moon_sun_diff_jst(d: date) -> float:
            return 0.0
        
        def find_solar_term(d: date) -> Optional[str]:
            return None
        
        def is_new_moon(d: date) -> bool:
            return False
        
        def is_full_moon(d: date) -> bool:
            return False

except ImportError:
    HAS_SKYFIELD = False
    print("警告: skyfield がインストールされていないため、天体計算は利用できません")
    print("pip install skyfield でインストールしてください")
    
    # スカイフィールドがない場合のダミー関数
    def solar_longitude_jst(d: date) -> float:
        return 0.0
    
    def moon_sun_diff_jst(d: date) -> float:
        return 0.0
    
    def find_solar_term(d: date) -> Optional[str]:
        return None
    
    def is_new_moon(d: date) -> bool:
        return False
    
    def is_full_moon(d: date) -> bool:
        return False

def generate_calendar(start_date: date, end_date: date) -> List[Dict]:
    """
    指定期間の暦情報を生成する
    
    Args:
        start_date (date): 開始日
        end_date (date): 終了日
        
    Returns:
        List[Dict]: 日毎の暦情報リスト
    """
    result = []
    current = start_date
    
    while current <= end_date:
        # 干支の取得
        eto = get_eto(current)
        
        # 基本情報
        day_info = {
            "date": current.isoformat(),
            "year": current.year,
            "month": current.month,
            "day": current.day,
            "weekday": current.weekday(),  # 0: 月曜, 6: 日曜
            "eto": eto,
            "gogyo": get_gogyo(eto),  # 五行
            "kyusei": get_kyusei_from_eto(eto),  # 九星
        }
        
        # skyfield が利用可能な場合は天体情報も追加
        if HAS_SKYFIELD:
            sol_lon = solar_longitude_jst(current)
            diff_ms = moon_sun_diff_jst(current)
            
            day_info.update({
                "solar_longitude": round(sol_lon, 2),
                "moon_sun_diff": round(diff_ms, 2),
                "solar_term": find_solar_term(current),
                "is_new_moon": is_new_moon(current),
                "is_full_moon": is_full_moon(current)
            })
        
        result.append(day_info)
        current += timedelta(days=1)
    
    return result

def print_calendar(start_date: date, end_date: date):
    """
    万年暦を表示する
    
    Args:
        start_date (date): 開始日
        end_date (date): 終了日
    """
    calendar_data = generate_calendar(start_date, end_date)
    
    print(f"九星気学万年暦 ({start_date} ～ {end_date})")
    print("-" * 78)
    
    for day in calendar_data:
        date_str = f"{day['year']:4d}/{day['month']:02d}/{day['day']:02d}"
        weekday_str = ["月", "火", "水", "木", "金", "土", "日"][day['weekday']]
        eto_str = day['eto']
        kyusei_str = day['kyusei'] if day['kyusei'] else "不明"
        gogyo_str = day['gogyo'] if day['gogyo'] else "不明"
        
        # 基本情報の表示
        output = f"{date_str} ({weekday_str}) 干支:{eto_str} 五行:{gogyo_str} 九星:{kyusei_str}"
        
        # skyfield 情報がある場合
        if HAS_SKYFIELD and 'solar_longitude' in day:
            if day['solar_term']:
                output += f" 【{day['solar_term']}】"
            if day['is_new_moon']:
                output += " 【朔】"
            if day['is_full_moon']:
                output += " 【望】"
        
        print(output)

if __name__ == "__main__":
    # 使用例: 2025年1月の万年暦を表示
    start_date = date(2025, 1, 1)
    end_date = date(2025, 1, 31)
    
    print_calendar(start_date, end_date) 