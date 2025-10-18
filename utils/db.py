from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
load_dotenv()
class Database:
    def __init__(self):
        self.connection_string = os.getenv(
            "NEON_CONNECTION_STRING",
            "postgresql://api_user:your_password@ep-quiet-pond-123456.us-east-2.aws.neon.tech/fundacion_amigos_ninos?sslmode=require"
        )
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=self.connection_string,
            cursor_factory=RealDictCursor
        )

    def get_connection(self):
        return self.pool.getconn()

    def release_connection(self, conn):
        self.pool.putconn(conn)

    def close_all(self):
        self.pool.closeall()

db = Database()