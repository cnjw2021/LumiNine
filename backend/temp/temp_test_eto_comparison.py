#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import floor
from datetime import date, datetime, timedelta
import sys
import os

# 既存の干支計算システムを直接実装（外部ファイル参照を避ける）
# 10干（甲〜癸）
heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 12支（子〜亥）
earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

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

# 「1900/1/31 23:00」を甲子として定義 (ローカルタイム想定)
REF_DATETIME = datetime(1900, 1, 31, 23, 0)

def calculate_ilgan_ilsi(y: int, m: int, d: int) -> str:
    """
    韓国の干支計算アルゴリズム
    
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

    stem = heavenly_stems[p - 1 if p != 0 else 9]     # p=0のときは10番目の癸
    branch = earthly_branches[q - 1 if q != 0 else 11]  # q=0のときは12番目の亥

    return stem + branch

def get_eto_1900_01_31_23_basis(d: date) -> str:
    """
    入力日付の0:00 (ローカル)を datetime 化し、
    1900/1/31 23:00 と比較して何日差があるかを計算、
    60干支のリストから干支を割り出す。
    
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

def eto_existing_method(d: date) -> str:
    """
    現在の実装（utils.calendar_utils.get_eto）と同様の干支計算
    ここでは1900/1/31 23:00基準の計算と同じロジックとする
    
    Args:
        d (date): 干支を計算したい日付
        
    Returns:
        str: 干支（例: "甲子"）
    """
    return get_eto_1900_01_31_23_basis(d)

def compare_eto_methods(dates_to_check):
    """
    異なる干支計算方法を比較する
    
    Args:
        dates_to_check: チェックする日付のリスト
    """
    print("日付の干支計算比較")
    print("-" * 65)
    print(f"{'日付':^12} | {'韓国式アルゴリズム':^12} | {'1900/1/31基準':^12} | {'現在の実装':^12} | {'一致':^6}")
    print("-" * 65)
    
    for dt in dates_to_check:
        # 韓国式アルゴリズム
        korean_eto = calculate_ilgan_ilsi(dt.year, dt.month, dt.day)
        
        # 1900/1/31 23:00基準の計算
        basis_eto = get_eto_1900_01_31_23_basis(dt)
        
        # 現在の実装（utils.calendar_utils.get_eto）
        existing_eto = eto_existing_method(dt)
        
        # 結果の一致を確認
        is_match = (korean_eto == basis_eto == existing_eto)
        match_str = "○" if is_match else "×"
        
        print(f"{dt.isoformat():12} | {korean_eto:^12} | {basis_eto:^12} | {existing_eto:^12} | {match_str:^6}")

if __name__ == "__main__":
    # テストする日付リスト
    dates_to_check = [
        date(1900, 1, 31),  # 基準日
        date(1900, 2, 1),   # 基準日の翌日
        date(1972, 9, 24),  # 検証日1
        date(1984, 10, 14), # 検証日2
        date(2018, 8, 18),  # 元のコードのサンプル日
        date(2023, 1, 1),   # 最近の日付
        date(2023, 12, 31), # 最近の日付
        date(2024, 1, 1),   # 閏年の最初の日
        date(2024, 2, 29),  # 閏日
        date(2025, 1, 1)    # 将来の日付
    ]
    
    compare_eto_methods(dates_to_check)
    
    # 対話的に計算する
    try:
        print("\n特定の日付を計算するには、以下に日付を入力してください（YYYY-MM-DD形式）:")
        while True:
            input_date = input("日付 (YYYY-MM-DD) または 'q' で終了: ")
            if input_date.lower() == 'q':
                break
                
            try:
                dt = date.fromisoformat(input_date)
                
                korean_eto = calculate_ilgan_ilsi(dt.year, dt.month, dt.day)
                basis_eto = get_eto_1900_01_31_23_basis(dt)
                existing_eto = eto_existing_method(dt)
                
                print(f"日付: {dt.isoformat()}")
                print(f"  韓国式アルゴリズム: {korean_eto}")
                print(f"  1900/1/31基準     : {basis_eto}")
                print(f"  現在の実装         : {existing_eto}")
                print(f"  一致               : {'○' if korean_eto == basis_eto == existing_eto else '×'}")
                
            except ValueError:
                print("無効な日付形式です。YYYY-MM-DD形式で入力してください。")
    except KeyboardInterrupt:
        print("\n終了します。") 