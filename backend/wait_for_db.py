import sys
import time
import os

def check_postgres_connection():
    """PostgreSQL 연결 확인 (로컬 개발환경 전용)"""
    try:
        import psycopg2
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url:
            conn = psycopg2.connect(db_url, connect_timeout=10)
            conn.close()
            return True
        # 개별 환경변수 폴백
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'postgres'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            dbname=os.environ.get('DB_NAME'),
            port=int(os.environ.get('DB_PORT', 5432)),
            connect_timeout=10
        )
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        return False

if __name__ == "__main__":
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts} to connect to PostgreSQL...")
        if check_postgres_connection():
            print("PostgreSQL is ready!")
            sys.exit(0)
        if attempt < max_attempts:
            print("Waiting 2 seconds before next attempt...")
            time.sleep(2)
    print("Failed to connect to PostgreSQL after maximum attempts")
    sys.exit(1)