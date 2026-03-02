from datetime import datetime, date, time
from typing import Dict, Any, Optional, Tuple, List

from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, Date, Time

from core.database import db
from core.utils.logger import get_logger
from core.config import get_config

logger = get_logger(__name__)
metadata = MetaData()

# テーブル定義
stellar_cycles = Table(
    'stellar_cycles',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('year', Integer, nullable=False, unique=True),
    Column('first_ascending_phase_date', Date, nullable=True, comment='初回目陽遁開始日'),
    Column('first_ascending_phase_time', Time, nullable=True, comment='初回目陽遁開始時刻'),
    Column('first_descending_phase_date', Date, nullable=False, comment='初回目陰遁開始日'),
    Column('first_descending_phase_time', Time, nullable=False, default='00:00:00', comment='初回目陰遁開始時刻'),
    Column('second_ascending_phase_date', Date, nullable=True, comment='二回目陽遁開始日'),
    Column('second_ascending_phase_time', Time, nullable=True, comment='二回目陽遁開始時刻'),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now)
)

class StellarCycle:
    """九星気学の周期情報（陰遁・陽遁）を扱うクラス"""

    @staticmethod
    async def get_by_year(year: int) -> Optional[Dict[str, Any]]:
        """指定した年の九星気学周期情報（陰遁・陽遁の開始日）を取得する

        Args:
            year (int): 取得対象の年

        Returns:
            Optional[Dict[str, Any]]: 九星気学周期情報。存在しない場合はNone
        """
        query = stellar_cycles.select().where(stellar_cycles.c.year == year)
        result = await db.session.execute(query)
        return result.fetchone()

    @staticmethod
    async def get_all() -> List[Dict[str, Any]]:
        """すべての九星気学周期情報（陰遁・陽遁の開始日）を取得する

        Returns:
            List[Dict[str, Any]]: 九星気学周期情報のリスト
        """
        query = stellar_cycles.select().order_by(stellar_cycles.c.year)
        results = await db.session.execute(query)
        return results.fetchall()

    @staticmethod
    async def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """九星気学周期情報（陰遁・陽遁の開始日）を新規作成する

        Args:
            data (Dict[str, Any]): 作成する九星気学周期情報（陰遁・陽遁の開始日時）

        Returns:
            Dict[str, Any]: 作成された九星気学周期情報
        """
        values = {k: v for k, v in data.items() if k != 'id'}
        query = stellar_cycles.insert().values(**values)
        result = await db.session.execute(query)
        await db.session.commit()
        data['id'] = result.inserted_primary_key[0]
        return data

    @staticmethod
    async def update(data: Dict[str, Any]) -> Dict[str, Any]:
        """九星気学周期情報（陰遁・陽遁の開始日）を更新する

        Args:
            data (Dict[str, Any]): 更新する九星気学周期情報

        Returns:
            Dict[str, Any]: 更新された九星気学周期情報
        """
        if 'id' not in data:
            # IDがない場合は年で検索
            existing = await StellarCycle.get_by_year(data['year'])
            if existing:
                data['id'] = existing['id']

        values = {k: v for k, v in data.items() if k != 'id'}
        if 'id' in data:
            # 既存レコードの更新
            query = stellar_cycles.update().where(
                stellar_cycles.c.id == data['id']
            ).values(**values)
            await db.session.execute(query)
            await db.session.commit()
        else:
            # 新規作成
            data = await StellarCycle.create(data)
        
        return data

    @staticmethod
    async def batch_insert(records: List[Dict[str, Any]]) -> None:
        """九星気学周期情報（陰遁・陽遁の開始日）を一括登録する

        Args:
            records (List[Dict[str, Any]]): 九星気学周期情報のリスト
        """
        if not records:
            return

        values_list = []
        for record in records:
            values = {k: v for k, v in record.items() if k != 'id'}
            values_list.append(values)

        query = stellar_cycles.insert().values(values_list)
        await db.session.execute(query)
        await db.session.commit()

    @staticmethod
    async def upsert(data: Dict[str, Any]) -> Dict[str, Any]:
        """九星気学周期情報（陰遁・陽遁の開始日）を更新または挿入する

        Args:
            data (Dict[str, Any]): 更新または挿入する九星気学周期情報

        Returns:
            Dict[str, Any]: 更新または挿入された九星気学周期情報
        """
        existing = await StellarCycle.get_by_year(data['year'])
        if existing:
            data['id'] = existing['id']
            return await StellarCycle.update(data)
        else:
            return await StellarCycle.create(data)

    @staticmethod
    async def delete_by_year(year: int) -> bool:
        """指定した年の九星気学周期情報（陰遁・陽遁の開始日）を削除する

        Args:
            year (int): 削除対象の年

        Returns:
            bool: 削除に成功した場合はTrue、対象が存在しなかった場合はFalse
        """
        query = stellar_cycles.delete().where(stellar_cycles.c.year == year)
        result = await db.session.execute(query)
        await db.session.commit()
        return result.rowcount > 0
    
    @staticmethod
    def get_cycle_by_year_sync(year: int) -> Optional[Dict[str, Any]]:
        """同期的に指定した年の陽遁・陰遁周期を取得する

        Args:
            year (int): 取得対象の年

        Returns:
            Optional[Dict[str, Any]]: 九星気学周期情報。存在しない場合はNone
        """
        from sqlalchemy import create_engine, text
        
        config = get_config()
        database_url = config.SQLALCHEMY_DATABASE_URI
        
        engine = create_engine(database_url)
        with engine.connect() as connection:
            query = f"SELECT * FROM stellar_cycles WHERE year = {year}"
            result = connection.execute(text(query))
            row = result.fetchone()
            if row:
                # カラム名を明示して値を取得
                # SQLAlchemyの結果オブジェクトからマッピングをきちんと取得
                row_dict = dict(row._mapping)
                
                # 日付データの取得
                first_ascending_date = row_dict.get('first_ascending_phase_date')
                first_ascending_time = row_dict.get('first_ascending_phase_time')
                first_descending_date = row_dict.get('first_descending_phase_date')
                first_descending_time = row_dict.get('first_descending_phase_time')
                second_ascending_date = row_dict.get('second_ascending_phase_date')
                second_ascending_time = row_dict.get('second_ascending_phase_time')
                
                # 実際に使用する陽遁・陰遁日時を決定
                # 基本的に、二回目の陽遁日が設定されている場合はそれを使用
                ascending_phase_date = second_ascending_date if second_ascending_date else first_ascending_date
                ascending_phase_time = second_ascending_time if second_ascending_time else first_ascending_time
                
                # 互換性のため、古い名前のキーも保持
                return {
                    'id': row_dict['id'],
                    'year': row_dict['year'],
                    # 新しいカラム
                    'first_ascending_phase_date': first_ascending_date,
                    'first_ascending_phase_time': first_ascending_time, 
                    'first_descending_phase_date': first_descending_date,
                    'first_descending_phase_time': first_descending_time,
                    'second_ascending_phase_date': second_ascending_date,
                    'second_ascending_phase_time': second_ascending_time,
                    # 互換性のため、古い名前のキーも保持
                    'ascending_phase_date': ascending_phase_date,
                    'ascending_phase_time': ascending_phase_time,
                    'descending_phase_date': first_descending_date,  # 初回陰遁日を使用
                    'descending_phase_time': first_descending_time,
                    'created_at': row_dict['created_at'],
                    'updated_at': row_dict['updated_at']
                }
            return None
            