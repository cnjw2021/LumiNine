"""九星間の相性マトリックスモデル"""

from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from core.database import db
from typing import Dict, List, Optional
from core.models.compatibility_level import CompatibilityLevel

class StarCompatibilityMatrix(db.Model):
    """九星間の相性マトリックスモデル
    
    各星から見た他の星との相性関係を相性マトリックス形式で管理します。
    例：一白水星から見た三碧木星が大吉か中吉か小吉か凶かなど
    """
    __tablename__ = 'star_compatibility_matrix'

    base_star = db.Column(db.Integer, db.ForeignKey('stars.star_number'), primary_key=True)
    star_1 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='一白水星との相性')
    star_2 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='二黒土星との相性')
    star_3 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='三碧木星との相性')
    star_4 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='四緑木星との相性')
    star_5 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='五黄土星との相性')
    star_6 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='六白金星との相性')
    star_7 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='七赤金星との相性')
    star_8 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='八白土星との相性')
    star_9 = db.Column(db.Enum(CompatibilityLevel), nullable=False, comment='九紫火星との相性')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    base_star_rel = relationship('NineStar', foreign_keys=[base_star])

    def __init__(self, base_star: int, star_1: CompatibilityLevel, star_2: CompatibilityLevel, 
                 star_3: CompatibilityLevel, star_4: CompatibilityLevel, star_5: CompatibilityLevel, 
                 star_6: CompatibilityLevel, star_7: CompatibilityLevel, star_8: CompatibilityLevel, 
                 star_9: CompatibilityLevel):
        """コンストラクタ
        
        Args:
            base_star (int): 基準となる星の番号（1-9）
            star_1 (CompatibilityLevel): 一白水星との相性
            star_2 (CompatibilityLevel): 二黒土星との相性
            star_3 (CompatibilityLevel): 三碧木星との相性
            star_4 (CompatibilityLevel): 四緑木星との相性
            star_5 (CompatibilityLevel): 五黄土星との相性
            star_6 (CompatibilityLevel): 六白金星との相性
            star_7 (CompatibilityLevel): 七赤金星との相性
            star_8 (CompatibilityLevel): 八白土星との相性
            star_9 (CompatibilityLevel): 九紫火星との相性
        """
        self.base_star = base_star
        self.star_1 = star_1
        self.star_2 = star_2
        self.star_3 = star_3
        self.star_4 = star_4
        self.star_5 = star_5
        self.star_6 = star_6
        self.star_7 = star_7
        self.star_8 = star_8
        self.star_9 = star_9

    def to_dict(self) -> Dict:
        """モデルを辞書形式に変換
        
        Returns:
            Dict: モデルの辞書表現
        """
        return {
            'base_star': self.base_star,
            'star_1': self.star_1.value if self.star_1 else None,
            'star_2': self.star_2.value if self.star_2 else None,
            'star_3': self.star_3.value if self.star_3 else None,
            'star_4': self.star_4.value if self.star_4 else None,
            'star_5': self.star_5.value if self.star_5 else None,
            'star_6': self.star_6.value if self.star_6 else None,
            'star_7': self.star_7.value if self.star_7 else None,
            'star_8': self.star_8.value if self.star_8 else None,
            'star_9': self.star_9.value if self.star_9 else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_compatibility_level(self, target_star: int) -> CompatibilityLevel:
        """指定された星との相性レベルを取得
        
        Args:
            target_star (int): 判定対象の星番号（1-9）
            
        Returns:
            CompatibilityLevel: 相性レベル
            
        Raises:
            ValueError: 無効な星番号が指定された場合
        """
        if not 1 <= target_star <= 9:
            raise ValueError(f"Invalid star number: {target_star}")
            
        star_map = {
            1: self.star_1,
            2: self.star_2,
            3: self.star_3,
            4: self.star_4,
            5: self.star_5,
            6: self.star_6,
            7: self.star_7,
            8: self.star_8,
            9: self.star_9
        }
        return star_map[target_star]

    def is_auspicious(self, target_star: int) -> bool:
        """指定された星との相性が吉かどうかを判定（BAD以外は吉と判断）
        
        Args:
            target_star (int): 判定対象の星番号（1-9）
            
        Returns:
            bool: 吉の場合True、凶の場合False
        """
        compatibility = self.get_compatibility_level(target_star)
        return compatibility != CompatibilityLevel.BAD

    def is_best_match(self, target_star: int) -> bool:
        """指定された星との相性が大吉(BEST)かどうかを判定
        
        Args:
            target_star (int): 判定対象の星番号（1-9）
            
        Returns:
            bool: 大吉の場合True、それ以外はFalse
        """
        compatibility = self.get_compatibility_level(target_star)
        return compatibility == CompatibilityLevel.BEST

    def get_stars_by_compatibility(self, level: CompatibilityLevel) -> List[int]:
        """指定した相性レベルの星のリストを取得
        
        Args:
            level (CompatibilityLevel): 取得したい相性レベル
            
        Returns:
            List[int]: 指定した相性レベルの星番号のリスト
        """
        stars = []
        for star_num in range(1, 10):
            if self.get_compatibility_level(star_num) == level:
                stars.append(star_num)
        return stars

    def get_auspicious_stars(self) -> List[int]:
        """この星から見た吉となる星のリストを取得（BAD以外すべて）
        
        Returns:
            List[int]: 吉となる星番号のリスト
        """
        auspicious_stars = []
        for star_num in range(1, 10):
            if self.is_auspicious(star_num):
                auspicious_stars.append(star_num)
        return auspicious_stars

    def get_inauspicious_stars(self) -> List[int]:
        """この星から見た凶となる星のリストを取得
        
        Returns:
            List[int]: 凶となる星番号のリスト
        """
        return self.get_stars_by_compatibility(CompatibilityLevel.BAD)

    def get_best_stars(self) -> List[int]:
        """この星から見た大吉となる星のリストを取得
        
        Returns:
            List[int]: 大吉となる星番号のリスト
        """
        return self.get_stars_by_compatibility(CompatibilityLevel.BEST)

    def get_better_stars(self) -> List[int]:
        """この星から見た中吉となる星のリストを取得
        
        Returns:
            List[int]: 中吉となる星番号のリスト
        """
        return self.get_stars_by_compatibility(CompatibilityLevel.BETTER)

    def get_good_stars(self) -> List[int]:
        """この星から見た小吉となる星のリストを取得
        
        Returns:
            List[int]: 小吉となる星番号のリスト
        """
        return self.get_stars_by_compatibility(CompatibilityLevel.GOOD)

    @classmethod
    def get_by_base_star(cls, base_star: int) -> Optional['StarCompatibilityMatrix']:
        """基準となる星から相性を取得
        
        Args:
            base_star (int): 基準となる星の番号（1-9）
            
        Returns:
            Optional[StarCompatibilityMatrix]: 相性のマトリックス。存在しない場合はNone
        """
        return cls.query.filter_by(base_star=base_star).first() 