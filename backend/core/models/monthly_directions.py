"""月ごとの方位データモデル"""

from datetime import datetime
from core.database import db
from core.utils.logger import get_logger
from .star_groups import StarGroups

logger = get_logger(__name__)

class MonthlyDirections(db.Model):
    """月ごとの方位データモデル
    本命星のグループごとに月盤データを格納
    """
    __tablename__ = 'monthly_directions'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False, comment='本命星グループID（1-3）')
    month = db.Column(db.Integer, nullable=False, comment='月（1-12）')
    zodiac = db.Column(db.String(10), nullable=True, comment='干支（子、丑、寅...）')
    center_star = db.Column(db.Integer, nullable=False, comment='中央の星（1-9）')

    # 八方位の星 - SQLに合わせてnullable=Falseに修正
    north = db.Column(db.Integer, nullable=False, comment='北の星')
    northeast = db.Column(db.Integer, nullable=False, comment='北東の星')
    east = db.Column(db.Integer, nullable=False, comment='東の星')
    southeast = db.Column(db.Integer, nullable=False, comment='南東の星')
    south = db.Column(db.Integer, nullable=False, comment='南の星')
    southwest = db.Column(db.Integer, nullable=False, comment='南西の星')
    west = db.Column(db.Integer, nullable=False, comment='西の星')
    northwest = db.Column(db.Integer, nullable=False, comment='北西の星')

    # 方位の吉凶情報
    north_fortune = db.Column(db.String(50), nullable=True, comment='北の吉凶')
    northeast_fortune = db.Column(db.String(50), nullable=True, comment='北東の吉凶')
    east_fortune = db.Column(db.String(50), nullable=True, comment='東の吉凶')
    southeast_fortune = db.Column(db.String(50), nullable=True, comment='南東の吉凶')
    south_fortune = db.Column(db.String(50), nullable=True, comment='南の吉凶')
    southwest_fortune = db.Column(db.String(50), nullable=True, comment='南西の吉凶')
    west_fortune = db.Column(db.String(50), nullable=True, comment='西の吉凶')
    northwest_fortune = db.Column(db.String(50), nullable=True, comment='北西の吉凶')

    # 季節情報
    season_start = db.Column(db.String(50), nullable=True, comment='季節の始まり')
    season_end = db.Column(db.String(50), nullable=True, comment='季節の終わり')
    description = db.Column(db.Text, nullable=True, comment='月盤の説明')

    # タイムスタンプ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, group_id, month, center_star,
                 north, northeast, east, southeast, south, southwest, west, northwest,
                 north_fortune=None, northeast_fortune=None, east_fortune=None, southeast_fortune=None,
                 south_fortune=None, southwest_fortune=None, west_fortune=None, northwest_fortune=None,
                 season_start=None, season_end=None, description=None, zodiac=None):
        self.group_id = group_id
        self.month = month
        self.zodiac = zodiac
        self.center_star = center_star
        self.north = north
        self.northeast = northeast
        self.east = east
        self.southeast = southeast
        self.south = south
        self.southwest = southwest
        self.west = west
        self.northwest = northwest
        self.north_fortune = north_fortune
        self.northeast_fortune = northeast_fortune
        self.east_fortune = east_fortune
        self.southeast_fortune = southeast_fortune
        self.south_fortune = south_fortune
        self.southwest_fortune = southwest_fortune
        self.west_fortune = west_fortune
        self.northwest_fortune = northwest_fortune
        self.season_start = season_start
        self.season_end = season_end
        self.description = description

    def to_dict(self):
        """辞書形式に変換するメソッド"""
        return {
            'id': self.id,
            'group_id': self.group_id,
            'month': self.month,
            'zodiac': self.zodiac,
            'center_star': self.center_star,
            'directions': {
                'north': self.north,
                'northeast': self.northeast,
                'east': self.east,
                'southeast': self.southeast,
                'south': self.south,
                'southwest': self.southwest,
                'west': self.west,
                'northwest': self.northwest
            },
            'fortunes': {
                'north': self.north_fortune,
                'northeast': self.northeast_fortune,
                'east': self.east_fortune,
                'southeast': self.southeast_fortune,
                'south': self.south_fortune,
                'southwest': self.southwest_fortune,
                'west': self.west_fortune,
                'northwest': self.northwest_fortune
            },
            'season': {
                'start': self.season_start,
                'end': self.season_end,
                'description': self.description
            }
        }

    @classmethod
    def get_monthly_directions_by_star(cls, star_number, month):
        """特定の本命星と月の方位情報を取得"""
        group_id = StarGroups.get_group_for_star(star_number)

        if not group_id:
            logger.error(f"星番号 {star_number} に対応するグループデータが見つかりません")
            return None

        return cls.query.filter_by(group_id=group_id, month=month).first()

    @classmethod
    def get_all_month_directions_by_star(cls, target_year):
        """指定年の立春開始月の九星の中宮に対して、その年の12ヶ月分の九星盤を取得"""
        from core.models.solar_terms import SolarTerms

        # 立春のデータを取得
        spring_term = SolarTerms.get_by_year_and_name(target_year, '立春')

        if not spring_term:
            logger.error(f"年 {target_year} の立春データが見つかりません")
            return None

        # 立春の星番号を基準としたgroup_idを取得
        group_id = StarGroups.get_group_for_star(spring_term.star_number)

        if not group_id:
            logger.error(f"星番号 {spring_term.star_number} に対応するグループデータが見つかりません")
            return None

        return cls.query.filter_by(group_id=group_id).order_by(cls.month).all()

    @classmethod
    def get_monthly_directions_by_group(cls, group_id, month):
        """特定のグループと月の方位情報を取得"""
        return cls.query.filter_by(group_id=group_id, month=month).first()

    @classmethod
    def get_all_by_star(cls, star_number):
        """特定の本命星の全ての月の方位情報を取得"""
        group_id = StarGroups.get_group_for_star(star_number)

        if not group_id:
            logger.error(f"星番号 {star_number} に対応するグループデータが見つかりません")
            return []

        return cls.query.filter_by(group_id=group_id).order_by(cls.month).all()

    @classmethod
    def get_all_by_group(cls, group_id):
        """特定のグループの全ての月の方位情報を取得"""
        return cls.query.filter_by(group_id=group_id).order_by(cls.month).all()
