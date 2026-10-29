import psycopg2
from psycopg2.extras import RealDictCursor

# Configurações de acesso ao seu PostgreSQL Local
DB_HOST = "localhost"
DB_NAME = "lol_client_db"
DB_USER = "postgres"
DB_PASS = "Naruto2709" # ⚠️ COLOQUE AQUI A SENHA MASTER QUE VOCE CRIOU NO POSTGRESQL !
DB_PORT = "5432"

def get_db_connection():
    """Abre uma nova conexão limpa com o PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            cursor_factory=RealDictCursor # Faz o SQL retornar dados em formado
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no banco de dados: {e}")