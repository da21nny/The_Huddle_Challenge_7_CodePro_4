import psycopg2 # Importa motor de base de datos PostgreSQL
import os # Importa el modulo de acceso a archivos del sistema

def get_connection(): # Funcion para generar la base de datos de reservas
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "reservation_db"),
        user=os.getenv("DB_USER", "penguin"),
        password=os.getenv("DB_PASS", "secreto")
    )

def init_db(): # Funcion para generar la base de datos de reservas
    try:
        connection = get_connection() # Abre la conexion con la base de datos
        cursor = connection.cursor() # Crea el cursor de ejecucion de sentencias
        cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
                        id SERIAL PRIMARY KEY,
                        fecha TEXT,
                        hora TEXT,
                        mesa_id INTEGER,
                        username TEXT,
                        UNIQUE(fecha, hora, mesa_id)
                    )''') # Crea tabla de reservas con clave unica combinada
        connection.commit() # Guarda la creacion de la tabla en disco
        connection.close() # Finaliza la sesion de base de datos
    except Exception as e:
        print(f"Error inicializando la DB reservation: {e}")

if __name__ == '__main__': # Comprueba la ejecucion individual del script
    init_db() # Crea las tablas de reservas por primera vez
