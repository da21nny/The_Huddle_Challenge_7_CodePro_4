import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'station.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations (id INTEGER PRIMARY KEY, nombre TEXT)''')
    # Insertar mesas iniciales si no existen
    c.execute("SELECT COUNT(*) FROM stations")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO stations (id, nombre) VALUES (1, 'Mesa 1')")
        c.execute("INSERT INTO stations (id, nombre) VALUES (2, 'Mesa 2')")
        c.execute("INSERT INTO stations (id, nombre) VALUES (3, 'Mesa 3')")
        conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
