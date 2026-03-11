"""方位関連の共有定数モジュール.

StarGridPattern / FortuneStatusService / DirectionRuleEngine 等で
重複定義されていた方位定数を一箇所に集約する。
"""
from __future__ import annotations

from typing import Dict, List

# 8方位名（北から時計回り）
DIRECTIONS: List[str] = [
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest",
]

# 方位の反対関係
OPPOSITE_POSITIONS: Dict[str, str] = {
    "north": "south",
    "northeast": "southwest",
    "east": "west",
    "southeast": "northwest",
    "south": "north",
    "southwest": "northeast",
    "west": "east",
    "northwest": "southeast",
}
