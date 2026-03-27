import psycopg2 # Importa motor de base de datos PostgreSQL
import os # Importa utilidades del sistema de archivos

def get_connection(): # Funcion para obtener conexion
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "auth_db"),
        user=os.getenv("DB_USER", "penguin"),
        password=os.getenv("DB_PASS", "secreto")
    )

def init_db(): # Funcion para inicializar la base de datos de autenticacion
    try:
        connection = get_connection() # Abre la conexion a Postgres
        cursor = connection.cursor() # Crea el cursor para ejecutar sentencias SQL
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''') # Crea tabla de usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, username TEXT)''') # Crea tabla de tokens
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'secreto123') ON CONFLICT (username) DO NOTHING") # Crea el administrador inicial
        connection.commit() # Guarda las tablas y el admin en el disco
        connection.close() # Cierra la conexion para liberar recursos
    except Exception as e:
        print(f"Error inicializando la DB auth: {e}")

if __name__ == '__main__': # Comprueba si el script se ejecuta directamente
    init_db() # Lanza la creacion de la base de datos
