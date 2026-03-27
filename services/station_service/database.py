import psycopg2 # Importa motor de base de datos PostgreSQL
import os # Importa acceso al sistema operativo

def get_connection(): # Funcion para crear la base de datos de estaciones
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "station_db"),
        user=os.getenv("DB_USER", "penguin"),
        password=os.getenv("DB_PASS", "secreto")
    )

def init_db(): # Funcion para crear la base de datos de estaciones
    try:
        conexion = get_connection() # Conecta con el archivo de estaciones
        cursor = conexion.cursor() # Crea el gestor de ejecucion SQL
        cursor.execute('''CREATE TABLE IF NOT EXISTS stations (id SERIAL PRIMARY KEY, nombre TEXT)''') # Crea tabla de mesas
        cursor.execute("SELECT COUNT(*) FROM stations") # Busca si ya hay mesas registradas
        if cursor.fetchone()[0] == 0: # Si la base de datos esta vacia
            cursor.execute("INSERT INTO stations (id, nombre) VALUES (1, 'Mesa 1')") # Crea la mesa numero uno
            cursor.execute("INSERT INTO stations (id, nombre) VALUES (2, 'Mesa 2')") # Crea la mesa numero dos
            cursor.execute("INSERT INTO stations (id, nombre) VALUES (3, 'Mesa 3')") # Crea la mesa numero tres
            conexion.commit() # Guarda las mesas iniciales permanentemente
        conexion.close() # Finaliza el acceso a la base de datos
    except Exception as e:
        print(f"Error inicializando la DB station: {e}")

if __name__ == '__main__': # Comprueba si se ejecuta el script directamente
    init_db() # Lanza la creacion de la base de datos
