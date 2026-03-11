"""九星盤パターン 도메인 Value Object.

ORM モデル (core.models.star_grid_pattern.StarGridPattern) から分離された
不変ドメイン型。方位別の星番号のみを保持し、インフラ関心事
(SQLAlchemy relationship や timestamp など) を含まない。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StarGridPatternVO:
    """九星盤の星配置パターンを表す不変 Value Object.

    Attributes:
        center_star: 중궁성 번호 (1~9)
        north ~ northwest: 각 방위의 별 번호 (1~9)
    """
    center_star: int
    north: int
    northeast: int
    east: int
    southeast: int
    south: int
    southwest: int
    west: int
    northwest: int

    def to_dict(self) -> dict:
        """어플리케이션/프레젠터 계층에서 직렬화에 사용."""
        return {
            "center_star": self.center_star,
            "north": self.north,
            "northeast": self.northeast,
            "east": self.east,
            "southeast": self.southeast,
            "south": self.south,
            "southwest": self.southwest,
            "west": self.west,
            "northwest": self.northwest,
        }
