from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class CompatibilityMaster(db.Model):
    __tablename__ = 'compatibility_master'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    main_star = Column(Integer, ForeignKey('stars.star_number'), nullable=False, 
                     comment='主星 (判断する側の本命星) 番号')
    main_birth_month = Column(Integer, nullable=True, 
                           comment='主星の持ち主の生まれ月 (NULL の場合は月に関係なく適用)')
    target_star = Column(Integer, ForeignKey('stars.star_number'), nullable=False, 
                       comment='対象星 (相手の本命星) 番号')
    target_birth_month = Column(Integer, nullable=True, 
                             comment='対象星の持ち主の生まれ月 (NULL の場合は月に関係なく適用)')
    symbols_male = Column(String(10), nullable=False, 
                        comment='男性の相性記号 (★,○,P,F,N,▲ など)')
    symbols_female = Column(String(10), nullable=False, 
                          comment='女性の相性記号 (★,○,P,F,N,▲ など)')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('main_star', 'main_birth_month', 'target_star', 'target_birth_month', 
                        'symbols_male', 'symbols_female', name='unique_compatibility'),
        Index('idx_main_star', 'main_star'),
        Index('idx_main_birth_month', 'main_birth_month'),
        Index('idx_target_star', 'target_star'),
        Index('idx_target_birth_month', 'target_birth_month'),
        Index('idx_symbols_male', 'symbols_male'),
        Index('idx_symbols_female', 'symbols_female'),
    )

    def __init__(self, main_star, target_star, symbols_male, symbols_female, 
                main_birth_month=None, target_birth_month=None):
        self.main_star = main_star
        self.main_birth_month = main_birth_month
        self.target_star = target_star
        self.target_birth_month = target_birth_month
        self.symbols_male = symbols_male
        self.symbols_female = symbols_female

    def to_dict(self):
        return {
            'id': self.id,
            'main_star': self.main_star,
            'main_birth_month': self.main_birth_month,
            'target_star': self.target_star,
            'target_birth_month': self.target_birth_month,
            'symbols_male': self.symbols_male,
            'symbols_female': self.symbols_female,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def get_compatibility_symbols(cls, main_star, target_star, main_birth_month, target_birth_month, is_male=True):
        """
        主星と対象星の本命星と生年月からシンボルを取得する
        
        Args:
            main_star (int): 主星の本命星番号
            target_star (int): 対象星の本命星番号
            main_birth_month (int): 主星の持ち主の生まれ月
            target_birth_month (int): 対象星の持ち主の生まれ月
            is_male (bool, optional): 主星の持ち主が男性かどうか (Trueなら男性視点、Falseなら女性視点)
            
        Returns:
            str: 相性記号 (★,○,P,F,N,▲ など)
        """
        try:
            # 完全一致の相性データを検索
            compatibility = cls.query.filter_by(
                main_star=main_star,
                target_star=target_star,
                main_birth_month=main_birth_month,
                target_birth_month=target_birth_month
            ).first()
            
            if compatibility:
                return compatibility.symbols_male if is_male else compatibility.symbols_female
            
            # 完全一致するデータがない場合はデフォルトデータを検索
            default_compatibility = cls.query.filter_by(
                main_star=main_star,
                target_star=target_star,
                main_birth_month=None,
                target_birth_month=None
            ).first()
            
            if default_compatibility:
                return default_compatibility.symbols_male if is_male else default_compatibility.symbols_female
            
            # 見つからない場合
            logger.warning(f"相性データが見つかりません: main_star={main_star}, target_star={target_star}, "
                          f"main_birth_month={main_birth_month}, target_birth_month={target_birth_month}")
            return ""
            
        except Exception as e:
            logger.error(f"相性データ取得中にエラーが発生しました: {str(e)}")
            return "" 