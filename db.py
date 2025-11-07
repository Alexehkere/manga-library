import psycopg2
from psycopg2 import extras

# Configuration (Move these here)
DB_HOST = '10.30.0.137'
DB_USER = 'gr622_naadm'
DB_PASSWORD = 'AnnaTorgashova0803'
DB_NAME = 'gr622_naadm'
DB_PORT = 5432

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.cursor_factory = extras.DictCursor
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None
