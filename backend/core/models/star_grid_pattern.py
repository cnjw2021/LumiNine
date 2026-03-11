from datetime import datetime
from sqlalchemy.orm import relationship
from core.database import db


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

