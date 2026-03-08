from flask import Flask, request, jsonify
import sqlite3
import requests
import database

app = Flask(__name__)

AUTH_URL = "http://127.0.0.1:5001/verify"

@app.route('/stations', methods=['GET'])
def get_stations():
    # Validar token llamando al microservicio de auth
    auth_header = request.headers.get("Authorization", "")
    try:
        res = requests.get(AUTH_URL, headers={"Authorization": auth_header})
        if res.status_code != 200:
            return jsonify({"status": 401, "message": "No autorizado"}), 401
    except requests.exceptions.ConnectionError:
        return jsonify({"status": 500, "message": "Auth service instance error"}), 500
        
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre FROM stations")
    stations = [{"id": row[0], "nombre": row[1]} for row in c.fetchall()]
    conn.close()
    
    return jsonify({"status": 200, "data": stations}), 200

if __name__ == '__main__':
    database.init_db()
    # Usamos el puerto 5002 para Station Service
    app.run(port=5002)
