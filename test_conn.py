import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'energia_xm',
    'user': 'admin',
    'password': 'dbprueba123'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("Conexión exitosa a la base de datos")
except Exception as e:
    print("Error de conexión:", e)