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

@circuit_breaker(maximos_fallos=3, ventana_temporal=10) # Decorador para aplicar proteccion de circuito
@retry(max_reintentos=3, retraso=1) # Decorador para aplicar reintentos automaticos
def verificar_token_con_auth(auth_header):
    return requests.get(AUTH_URL, headers={"Authorization": auth_header}, timeout=3)

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify")

@app.route('/stations', methods=['GET'])
def get_stations():
    # Validar token llamando al microservicio de auth con resiliencia
    auth_header = request.headers.get("Authorization", "")
    try:
        res = verificar_token_con_auth(auth_header)
        if res.status_code != 200:
            return jsonify({"status": 401, "message": "No autorizado"}), 401
    except CircuitBreakerOpenException as cbe:
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(cbe)}"}), 503
    except requests.exceptions.RequestException:
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500
        
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre FROM stations")
    stations = [{"id": row[0], "nombre": row[1]} for row in c.fetchall()]
    conn.close()
    
    return jsonify({"status": 200, "data": stations}), 200

@app.route('/stations/<int:id_mesa>', methods=['PUT'])
def actualizar_nombre_mesa(id_mesa):
    # 1. Validar que el usuario tiene permisos (Verificamos su Token)
    token_autorizacion = request.headers.get("Authorization", "")
    try:
        respuesta_auth = verificar_token_con_auth(token_autorizacion)
        if respuesta_auth.status_code != 200:
            return jsonify({"status": 401, "message": "No tienes permiso para editar mesas"}), 401
    except Exception as error_autorizacion:
        return jsonify({"status": 500, "message": f"Error validando la sesión: {error_autorizacion}"}), 500

    # 2. Leer el nuevo nombre que nos mandan
    datos_recibidos = request.json or {}
    nuevo_nombre = datos_recibidos.get("nombre")
    
    if not nuevo_nombre:
        return jsonify({"status": 400, "message": "Debes especificar el campo 'nombre'"}), 400

    # 3. Guardar el nuevo nombre en la Base de Datos
    conexion = sqlite3.connect(database.DB_PATH)
    cursor = conexion.cursor()
    
    # IMPORTANTE: Usamos '?' para evitar inyección SQL (Seguridad)
    cursor.execute("UPDATE stations SET nombre = ? WHERE id = ?", (nuevo_nombre, id_mesa))
    
    # 4. Confirmar si la mesa que pidieron realmente existía
    if cursor.rowcount == 0:
        conexion.close()
        return jsonify({"status": 404, "message": f"La mesa {id_mesa} no existe"}), 404
        
    conexion.commit() # Guardamos los cambios
    conexion.close()
    
    return jsonify({"status": 200, "message": f"Mesa {id_mesa} ha sido renombrada a '{nuevo_nombre}'"}), 200

if __name__ == '__main__':
    database.init_db()
    # Usamos el puerto 5002 para Station Service
    port = int(os.getenv("STATION_SERVICE_PORT", 5002))
    app.run(host='0.0.0.0', port=port)
