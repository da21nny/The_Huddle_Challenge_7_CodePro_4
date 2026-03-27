from flask import Flask, request, jsonify # Importa componentes de Flask para la API
import psycopg2 # Importa libreria de base de datos
import requests # Importa libreria HTTP
import jwt # Importa libreria JWT para validacion local rapida
import database # Importa configuracion de DB local
import os # Importa utilidades de variables de entorno
import sys # Importa utilidades de ruta del sistema

SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_penguin_key") # Define clave secreta JWT compartida
STATIONS_URL = os.getenv("STATIONS_URL", "http://127.0.0.1:5002/stations") # Define URL del servicio de mesas

# Se agrega la ruta del directorio padre para acceder a utilidades comunes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Configura el path de busqueda
from utils.retry import retry # Importa decorador para reintentar fallos
from utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException # Importa patron de resiliencia

app = Flask(__name__) # Crea la aplicacion de microservicio de reservas

def validate_jwt_local(auth_header): # Valida el JWT localmente sin sobrecarga de red
    token = auth_header.replace("Bearer ", "") # Extrae la cadena del token
    if not token: # Verifica si esta vacio
        return None # Devuelve fallo
    try: # Intenta decodificar
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) # Decodifica matematicamente
        return payload["username"] # Devuelve usuario valido
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError): # Captura errores de JWT
        return None # Devuelve fallo

@circuit_breaker(maximos_fallos=3, ventana_temporal=10) # Protege contra fallos en cascada
@retry(max_reintentos=3, retraso=1) # Reintenta la conexion si el servicio de mesas cae
def check_station_exists(station_id, auth_header): # Funcion para verificar si la mesa existe por red
    return requests.get(f"{STATIONS_URL}/{station_id}", headers={"Authorization": auth_header}, timeout=3) # Llama al servicio de mesas

@app.route('/reservations', methods=['POST', 'GET']) # Define ruta para crear y listar reservas
def reservations(): # Manejador principal de reservas
    auth_header = request.headers.get("Authorization", "") # Obtiene token de seguridad
    username = validate_jwt_local(auth_header) # Valida identidad del usuario localmente
    if not username: # Si el token es invalido
        return jsonify({"status": 401, "message": "Unauthorized"}), 401 # Deniega acceso a la reserva
        
    db_connection = database.get_connection() # Conecta a la base de datos de reservas
    db_cursor = db_connection.cursor() # Crea el cursor de comandos SQL
    
    if request.method == 'POST': # Lógica para guardar una nueva reserva
        json_body = request.json or {} # Parsea el cuerpo del mensaje
        reservation_date = json_body.get("fecha") # Captura el dia elegido
        reservation_time = json_body.get("hora") # Captura el horario elegido
        station_id = json_body.get("mesa_id") # Captura el identificador de la mesa
        
        if not reservation_date or not reservation_time or not station_id: # Valida integridad de los datos
            return jsonify({"status": 400, "message": "Missing reservation data"}), 400 # Informa campos no encontrados
            
        try: # Intenta llamada de red al servicio de mesas
            station_response = check_station_exists(station_id, auth_header) # Verifica si la mesa es real
            if station_response.status_code != 200: # Si la mesa no se encuentra
                return jsonify({"status": 404, "message": "Target station does not exist"}), 404 # Rechaza la reserva
        except CircuitBreakerOpenException as cb_error: # Captura si el servicio remoto esta sobrecargado
            return jsonify({"status": 503, "message": f"Station Service Unavailable: {str(cb_error)}"}), 503 # Informa saturacion del sistema
        except requests.exceptions.RequestException: # Captura fallos de red sin procesar
            return jsonify({"status": 500, "message": "Failed to communicate with Station Service"}), 500 # Informa caida de red
            
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
    auth_header = request.headers.get("Authorization", "") # Obtiene identidad del solicitante
    username = validate_jwt_local(auth_header) # Valida autorizacion localmente
    if not username: # Si la identidad es invalida
        return jsonify({"status": 401, "message": "Unauthorized to delete"}), 401 # Deniega accion

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
