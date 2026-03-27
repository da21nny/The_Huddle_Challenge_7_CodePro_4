from flask import Flask, request, jsonify # Importa componentes de Flask para la API
import psycopg2 # Importa libreria para manejo de Base de Datos
import requests # Importa libreria para realizar peticiones HTTP
import database # Importa archivo local de configuracion de DB
import os # Importa utilidades para variables de entorno
import sys # Importa sistema para gestion de rutas de importacion

# Se agrega la ruta del directorio padre para acceder a utilidades comunes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Configura el path de busqueda
from utils.retry import retry # Importa decorador para reintentar fallos
from utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException # Importa patron de resiliencia

app = Flask(__name__) # Crea la aplicacion de microservicio de reservas

@circuit_breaker(maximos_fallos=3, ventana_temporal=10) # Protege contra caidas del servicio de auth
@retry(max_reintentos=3, retraso=1) # Reintenta si hay micro-cortes en la red
def verify_token_with_auth(auth_header): # Funcion que delega la validacion al servicio experto
    return requests.get(AUTH_URL, headers={"Authorization": auth_header}, timeout=3) # Llama al endpoint de verificacion

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify") # Carga direccion del servicio auth

@app.route('/reservations', methods=['POST', 'GET']) # Define ruta para crear y listar reservas
def reservations(): # Manejador principal de reservas
    auth_header = request.headers.get("Authorization", "") # Obtiene el token de seguridad
    try: # Inicia validacion del usuario via red
        server_response = verify_token_with_auth(auth_header) # Consulta al servicio de identidad
        if server_response.status_code != 200: # Si el token es invalido
            return jsonify({"status": 401, "message": "No autorizado"}), 401 # Bloquea el acceso a la reserva
        username = server_response.json().get("username") # Obtiene el nombre del pinguino autenticado
    except CircuitBreakerOpenException as cb_error: # Captura si el circuito esta previniendo llamadas
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(cb_error)}"}), 503 # Indica servicio saturado
    except requests.exceptions.RequestException: # Captura fallos de comunicacion fisica
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Error de infraestructura
        
    db_connection = database.get_connection() # Conecta a la base de datos de reservas
    db_cursor = db_connection.cursor() # Crea el cursor de comandos SQL
    
    if request.method == 'POST': # Lógica para guardar una nueva reserva
        json_body = request.json or {} # Parsea el cuerpo del mensaje
        reservation_date = json_body.get("fecha") # Captura el dia elegido
        reservation_time = json_body.get("hora") # Captura el horario elegido
        station_id = json_body.get("mesa_id") # Captura el identificador de la mesa
        
        if not reservation_date or not reservation_time or not station_id: # Valida integridad de los datos
            return jsonify({"status": 400, "message": "Faltan datos (fecha, hora o mesa_id)"}), 400 # Informa omision de datos
            
        try: # Intenta insertar la reserva en la tabla
            db_cursor.execute("INSERT INTO reservations (fecha, hora, mesa_id, username) VALUES (%s, %s, %s, %s)",
                      (reservation_date, reservation_time, station_id, username)) # Realiza insercion protegida
            db_connection.commit() # Guarda la reserva en el disco
            db_connection.close() # Libera el archivo de base de datos
            return jsonify({"status": 201, "message": "Reserva creada exitosamente."}), 201 # Confirma registro exitoso
        except psycopg2.IntegrityError: # Controla si la mesa ya esta ocupada
            db_connection.close() # Libera la conexion antes de salir
            return jsonify({"status": 409, "message": "Conflicto: La mesa ya está reservada en esa fecha y hora."}), 409 # Informa colision

    elif request.method == 'GET': # Lógica para mostrar todas las reservas existentes
        db_cursor.execute("SELECT fecha, hora, mesa_id, username FROM reservations") # Consulta todos los registros
        found_rows = db_cursor.fetchall() # Recupera la informacion de la DB
        reservations_list = [{"fecha": row[0], "hora": row[1], "mesa_id": row[2], "usuario": row[3]} for row in found_rows] # Mapea a dicts
        db_connection.close() # Cierra la conexion a la DB
        return jsonify({"status": 200, "data": reservations_list}), 200 # Envía la lista completa de reservas

@app.route('/reservations/<int:reservation_id>', methods=['DELETE']) # Define ruta para cancelacion de reservas
def delete_reservation(reservation_id): # Funcion para eliminar una reserva por su ID
    deletion_token = request.headers.get("Authorization", "") # Identifica al solicitante del borrado
    try: # Valida que el solicitante sea un usuario real
        auth_response = verify_token_with_auth(deletion_token) # Pide confirmacion al servicio Auth
        if auth_response.status_code != 200: # Si la identidad no es valida
            return jsonify({"status": 401, "message": "Prohibido. No tienes permiso para borrar."}), 401 # Deniega el borrado
    except CircuitBreakerOpenException as cb_error: # Controla disponibilidad del sistema de seguridad
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(cb_error)}"}), 503 # Informa servicio ocupado
    except requests.exceptions.RequestException: # Controla fallos de enlace de red
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Informa fallo de red

    db_connection = database.get_connection() # Abre conexion a la DB de reservas
    db_cursor = db_connection.cursor() # Inicia el cursor para borrar
    db_cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,)) # Intenta ejecutar el borrado fisico
    
    if db_cursor.rowcount == 0: # Comprueba si realmente se borro algo
        db_connection.close() # Cierra la conexion si no hubo accion
        return jsonify({"status": 404, "message": f"La reserva {reservation_id} no existe o ya fue borrada"}), 404 # Informa ID invalido
        
    db_connection.commit() # Confirma el borrado permanentemente
    db_connection.close() # Finaliza el acceso a la DB
    
    return jsonify({"status": 200, "message": f"Reserva {reservation_id} eliminada con éxito"}), 200 # Confirma eliminacion

if __name__ == '__main__': # Verifica si el script corre individualmente
    database.init_db() # Crea el esquema de reservas si es necesario
    run_port = int(os.getenv("RESERVATION_SERVICE_PORT", 5003)) # Lee puerto del entorno
    app.run(host='0.0.0.0', port=run_port) # Inicia el servidor de reservas
