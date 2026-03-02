#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九星気学 – 年盤による方位吉凶判定
=================================

CSVデータを使用して各方位の吉凶を判定します
"""

from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import json

# ロギング設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# CSVファイルパス
CSV_DIR = Path("./backend/data/csv")
STAR_COMPATIBILITY_CSV = CSV_DIR / "star_compatibility_matrix.csv"
SOLAR_STARTS_CSV = CSV_DIR / "solar_starts_data.csv"

# 互換性レベルの定義
class CompatibilityLevel(Enum):
    BEST = "best"
    BETTER = "better"
    GOOD = "good"
    BAD = "bad"

class StarCompatibilityMatrix:
    """星の相性マトリクスを表現するクラス（CSVデータ使用版）"""
    
    # クラス変数としてデータを保持
    __compatibility_data = None
    
    @classmethod
    def load_data(cls):
        """CSVから相性データを読み込む"""
        if cls.__compatibility_data is None:
            try:
                df = pd.read_csv(STAR_COMPATIBILITY_CSV)
                cls.__compatibility_data = {}
                
                # CSVデータを辞書形式に変換
                for _, row in df.iterrows():
                    base_star = int(row["base_star"])
                    compatibility = {}
                    for i in range(1, 10):
                        col_name = f"star_{i}"
                        if col_name in row:
                            # 値を判定（例：true/false または BEST/BETTER/GOOD/BAD など）
                            value = row[col_name]
                            if isinstance(value, bool):
                                compatibility[i] = CompatibilityLevel.GOOD if value else CompatibilityLevel.BAD
                            elif isinstance(value, str):
                                if value.lower() == "best":
                                    compatibility[i] = CompatibilityLevel.BEST
                                elif value.lower() == "better":
                                    compatibility[i] = CompatibilityLevel.BETTER
                                elif value.lower() == "good":
                                    compatibility[i] = CompatibilityLevel.GOOD
                                else:
                                    compatibility[i] = CompatibilityLevel.BAD
                            else:
                                compatibility[i] = CompatibilityLevel.BAD
                    
                    cls.__compatibility_data[base_star] = compatibility
                
                logger.info(f"Successfully loaded star compatibility data for {len(cls.__compatibility_data)} stars")
            except Exception as e:
                logger.error(f"Failed to load star compatibility data: {str(e)}")
                # 最低限の互換性データを提供（すべてGOOD）
                cls.__compatibility_data = {}
                default_compatibility = {i: CompatibilityLevel.GOOD for i in range(1, 10)}
                for i in range(1, 10):
                    cls.__compatibility_data[i] = default_compatibility.copy()
    
    @classmethod
    def get_by_base_star(cls, base_star: int) -> Optional[StarCompatibilityMatrix]:
        """基準星の相性マトリクスを取得"""
        # データがまだ読み込まれていない場合は読み込む
        if cls.__compatibility_data is None:
            cls.load_data()
            
        if base_star not in cls.__compatibility_data:
            logger.warning(f"No compatibility data for base star {base_star}")
            return None
            
        matrix = StarCompatibilityMatrix()
        matrix.base_star = base_star
        matrix.compatibility = cls.__compatibility_data[base_star]
        return matrix
    
    def get_compatibility_level(self, target_star: int) -> CompatibilityLevel:
        """対象星との相性レベルを取得"""
        if target_star not in self.compatibility:
            logger.warning(f"No compatibility data for target star {target_star}")
            return CompatibilityLevel.BAD
            
        return self.compatibility[target_star]

def get_zodiac_opposite_direction(zodiac: str) -> str:
    """干支の反対方位を返す（破の判定用）"""
    # 十二支から方位への変換（九星気学の方位）
    zodiac_to_direction = {
        "子": "北", "丑": "北東", "寅": "東", "卯": "西",
        "辰": "南東", "巳": "南西", "午": "南", "未": "南東",
        "申": "東", "酉": "東", "戌": "北東", "亥": "北東"
    }
    
    # 反対方位の対応
    opposite_directions = {
        "北": "南", "北東": "南西", "東": "西", "南東": "北西",
        "南": "北", "南西": "北東", "西": "東", "北西": "南東"
    }
    
    # 与えられた干支が複合的（例：甲寅）なので、最後の文字だけ抽出
    branch = zodiac[-1] if zodiac else ""
    
    if branch not in zodiac_to_direction:
        raise ValueError(f"Invalid zodiac branch: {branch}")
        
    direction = zodiac_to_direction[branch]
    opposite = opposite_directions.get(direction, "")
    
    return opposite

class YearBoard:
    """九星気学の年盤を表現するクラス"""
    
    def __init__(self, center_star: int):
        """
        中心星から年盤を初期化
        
        Args:
            center_star: 中心星の番号（1-9）
        """
        self.center_star = center_star
        self.positions = self._place_stars()
        
    def _place_stars(self) -> Dict[str, int]:
        """中心星から各方位の星を計算"""
        # ハードコードされた星の配置（図に基づく）
        position_patterns = {
            1: {"北": 6, "北東": 4, "東": 8, "南東": 9, "南": 5, "南西": 7, "西": 3, "北西": 2},
            2: {"北": 7, "北東": 5, "東": 9, "南東": 1, "南": 6, "南西": 8, "西": 4, "北西": 3},
            3: {"北": 8, "北東": 6, "東": 1, "南東": 2, "南": 7, "南西": 9, "西": 5, "北西": 4},
            4: {"北": 9, "北東": 7, "東": 2, "南東": 3, "南": 8, "南西": 1, "西": 6, "北西": 5},
            5: {"北": 1, "北東": 8, "東": 3, "南東": 4, "南": 9, "南西": 2, "西": 7, "北西": 6},
            6: {"北": 2, "北東": 9, "東": 4, "南東": 5, "南": 1, "南西": 3, "西": 8, "北西": 7},
            7: {"北": 3, "北東": 1, "東": 5, "南東": 6, "南": 2, "南西": 4, "西": 9, "北西": 8},
            8: {"北": 4, "北東": 2, "東": 6, "南東": 7, "南": 3, "南西": 5, "西": 1, "北西": 9},
            9: {"北": 5, "北東": 3, "東": 7, "南東": 8, "南": 4, "南西": 6, "西": 2, "北西": 1}
        }
        
        if self.center_star not in position_patterns:
            raise ValueError(f"Invalid center star: {self.center_star}")
            
        return position_patterns[self.center_star]
    
    def _get_dark_sword_star(self) -> int:
        """暗剣殺（5の反対側）の星番号を取得
        
        Returns:
            int: 暗剣殺の星番号（1-9）
                 -1: 中央星が5の場合（暗剣殺は存在しない特殊ケース）
            
        Raises:
            ValueError: 5が見つからない場合や5の反対側がマッピングできない場合
        """
        # 中央星が5の場合、暗剣殺は存在しないため-1を返す
        if self.center_star == 5:
            return -1
            
        # 各方位の星番号
        positions = {
            'north': self.north,
            'northeast': self.northeast,
            'east': self.east,
            'southeast': self.southeast,
            'south': self.south,
            'southwest': self.southwest,
            'west': self.west,
            'northwest': self.northwest
        }
        
        # 5がある方位を特定
        five_position = None
        for position, number in positions.items():
            if number == 5:
                five_position = position
                break
        
        # 5が見つからない場合（通常ありえない）
        if five_position is None:
            logger.warning(f"Could not find star 5 in the grid for center star {self.center_star}")
            return -1
            
        # 反対側の方位マッピング
        opposite_positions = {
            'north': 'south',
            'northeast': 'southwest',
            'east': 'west',
            'southeast': 'northwest',
            'south': 'north',
            'southwest': 'northeast',
            'west': 'east',
            'northwest': 'southeast'
        }
        
        # 反対側の方位を取得
        opposite_position = opposite_positions.get(five_position)
        if opposite_position is None:
            logger.warning(f"五黄土星の反対側の方位がマッピングできません: {five_position}")
            return -1
            
        # 反対側の方位の星番号を返す
        return positions.get(opposite_position)
    
    @property
    def north(self) -> int:
        return self.positions.get("北", 0)
        
    @property
    def northeast(self) -> int:
        return self.positions.get("北東", 0)
        
    @property
    def east(self) -> int:
        return self.positions.get("東", 0)
        
    @property
    def southeast(self) -> int:
        return self.positions.get("南東", 0)
        
    @property
    def south(self) -> int:
        return self.positions.get("南", 0)
        
    @property
    def southwest(self) -> int:
        return self.positions.get("南西", 0)
        
    @property
    def west(self) -> int:
        return self.positions.get("西", 0)
        
    @property
    def northwest(self) -> int:
        return self.positions.get("北西", 0)
    
    def get_fortune_status(self, params: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """各方位の吉凶状態を判定して返す
        
        Args:
            params (Dict[str, Any]): 吉凶判定に必要なパラメータ
                - main_star (int): 本命星の番号（1-9）
                - month_star (int): 月命星の番号（1-9）
                - zodiac (str): 今年の干支（例: "甲寅"）
                
        Returns:
            Dict[str, Dict[str, Any]]: 各方位の吉凶状態と具体的なマーク
                {
                    "north": {
                        "is_auspicious": bool,
                        "reason": str or None,
                        "marks": [str, ...] // "dark_sword", "main_star", "month_star", "water_fire", "zodiac_branch_position", "compatibility_matrix" など
                    },
                    "northeast": {...},
                    ...
                }
                
        Raises:
            ValueError: パラメータが不正な場合や判定に必要な情報が不足している場合
            RuntimeError: 判定処理中に想定外のエラーが発生した場合
        """
        # パラメータの取得と検証
        main_star = params.get('main_star', 0)
        month_star = params.get('month_star', 0)
        zodiac = params.get('zodiac', '')
        
        # logger.debug(f"Calculating fortune status with params: main_star={main_star}, month_star={month_star}, zodiac={zodiac}")
        
        if not all([isinstance(main_star, int), isinstance(month_star, int), isinstance(zodiac, str)]):
            raise ValueError("Invalid parameter types")
            
        if not (1 <= main_star <= 9 and 1 <= month_star <= 9):
            raise ValueError("Star numbers must be between 1 and 9")
        
        # 干支の反対方位を取得（破）
        zodiac_opposite_direction = ""
        try:
            zodiac_opposite_direction = get_zodiac_opposite_direction(zodiac)
        except ValueError as e:
            logger.error(f"Error determining opposite direction from zodiac: {str(e)}")
            # エラーがあっても処理を継続
            logger.warning("Continuing without zodiac opposite direction")
        
        # 暗剣殺の星を取得
        dark_sword_star = -1
        try:
            dark_sword_star = self._get_dark_sword_star()
        except ValueError as e:
            logger.error(f"Error getting dark sword star: {str(e)}")
            raise RuntimeError(f"Failed to determine dark sword star: {str(e)}") from e
        
        # 各方位の星番号を取得
        directions = {
            'north': self.north,
            'northeast': self.northeast,
            'east': self.east,
            'southeast': self.southeast,
            'south': self.south,
            'southwest': self.southwest,
            'west': self.west,
            'northwest': self.northwest
        }
        
        # 方位の反対関係を定義
        opposite_positions = {
            'north': 'south',
            'northeast': 'southwest',
            'east': 'west',
            'southeast': 'northwest',
            'south': 'north',
            'southwest': 'northeast',
            'west': 'east',
            'northwest': 'southeast'
        }
        
        # 日本語方位から英語方位への変換
        jp_to_en_directions = {
            "北": "north",
            "北東": "northeast",
            "東": "east",
            "南東": "southeast",
            "南": "south",
            "南西": "southwest",
            "西": "west",
            "北西": "northwest"
        }
        
        # 干支の反対方位を英語に変換（存在する場合）
        zodiac_opposite_direction_en = jp_to_en_directions.get(zodiac_opposite_direction, "")
        
        # 本命星と月命星の位置を追跡（1つだけ）
        main_star_position = None
        month_star_position = None
        
        # 九星相性マトリックスを取得
        compatibility_matrix = StarCompatibilityMatrix.get_by_base_star(main_star)
        if not compatibility_matrix:
            logger.error(f"Star compatibility matrix not found for center star {main_star}")
            raise RuntimeError(f"Star compatibility matrix not found for center star {main_star}")
        
        # 各方位の吉凶を判定
        results = {}
        
        # 最初のパス: 基本的な判定を行う
        for direction, star_number in directions.items():
            # デフォルトは吉
            result = {
                "is_auspicious": True,
                "reason": None,
                "marks": []
            }
            
            if star_number == 5:
                result["is_auspicious"] = False
                result["reason"] = "五黄殺"
                result["marks"].append("five_yellow")
            
            # ２）暗剣殺の判定
            if dark_sword_star == -1:
                # 中央星が5の場合は暗剣殺判定をスキップ
                result["marks"].append("no_dark_sword_center_five")
            else:
                # 暗剣殺の星を凶とする
                if star_number == dark_sword_star:
                    result["is_auspicious"] = False
                    result["reason"] = "暗剣殺"
                    result["marks"].append("dark_sword")
            
            # ３）本命星と月命星の判定
            if star_number == main_star:
                result["is_auspicious"] = False
                result["reason"] = "本命殺" if not result["reason"] else result["reason"] + ", 本命殺"
                result["marks"].append("main_star")
                main_star_position = direction
            
            if star_number == month_star:
                result["is_auspicious"] = False
                result["reason"] = "月命殺" if not result["reason"] else result["reason"] + ", 月命殺"
                result["marks"].append("month_star")
                month_star_position = direction
            
            # ４）水火殺の判定
            if (star_number == 1 or star_number == 9) and (self.south == 1 or self.north == 9):
                result["is_auspicious"] = False
                result["reason"] = "水火殺" if not result["reason"] else result["reason"] + ", 水火殺"
                result["marks"].append("water_fire")
            
            # 5）干支の反対方位（破）の判定
            if direction == zodiac_opposite_direction_en and zodiac_opposite_direction_en:
                result["is_auspicious"] = False
                result["reason"] = "破" if not result["reason"] else result["reason"] + ", 破"
                result["marks"].append("zodiac_opposite_direction")
            
            # ６）九星相性マトリックスによる判定
            # まず相性レベルを取得（BEST, BETTER, GOOD, BAD）
            compatibility_level = compatibility_matrix.get_compatibility_level(star_number)
            # 相性レベルを結果オブジェクトに保存（フロントエンド用）
            result["compatibility_level"] = compatibility_level.value
            # 相性マトリクスのデバッグ情報を追加
            result["debug_info"] = f"相性: 本命星{main_star}と{star_number}の相性は{compatibility_level.value}"
            # BADの場合は凶と判定
            if compatibility_level == CompatibilityLevel.BAD:
                result["is_auspicious"] = False
                result["reason"] = "凶方星" if not result["reason"] else result["reason"] + ", 凶方星"
                result["marks"].append("compatibility_matrix")
            
            results[direction] = result
        
        # 本命的殺
        if main_star_position:
            opposite_pos = opposite_positions.get(main_star_position)
            if opposite_pos:
                results[opposite_pos]["is_auspicious"] = False
                results[opposite_pos]["reason"] = "本命的殺" if not results[opposite_pos]["reason"] else results[opposite_pos]["reason"] + ", 本命的殺"
                results[opposite_pos]["marks"].append("main_star_opposite")
        
        # 月命的殺
        if month_star_position:
            opposite_pos = opposite_positions.get(month_star_position)
            if opposite_pos:
                results[opposite_pos]["is_auspicious"] = False
                results[opposite_pos]["reason"] = "月命的殺" if not results[opposite_pos]["reason"] else results[opposite_pos]["reason"] + ", 月命的殺"
                results[opposite_pos]["marks"].append("month_star_opposite")
        
        return results

def load_year_data(year: int) -> Dict[str, Any]:
    """指定された年の年盤データを読み込む"""
    try:
        df = pd.read_csv(SOLAR_STARTS_CSV)
        year_data = df[df['year'] == year]
        
        if year_data.empty:
            logger.warning(f"No data found for year {year}")
            return {"year": year, "center_star": 5, "zodiac": ""}
            
        row = year_data.iloc[0]
        return {
            "year": year,
            "center_star": int(row["star_number"]),
            "zodiac": row["zodiac"] if "zodiac" in row else ""
        }
    except Exception as e:
        logger.error(f"Error loading year data: {str(e)}")
        return {"year": year, "center_star": 5, "zodiac": ""}

def get_fortune_directions(year: int, main_star: int, month_star: int = 0) -> Dict[str, Dict[str, Any]]:
    """
    指定された年の吉方位を取得
    
    Args:
        year: 年
        main_star: 本命星（1-9）
        month_star: 月命星（1-9）、指定されない場合は本命星と同じ
    
    Returns:
        各方位の吉凶状態
    """
    # 月命星が指定されていない場合は本命星を使用
    if month_star <= 0:
        month_star = main_star
    
    # 年盤データを取得
    year_data = load_year_data(year)
    center_star = year_data["center_star"]
    zodiac = year_data["zodiac"]
    
    try:
        zodiac_dir = get_zodiac_opposite_direction(zodiac)
    except Exception as e:
        raise RuntimeError(f"Failed to get opposite direction: {str(e)}") from e
    
    # 年盤を構築
    year_board = YearBoard(center_star)
    
    # 吉凶判定
    params = {
        "main_star": main_star,
        "month_star": month_star,
        "zodiac": zodiac
    }
    
    fortune_status = year_board.get_fortune_status(params)
    return fortune_status

# テスト用のメイン処理
if __name__ == "__main__":
    import sys
    
    # コマンドライン引数の処理
    if len(sys.argv) < 3:
        print("Usage: python fortune_direction_year.py YEAR MAIN_STAR [MONTH_STAR]")
        sys.exit(1)
    
    year = int(sys.argv[1])
    main_star = int(sys.argv[2])
    month_star = int(sys.argv[3]) if len(sys.argv) > 3 else main_star
    
    # 吉方位を計算
    results = get_fortune_directions(year, main_star, month_star)
    
    # 結果を表示
    print(f"★ {year}年の本命星{main_star}、月命星{month_star}の吉凶方位")
    print("-" * 60)
    
    # 吉方位と凶方位を分けて表示
    auspicious = []
    inauspicious = []
    
    for direction, data in results.items():
        japanese_dir = {
            "north": "北", "northeast": "北東", "east": "東", "southeast": "南東",
            "south": "南", "southwest": "南西", "west": "西", "northwest": "北西"
        }.get(direction, direction)
        
        if data["is_auspicious"]:
            auspicious.append(f"{japanese_dir}: {data.get('reason', '吉')}")
        else:
            inauspicious.append(f"{japanese_dir}: {data.get('reason', '凶')}")
    
    print("【吉方位】")
    for dir_info in auspicious:
        print(f"  {dir_info}")
    
    print("\n【凶方位】")
    for dir_info in inauspicious:
        print(f"  {dir_info}")
    
    # 詳細なJSON出力（オプション）
    # print("\n詳細情報:")
    # print(json.dumps(results, ensure_ascii=False, indent=2))