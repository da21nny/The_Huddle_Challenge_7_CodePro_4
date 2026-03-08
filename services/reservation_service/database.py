import sqlite3

def init_db():
    conn = sqlite3.connect('reservation.db')
    c = conn.cursor()
    # Unique asegura que no haya mas de 1 reserva en misma fecha, hora y mesa
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    hora TEXT,
                    mesa_id INTEGER,
                    username TEXT,
                    UNIQUE(fecha, hora, mesa_id)
                )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
