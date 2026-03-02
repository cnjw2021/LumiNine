import sys
import time
import os
import mysql.connector
from mysql.connector import Error

def check_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'mysql'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            port=os.environ.get('DB_PORT', 3306),
            connection_timeout=10
        )
        if connection.is_connected():
            connection.close()
            return True
        return False
    except Error as e:
        print(f"MySQL connection error: {e}")
        return False

if __name__ == "__main__":
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts} to connect to MySQL...")
        if check_mysql_connection():
            print("MySQL is ready!")
            sys.exit(0)
        if attempt < max_attempts:
            print("Waiting 2 seconds before next attempt...")
            time.sleep(2)
    print("Failed to connect to MySQL after maximum attempts")
    sys.exit(1)