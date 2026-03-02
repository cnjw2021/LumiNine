import pandas as pd
import re

def convert_csv_file(input_file):
    """
    指定されたCSVファイルを読み込み、指定された形式に変換します。

    Args:
        input_file (str): 変換するCSVファイルのパス。

    Returns:
        pandas.DataFrame: 変換後のデータを含む DataFrame。
                          エラーが発生した場合は None を返します。
    """
    try:
        # CSVファイルをDataFrameとして読み込む
        df = pd.read_csv(input_file, dtype=str)  # すべての列を文字列として読み込む

        results = []
        for index, row in df.iterrows():
            year_str = str(row['西暦']).replace('年', '')

            month_map = {
                '2月（年初）': 2, '3月': 3, '4月': 4, '5月': 5, '6月': 6,
                '7月': 7, '8月': 8, '9 月': 9, '10月': 10, '11月': 11,
                '12月': 12, '翌年1月': 1
            }

            time_col_map = {
                2: 'time_2', 3: 'time_3', 4: 'time_4', 5: 'time_5', 6: 'time_6',
                7: 'time_7', 8: 'time_8', 9: 'time_9', 10: 'time_10', 11: 'time_11',
                12: 'time_12', 1: 'time_nextyear_1'
            }

            for month_col, month in month_map.items():
                date_str = str(row[month_col])  # 文字列に変換
                time_str = str(row[time_col_map[month]])  # 文字列に変換

                month_day_match = re.match(r'(\d+)月(\d+)日', date_str)
                if month_day_match:
                    day = int(month_day_match.group(2))
                    current_year = int(year_str)
                    if month == 1:
                        current_year += 1

                    iso_date = f"{current_year:04d}-{month:02d}-{day:02d}"

                    results.append({
                        'year': current_year,
                        'month': month,
                        'date': iso_date,
                        'time': time_str
                    })

        df_converted = pd.DataFrame(results)
        return df_converted

    except FileNotFoundError:
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# CSVファイル名を指定して変換
input_csv_file = 'mannenkoyomi_add_zodiac_star - 80年分_zodiac_star.csv'
df_converted = convert_csv_file(input_csv_file)

if df_converted is not None:
    print(df_converted)
    df_converted.to_csv('converted_data.csv', index=False, encoding='utf-8')
    print("\n'converted_data.csv' に保存しました。")
