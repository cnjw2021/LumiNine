"""九星のグループマスタデータを管理するモデル"""

from datetime import datetime
from core.database import db
from core.utils.logger import get_logger

logger = get_logger(__name__)

class StarGroups(db.Model):
    """九星のグループマスタデータ
    グループ1: 一白・四緑・七赤
    グループ2: 二黒・五黄・八白
    グループ3: 三碧・六白・九紫
    """
    __tablename__ = 'star_groups'

    star_number = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    name_jp = db.Column(db.String(50), nullable=False, comment='日本語名称')
    name_kanji = db.Column(db.String(50), nullable=True, comment='漢字表記')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, star_number, group_id, name_jp, name_kanji=None):
        self.star_number = star_number
        self.group_id = group_id
        self.name_jp = name_jp
        self.name_kanji = name_kanji

    def to_dict(self):
        """辞書形式に変換するメソッド"""
        return {
            'star_number': self.star_number,
            'group_id': self.group_id,
            'name_jp': self.name_jp,
            'name_kanji': self.name_kanji
        }

    @classmethod
    def get_group_for_star(cls, star_number):
        """星番号からグループIDを取得するメソッド"""
        star_group = cls.query.filter_by(star_number=star_number).first()
        if star_group:
            return star_group.group_id
        else:
            # 数学的な計算でグループIDを求める（フォールバック）
            # 1,4,7はグループ1、2,5,8はグループ2、3,6,9はグループ3
            group_id = star_number % 3
            if group_id == 0:
                group_id = 3
            return group_id

# StarGroupクラスは互換性維持のための別名定義
StarGroup = StarGroups
