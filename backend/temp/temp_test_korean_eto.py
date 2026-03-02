# -*- coding: utf-8 -*-
from math import floor
from datetime import date

# 10干（甲〜癸）
heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 12支（子〜亥）
earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def calculate_ilgan_ilsi(y: int, m: int, d: int) -> str:
    # 규칙 1: 1월, 2월은 전년도 취급
    if m == 1 or m == 2:
        y -= 1
        m += 12

    c = y // 100      # 세기
    n = y % 100       # 나머지 연도

    # 일간 계산 (mod 10)
    p = (4 * c + floor(c / 4) + 5 * n + floor(n / 4) + floor((3 * m + 3) / 5) + d + 7) % 10

    # 일支 계산 (mod 12)
    q = (8 * c + floor(c / 4) + 5 * n + floor(n / 4) + 6 * m + floor((3 * m + 3) / 5) + d + 1) % 12

    stem = heavenly_stems[p - 1 if p != 0 else 9]     # p=0일 때는 10번째인 癸
    branch = earthly_branches[q - 1 if q != 0 else 11]  # q=0일 때는 12번째인 亥

    return stem + branch

# 예시 실행
date_example = date(2018, 8, 18)
print(f"{date_example} → 일간일지: {calculate_ilgan_ilsi(date_example.year, date_example.month, date_example.day)}")

# 追加のテスト日付
test_dates = [
    date(1972, 9, 24),
    date(1984, 10, 14),
    date(2017, 2, 21),
    date(2018, 3, 22),
    date(2019, 4, 23),
    date(2020, 5, 24),
    date(2021, 6, 25),
    date(2022, 7, 26)
]

print("\n他の日付のテスト結果:")
for dt in test_dates:
    eto = calculate_ilgan_ilsi(dt.year, dt.month, dt.day)
    print(f"{dt} → 干支: {eto}") 