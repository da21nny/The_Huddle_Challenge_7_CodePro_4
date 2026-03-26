from flask import Flask, request, jsonify
import sqlite3
import requests
import database
import os
import sys

# Permitimos importar desde utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.retry import retry
from utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException

app = Flask(__name__)

@circuit_breaker(maximos_fallos=3, ventana_temporal=10) # Aplica proteccion de circuito con parametros en español
@retry(max_reintentos=3, retraso=1) # Aplica reintentos automaticos con parametros en español
def verificar_token_con_auth(auth_header):
    return requests.get(AUTH_URL, headers={"Authorization": auth_header}, timeout=3)

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify")

@app.route('/reservations', methods=['POST', 'GET'])
def reservations():
    # Validar token llamando al microservicio de auth con resiliencia
    auth_header = request.headers.get("Authorization", "")
    try:
        res = verificar_token_con_auth(auth_header)
        if res.status_code != 200:
            return jsonify({"status": 401, "message": "No autorizado"}), 401
        username = res.json().get("username")
    except CircuitBreakerOpenException as cbe:
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(cbe)}"}), 503
    except requests.exceptions.RequestException:
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500
        
    conn = sqlite3.connect(database.DB_PATH)
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

@app.route('/reservations/<int:id_reserva>', methods=['DELETE'])
def eliminar_reserva(id_reserva):
    # 1. Validar Token (Nadie borra si no está autenticado)
    token_autorizacion = request.headers.get("Authorization", "")
    try:
        respuesta_auth = verificar_token_con_auth(token_autorizacion)
        if respuesta_auth.status_code != 200:
            return jsonify({"status": 401, "message": "Prohibido. No tienes permiso para borrar."}), 401
    except Exception as error_red:
        return jsonify({"status": 500, "message": f"Servicio Auth no responde: {error_red}"}), 500

    # 2. Conectar a la base de datos y borrar
    conexion = sqlite3.connect(database.DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = ?", (id_reserva,))
    
    # 3. Si no se borró nada (rowcount = 0), es porque no existía ese ID
    if cursor.rowcount == 0:
        conexion.close()
        return jsonify({"status": 404, "message": f"La reserva {id_reserva} no existe o ya fue borrada"}), 404
        
    conexion.commit()
    conexion.close()
    
    return jsonify({"status": 200, "message": f"Reserva {id_reserva} eliminada con éxito"}), 200

if __name__ == '__main__':
    database.init_db()
    # Usamos el puerto 5003 para Reservation Service
    port = int(os.getenv("RESERVATION_SERVICE_PORT", 5003))
    app.run(host='0.0.0.0', port=port)
