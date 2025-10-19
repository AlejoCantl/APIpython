from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import psycopg2
import time

load_dotenv()

class Database:
    def __init__(self):
        self.connection_string = os.getenv(
            "NEON_CONNECTION_STRING",
            "postgresql://api_user:your_password@ep-quiet-pond-123456.us-east-2.aws.neon.tech/fundacion_amigos_ninos?sslmode=require"
        )
        self.pool = None
        self._initialize_pool()

    def _initialize_pool(self, retries=3, delay=2):
        """Inicializa el pool de conexiones con reintentos."""
        for attempt in range(retries):
            try:
                self.pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=self.connection_string,
                    cursor_factory=RealDictCursor
                )
                return
            except psycopg2.OperationalError as e:
                print(f"Error al inicializar el pool: {e}. Reintentando ({attempt + 1}/{retries})...")
                if attempt < retries - 1:
                    time.sleep(delay)
        raise Exception("No se pudo inicializar el pool de conexiones tras varios intentos.")

    def get_connection(self):
        """Obtiene una conexión válida del pool."""
        for _ in range(3):  # Reintentar hasta 3 veces
            try:
                conn = self.pool.getconn()
                # Verificar si la conexión está activa
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")  # Consulta simple para probar
                return conn
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                print(f"Error en la conexión: {e}. Reintentando...")
                self._reset_pool()
        raise Exception("No se pudo obtener una conexión válida tras varios intentos.")

    # ✅ AGREGAR CONTEXT MANAGER
    def get_connection_context(self):
        """Context manager que automáticamente devuelve la conexión al pool"""
        class ConnectionContext:
            def __init__(self, db):
                self.db = db
                self.conn = None
            
            def __enter__(self):
                self.conn = self.db.get_connection()
                return self.conn
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.conn:
                    self.db.release_connection(self.conn)
        
        return ConnectionContext(self)

    def release_connection(self, conn):
        """Devuelve la conexión al pool."""
        try:
            self.pool.putconn(conn)
        except psycopg2.InterfaceError:
            print("Conexión ya cerrada, ignorando devolución.")

    def _reset_pool(self):
        """Reinicia el pool de conexiones."""
        try:
            self.close_all()
            self._initialize_pool()
        except Exception as e:
            print(f"Error al reiniciar el pool: {e}")

    def close_all(self):
        """Cierra todas las conexiones del pool."""
        if self.pool:
            self.pool.closeall()

db = Database()