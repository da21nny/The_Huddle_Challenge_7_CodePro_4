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
    import time
    intentos = 5
    while intentos > 0:
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
            print("📅 Base de datos Reservation inicializada con éxito.")
            return
        except Exception as e:
            intentos -= 1
            print(f"⏳ Esperando a la base de datos reservation... ({intentos} reintentos) - Error: {e}")
            time.sleep(3)
    print("❌ No se pudo conectar a la base de datos reservation después de varios intentos.")

if __name__ == '__main__': # Comprueba la ejecucion individual del script
    init_db() # Crea las tablas de reservas por primera vez
