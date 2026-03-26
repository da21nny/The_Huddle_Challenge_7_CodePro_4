import sqlite3 # Importa motor de base de datos SQLite
import os # Importa utilidades del sistema de archivos

RUTA_DB = os.path.join(os.path.dirname(__file__), 'auth.db') # Define la ubicacion del archivo de base de datos
DB_PATH = RUTA_DB # Mantiene compatibilidad con otros archivos que importan DB_PATH

def init_db(): # Funcion para inicializar la base de datos de autenticacion
    conexion = sqlite3.connect(RUTA_DB) # Abre la conexion al archivo auth.db
    cursor = conexion.cursor() # Crea el cursor para ejecutar sentencias SQL
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''') # Crea tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, username TEXT)''') # Crea tabla de tokens
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'secreto123')") # Crea el administrador inicial
    conexion.commit() # Guarda las tablas y el admin en el disco
    conexion.close() # Cierra la conexion para liberar el archivo

if __name__ == '__main__': # Comprueba si el script se ejecuta directamente
    init_db() # Lanza la creacion de la base de datos
