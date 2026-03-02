"""Utility functions for chart calculations."""

import math

def calculate_pie_chart_coordinates(scores):
    """円グラフの座標を事前計算する関数"""
    total = sum(score[1] for score in scores)
    result = []
    cumulative_angle = 0
    
    for label, value, color in scores:
        percentage = round((value / total) * 100)
        angle = (value / total) * 360
        current_angle = cumulative_angle
        next_angle = current_angle + angle
        
        # 開始点の座標
        start_x = 50 + 40 * math.cos(math.radians(current_angle - 90))
        start_y = 50 + 40 * math.sin(math.radians(current_angle - 90))
        
        # 終了点の座標
        end_x = 50 + 40 * math.cos(math.radians(next_angle - 90))
        end_y = 50 + 40 * math.sin(math.radians(next_angle - 90))
        
        # テキストの座標
        text_angle = current_angle + (angle / 2) - 90
        text_x = 50 + 25 * math.cos(math.radians(text_angle))
        text_y = 50 + 25 * math.sin(math.radians(text_angle))
        
        result.append({
            'label': label,
            'percentage': percentage,
            'color': color,
            'start_x': round(start_x, 2),
            'start_y': round(start_y, 2),
            'end_x': round(end_x, 2),
            'end_y': round(end_y, 2),
            'text_x': round(text_x, 2),
            'text_y': round(text_y, 2),
            'large_arc': '1' if angle > 180 else '0'
        })
        
        cumulative_angle = next_angle
    
    return result 