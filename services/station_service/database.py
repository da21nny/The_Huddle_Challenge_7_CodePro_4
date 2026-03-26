import sqlite3 # Importa motor SQL para base de datos
import os # Importa acceso al sistema operativo

RUTA_DB = os.path.join(os.path.dirname(__file__), 'station.db') # Define la ruta del archivo station.db
DB_PATH = RUTA_DB # Compatible con los archivos que importan la ruta

def init_db(): # Funcion para crear la base de datos de estaciones
    conexion = sqlite3.connect(RUTA_DB) # Conecta con el archivo de estaciones
    cursor = conexion.cursor() # Crea el gestor de ejecucion SQL
    cursor.execute('''CREATE TABLE IF NOT EXISTS stations (id INTEGER PRIMARY KEY, nombre TEXT)''') # Crea tabla de mesas
    cursor.execute("SELECT COUNT(*) FROM stations") # Busca si ya hay mesas registradas
    if cursor.fetchone()[0] == 0: # Si la base de datos esta vacia
        cursor.execute("INSERT INTO stations (id, nombre) VALUES (1, 'Mesa 1')") # Crea la mesa numero uno
        cursor.execute("INSERT INTO stations (id, nombre) VALUES (2, 'Mesa 2')") # Crea la mesa numero dos
        cursor.execute("INSERT INTO stations (id, nombre) VALUES (3, 'Mesa 3')") # Crea la mesa numero tres
        conexion.commit() # Guarda las mesas iniciales permanentemente
    conexion.close() # Finaliza el acceso a la base de datos

if __name__ == '__main__': # Comprueba si se ejecuta el script directamente
    init_db() # Lanza la creacion de la base de datos
