"""csv seed data

Revision ID: 003
Revises: 002_seed_data
Create Date: 2026-03-10

CSV 마스터 데이터를 읽어와서 DB에 COPY 명령으로 삽입합니다.
이 마이그레이션은 Alembic 실행 시 자동으로 CSV 데이터를 채워 넣기 위해 사용됩니다.
"""
from alembic import op
import sqlalchemy as sa
import os
import sys

# revision identifiers
revision = '003_csv_seed_data'
down_revision = '002_seed_data'
branch_labels = None
depends_on = None

def _get_connection():
    """Alembic 1.x / 2.x 互換のコネクション取得"""
    try:
        return op.get_bind()  # Alembic 1.x
    except AttributeError:
        return op.get_context().connection  # Alembic 2.x

def upgrade():
    # scripts 패키지를 import하기 위해 경로 추가 (Alembic 실행 시를 위해)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    try:
        from scripts.csv_data_loader import load_multiple_csv_files
        
        # 기본 경로 외에 환경 변수 등으로 지정된 경로가 있을 수 있으므로 BASE_CSV_DIR을 덮어쓸 수 있도록 설정
        from scripts import csv_data_loader
        
        # CSV 파일이 위치한 디렉토리 찾기
        csv_candidates = [
            os.path.join(backend_dir, 'data', 'csv'),
            os.path.join(backend_dir, '..', 'data', 'csv'), # backend 하위가 아닐 경우
        ]
        
        valid_csv_dir = None
        for path in csv_candidates:
            if os.path.exists(path) and os.path.isdir(path):
                valid_csv_dir = path
                break
                
        if not valid_csv_dir:
            print(f"WARN: CSV directory not found. Searched: {csv_candidates} — skipping CSV seed")
            return
            
        # 임시로 BASE_CSV_DIR 변경 (scripts 에서 참조하기 때문)
        original_base_csv_dir = csv_data_loader.BASE_CSV_DIR
        csv_data_loader.BASE_CSV_DIR = valid_csv_dir

        csv_table_mapping = {
            'zodiac_groups.csv': 'zodiac_groups',
            'zodiac_group_members.csv': 'zodiac_group_members',
            'hourly_star_zodiacs.csv': 'hourly_star_zodiacs',
            'solar_terms_data.csv': 'solar_terms',
            'solar_starts_data.csv': 'solar_starts',
            'daily_astrology_data.csv': 'daily_astrology',
            'pattern_switch_dates.csv': 'pattern_switch_dates',
        }
        
        print(f"Loading CSV data from {valid_csv_dir}")
        
        # Alembic 연결 객체 획득
        connection = _get_connection()
        # SQLAlchemy Connection 객체에서 원시 DBAPI 커넥션 (psycopg2) 획득
        raw_connection = connection.connection
        
        # users 테이블은 002 에서 슈퍼유저를 만들었을 가능성이 높으므로 이 스크립트에서는 제외함.
        # 기존 로직과 동일하게 다수 파일 로드 (TRUNCATE 후 삽입)
        # 중요: csv_data_loader.load_multiple_csv_files는 작업 후 connection.close()를 
        # 호출하도록 하드코딩되어 있습니다. Alembic 공유 커넥션이 닫히면 안되므로 보호막(patch)을 씌웁니다.
        original_close = raw_connection.close
        raw_connection.close = lambda: None
        
        try:
            results = load_multiple_csv_files(
                raw_connection,
                csv_table_mapping,
                truncate_tables=True
            )
        finally:
            # 원래 close 메서드 복구
            raw_connection.close = original_close
        
        for table, count in results.items():
            print(f"Loaded {count} rows into {table}")
            
        # 원래 값으로 복원
        csv_data_loader.BASE_CSV_DIR = original_base_csv_dir
            
    except ImportError as e:
        print(f"WARN: Could not import csv_data_loader: {e} — skipping CSV seed")
    except Exception as e:
        print(f"ERROR: Failed to load CSV data: {e} — skipping CSV seed")
        # 실패하더라도 DB 마이그레이션이 완전히 실패하지 않도록 (필요한 경우 raise 해도 좋지만 멱등성 유지)
        pass

def downgrade():
    # 마이그레이션 다운그레이드시 데이터를 날리는 것은 위험하므로 생략
    pass
