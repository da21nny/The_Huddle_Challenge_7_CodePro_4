import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, username TEXT)''')
    # Crear usuario por defecto si no existe
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'secreto123')")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
