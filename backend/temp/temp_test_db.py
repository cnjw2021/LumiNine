from flask import Flask
from core.database import init_db, db
from core.config import get_config
from sqlalchemy import inspect

app = Flask(__name__)
app.config.from_object(get_config())
init_db(app)

def test_db_connection():
    try:
        with app.app_context():
            # データベース接続テスト
            db.engine.connect()
            print("データベース接続テスト: 成功")
            
            # テーブル一覧を取得
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("データベースのテーブル一覧:")
            for table in tables:
                print(f"- {table}")
                
            # メタデータのテーブル一覧
            print("\nSQLAlchemyメタデータのテーブル一覧:")
            for table_name in db.metadata.tables.keys():
                print(f"- {table_name}")
            
    except Exception as e:
        print("データベース接続テスト: 失敗")
        print(f"エラー: {e}")

if __name__ == "__main__":
    test_db_connection() 