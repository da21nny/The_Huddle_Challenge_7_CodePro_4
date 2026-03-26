import sqlite3 # Importa el modulo de base de datos SQL
import os # Importa el modulo de acceso a archivos del sistema

RUTA_DB = os.path.join(os.path.dirname(__file__), 'reservation.db') # Establece la ruta del archivo reservation.db
DB_PATH = RUTA_DB # Compatible con los archivos que importan DB_PATH

def init_db(): # Funcion para generar la base de datos de reservas
    conexion = sqlite3.connect(RUTA_DB) # Abre la conexion con la base de datos
    cursor = conexion.cursor() # Crea el cursor de ejecucion de sentencias
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    hora TEXT,
                    mesa_id INTEGER,
                    username TEXT,
                    UNIQUE(fecha, hora, mesa_id)
                )''') # Crea tabla de reservas con clave unica combinada
    conexion.commit() # Guarda la creacion de la tabla en disco
    conexion.close() # Finaliza la sesion de base de datos

if __name__ == '__main__': # Comprueba la ejecucion individual del script
    init_db() # Crea las tablas de reservas por primera vez
