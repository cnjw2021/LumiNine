from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import db
from core.utils.logger import get_logger
from core.utils.calendar_utils import get_opposite_zodiac_direction
from typing import Dict, List, Tuple, Optional, Any
from core.models.star_compatibility_matrix import StarCompatibilityMatrix
from core.models.compatibility_level import CompatibilityLevel

logger = get_logger(__name__)

class StarGridPattern(db.Model):
    """九星盤の星配置パターンモデル"""
    __tablename__ = 'star_grid_patterns'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    center_star = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False, unique=True)
    north = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    northeast = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    east = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    southeast = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    south = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    southwest = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    west = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    northwest = db.Column(db.Integer, db.ForeignKey('stars.star_number'), nullable=False)
    
    season_start = db.Column(db.String(50), nullable=True)
    season_end = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップの定義
    center_star_rel = relationship('NineStar', foreign_keys=[center_star], backref='center_patterns')
    north_star_rel = relationship('NineStar', foreign_keys=[north], backref='north_patterns')
    northeast_star_rel = relationship('NineStar', foreign_keys=[northeast], backref='northeast_patterns')
    east_star_rel = relationship('NineStar', foreign_keys=[east], backref='east_patterns')
    southeast_star_rel = relationship('NineStar', foreign_keys=[southeast], backref='southeast_patterns')
    south_star_rel = relationship('NineStar', foreign_keys=[south], backref='south_patterns')
    southwest_star_rel = relationship('NineStar', foreign_keys=[southwest], backref='southwest_patterns')
    west_star_rel = relationship('NineStar', foreign_keys=[west], backref='west_patterns')
    northwest_star_rel = relationship('NineStar', foreign_keys=[northwest], backref='northwest_patterns')

    def __repr__(self):
        return f"<StarGridPattern center_star={self.center_star}>"
    
    def to_dict(self):
        """モデルを辞書に変換（created_at, updated_at は除外）"""
        return {
            'id': self.id,
            'center_star': self.center_star,
            'north': self.north,
            'northeast': self.northeast,
            'east': self.east,
            'southeast': self.southeast,
            'south': self.south,
            'southwest': self.southwest,
            'west': self.west,
            'northwest': self.northwest,
            'season_start': self.season_start,
            'season_end': self.season_end
        }
    
    @classmethod
    def get_by_center_star(cls, center_star):
        """中央の星から九星盤パターンを取得"""
        return cls.query.filter_by(center_star=center_star).first()
    
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
        
        # 干支の向かい側の方位を取得（破）
        opposite_zodiac_direction = ""
        try:
            opposite_zodiac_direction = get_opposite_zodiac_direction(zodiac)
        except ValueError as e:
            logger.error(f"Error determining opposite direction from zodiac: {str(e)}")
            # エラーがあっても処理を継続
            logger.warning("Continuing without opposite zodiac direction")
        
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
            
            # 5）干支の向かい側（破）の判定
            if direction == opposite_zodiac_direction and opposite_zodiac_direction:
                result["is_auspicious"] = False
                result["reason"] = "破" if not result["reason"] else result["reason"] + ", 破"
                result["marks"].append("opposite_zodiac")
            
            # ６）九星相性マトリックスによる判定
            # まず相性レベルを取得（BEST, BETTER, GOOD, BAD）
            compatibility_level = compatibility_matrix.get_compatibility_level(star_number)
            # 相性レベルを結果オブジェクトに保存（フロントエンド用）
            result["compatibility_level"] = compatibility_level.value
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

    def get_time_fortune_status(self, params: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """時の運気情報を判定して返す
        
        Args:
            params (Dict[str, Any]): 吉凶判定に必要なパラメータ
                - zodiac (str): 今年の干支（例: "甲寅"）
                - main_star (int): 本命星の番号（1-9）
        Returns:
            Dict[str, Dict[str, Any]]: 各方位の吉凶状態と具体的なマーク
                {
                    "north": {
                        "is_auspicious": bool,
                        "reason": str or None,
                        "marks": [str, ...] // "dark_sword", "main_star", "month_star", "water_fire", "zodiac_branch_position", "compatibility_matrix" など
                        "is_main_star": bool
                    },
                    "northeast": {...},
                    ...
                    "center": {...} // 中央の情報も含む
                }
                
        Raises:
            ValueError: パラメータが不正な場合や判定に必要な情報が不足している場合
            RuntimeError: 判定処理中に想定外のエラーが発生した場合
        """
        # パラメータの取得と検証
        zodiac = params.get('zodiac', '')
        main_star = params.get('main_star', 0)

        if main_star == 0:
            raise ValueError("Main star is required")

        # logger.debug(f"Calculating fortune status with params: zodiac={zodiac}")
        
        if not isinstance(zodiac, str):
            raise ValueError("Invalid parameter types")
            
        # 干支の向かい側の方位を取得（破）
        opposite_zodiac_direction = ""
        try:
            opposite_zodiac_direction = get_opposite_zodiac_direction(zodiac)
        except ValueError as e:
            logger.error(f"Error determining opposite direction from zodiac: {str(e)}")
            # エラーがあっても処理を継続
            logger.warning("Continuing without opposite zodiac direction")
        
        # 暗剣殺の星を取得
        dark_sword_star = -1
        try:
            dark_sword_star = self._get_dark_sword_star()
        except ValueError as e:
            logger.error(f"Error getting dark sword star: {str(e)}")
            raise RuntimeError(f"Failed to determine dark sword star: {str(e)}") from e
        
        # 各方位の星番号を取得（中央も含める）
        directions = {
            'north': self.north,
            'northeast': self.northeast,
            'east': self.east,
            'southeast': self.southeast,
            'south': self.south,
            'southwest': self.southwest,
            'west': self.west,
            'northwest': self.northwest,
            'center': self.center_star  # 中央の星を追加
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
        
        # 各方位の吉凶を判定
        results = {}
        
        # 最初のパス: 基本的な判定を行う
        for direction, star_number in directions.items():
            # デフォルトは吉
            result = {
                "is_auspicious": True,
                "reason": None,
                "marks": [],
                "is_main_star": False
            }
            
            # 中央の場合は特別な処理
            if direction == 'center':
                # 中央は暗剣殺判定などはスキップして、本命星判定のみ行う
                if star_number == main_star:
                    result["is_main_star"] = True
                    result["is_auspicious"] = False
                results[direction] = result
                continue
            
            # 1）暗剣殺の判定
            if dark_sword_star == -1:
                # 中央星が5の場合は暗剣殺判定をスキップ
                result["marks"].append("no_dark_sword_center_five")
            else:
                # 暗剣殺の星を凶とする
                if star_number == dark_sword_star:
                    result["is_auspicious"] = False
                    result["reason"] = "暗剣殺"
                    result["marks"].append("dark_sword")
            
            # 2）水火殺の判定
            if (star_number == 1 or star_number == 9) and (self.south == 1 or self.north == 9):
                result["is_auspicious"] = False
                result["reason"] = "水火殺" if not result["reason"] else result["reason"] + ", 水火殺"
                result["marks"].append("water_fire")
            
            # 3）干支の向かい側（破）の判定
            if direction == opposite_zodiac_direction and opposite_zodiac_direction:
                result["is_auspicious"] = False
                result["reason"] = "破" if not result["reason"] else result["reason"] + ", 破"
                result["marks"].append("opposite_zodiac")

            # 4）本命星の判定
            if star_number == main_star:
                result["is_main_star"] = True

            results[direction] = result
        
        return results

    def get_dark_sword_direction(self) -> Optional[str]:
        """暗剣殺の方位を取得する

        Returns:
            Optional[str]: 暗剣殺の方位（"north", "northeast"など）
                         暗剣殺が存在しない場合はNone

        Raises:
            ValueError: 暗剣殺の方位が特定できない場合
        """
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

        # 暗剣殺の星番号を取得
        try:
            dark_sword_star = self._get_dark_sword_star()
            if dark_sword_star == -1:
                return None

            # 暗剣殺の星がある方位を探す
            for direction, star in directions.items():
                if star == dark_sword_star:
                    return direction

            return None

        except ValueError:
            return None

    def _get_dark_sword_star(self) -> int:
        """暗剣殺（5の反対側）の星番号を取得
        
        Returns:
            int: 暗剣殺の星番号（1-9）
                 -1: 中央星が5の場合（暗剣殺は存在しない特殊ケース）
            
        Raises:
            ValueError: 5が見つからない場合や5の反対側がマッピングできない場合
        """
        # 中央星が5の場合は暗剣殺は存在しない（特殊ケース）
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
            'northwest': self.northwest,
            'center': self.center_star
        }
        
        # 5がある方位を特定
        five_position = None
        for position, number in positions.items():
            if number == 5:
                five_position = position
                break
        
        # 5が見つからない場合（通常ありえない）
        if five_position is None:
            raise ValueError("星盤に五黄土星が存在しません")
            
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
            raise ValueError(f"五黄土星の反対側の方位がマッピングできません: {five_position}")
            
        # 反対側の方位の星番号を返す
        return positions.get(opposite_position)
