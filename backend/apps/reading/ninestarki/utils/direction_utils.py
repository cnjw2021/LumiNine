"""
方位変換用ユーティリティ
"""
from typing import List, Union


def convert_direction_to_japanese(direction: str) -> str:
    """
    英語の方位を日本語に変換する
    
    Args:
        direction (str): 英語の方位（例: "southeast"）
        
    Returns:
        str: 日本語の方位（例: "南東"）
    """
    direction_map = {
        'north': '北',
        'northeast': '北東',
        'east': '東',
        'southeast': '南東',
        'south': '南',
        'southwest': '南西',
        'west': '西',
        'northwest': '北西',
        'center': '中央'
    }
    return direction_map.get(direction.lower(), direction)


def convert_directions_to_japanese(directions: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    方位のリストまたは単一の方位を日本語に変換する
    
    Args:
        directions: 英語の方位または方位のリスト
        
    Returns:
        日本語の方位または方位のリスト
    """
    if isinstance(directions, str):
        return convert_direction_to_japanese(directions)
    elif isinstance(directions, list):
        return [convert_direction_to_japanese(direction) for direction in directions]
    else:
        return directions
