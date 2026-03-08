from flask import Flask, request, jsonify
import sqlite3
import requests
import database

app = Flask(__name__)

AUTH_URL = "http://127.0.0.1:5001/verify"

@app.route('/reservations', methods=['POST', 'GET'])
def reservations():
    # Validar token llamando al microservicio de auth
    auth_header = request.headers.get("Authorization", "")
    try:
        res = requests.get(AUTH_URL, headers={"Authorization": auth_header})
        if res.status_code != 200:
            return jsonify({"status": 401, "message": "No autorizado"}), 401
        username = res.json().get("username")
    except requests.exceptions.ConnectionError:
        return jsonify({"status": 500, "message": "Auth service instance error"}), 500
        
    conn = sqlite3.connect('reservation.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json or {}
        fecha = data.get("fecha")
        hora = data.get("hora")
        mesa_id = data.get("mesa_id")
        
        if not fecha or not hora or not mesa_id:
            return jsonify({"status": 400, "message": "Faltan datos (fecha, hora o mesa_id)"}), 400
            
        try:
            c.execute("INSERT INTO reservations (fecha, hora, mesa_id, username) VALUES (?, ?, ?, ?)",
                      (fecha, hora, mesa_id, username))
            conn.commit()
            conn.close()
            return jsonify({"status": 201, "message": "Reserva creada exitosamente."}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"status": 409, "message": "Conflicto: La mesa ya está reservada en esa fecha y hora."}), 409

    elif request.method == 'GET':
        c.execute("SELECT fecha, hora, mesa_id, username FROM reservations")
        rows = c.fetchall()
        reservas = [{"fecha": r[0], "hora": r[1], "mesa_id": r[2], "usuario": r[3]} for r in rows]
        conn.close()
        return jsonify({"status": 200, "data": reservas}), 200

if __name__ == '__main__':
    database.init_db()
    # Usamos el puerto 5003 para Reservation Service
    app.run(port=5003)
