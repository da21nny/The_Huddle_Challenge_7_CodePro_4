from flask import Flask, request, jsonify # Importa componentes para el servidor web
import psycopg2 # Importa libreria de base de datos local
import requests # Importa libreria para HTTP externo
import jwt # Importa libreria JWT para validacion local
import database # Importa configuracion de DB
import os # Importa configuracion de variables de entorno
import sys # Importa herramientas de ruta del sistema

SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_penguin_key") # Establece clave secreta compartida

# Configuracion de ruta para poder importar utilidades compartidas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Añade el directorio padre al path
from utils.retry import retry # Importa el decorador de reintentos
from utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException # Importa el circuit breaker

app = Flask(__name__) # Crea la instancia de la aplicacion Flask

def validate_jwt_local(auth_header): # Valida el JWT matematicamente
    token = auth_header.replace("Bearer ", "") # Extrae la cadena
    if not token: # Verifica si esta vacio
        return None # Devuelve None si falla
    try: # Inicia bloque de decodificacion
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) # Analiza la firma
        return payload["username"] # Devuelve usuario valido
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError): # Captura tokens malos
        return None # Devuelve None en caso de fallo

@app.route('/stations', methods=['GET']) # Define el endpoint para listar mesas
def get_stations(): # Funcion que maneja la obtencion de estaciones
    auth_header = request.headers.get("Authorization", "") # Obtiene encabezado Auth
    username = validate_jwt_local(auth_header) # Valida cadena JWT
    if not username: # Verifica resultado de validacion
        return jsonify({"status": 401, "message": "Unauthorized"}), 401 # Rechaza si es invalido
        
    db_connection = database.get_connection() # Abre la base de datos de estaciones
    db_cursor = db_connection.cursor() # Obtiene el cursor para consultas
    db_cursor.execute("SELECT id, nombre FROM stations") # Ejecuta la consulta de todas las mesas
    stations_list = [{"id": row[0], "nombre": row[1]} for row in db_cursor.fetchall()] # Formatea los resultados en una lista
    db_connection.close() # Cierra la conexion a la base de datos
    
    return jsonify({"status": 200, "data": stations_list}), 200 # Responde con la lista de estaciones encontradas

@app.route('/stations/<int:station_id>', methods=['PUT']) # Define endpoint para actualizar nombre de mesa
def update_station_name(station_id): # Funcion que procesa la actualizacion
    auth_header = request.headers.get("Authorization", "") # Extrae token de autenticacion
    username = validate_jwt_local(auth_header) # Realiza validacion sin estado
    if not username: # Verifica exito de analisis
        return jsonify({"status": 401, "message": "Permission denied"}), 401 # Rechaza la modificacion

    request_body = request.json or {} # Lee los datos enviados en el PUT
    updated_name = request_body.get("nombre") # Extrae el nuevo nombre deseado
    
    if not updated_name: # Valida que se haya enviado un nombre
        return jsonify({"status": 400, "message": "Debes especificar el campo 'nombre'"}), 400 # Informa falta de dato

    connection = database.get_connection() # Conecta a la base de datos local
    cursor = connection.cursor() # Crea cursor de ejecucion SQL
    
    cursor.execute("UPDATE stations SET nombre = %s WHERE id = %s", (updated_name, station_id)) # Ejecuta actualizacion segura
    
    if cursor.rowcount == 0: # Verifica si se encontro la mesa solicitada
        connection.close() # Cierra la DB si no hubo cambios
        return jsonify({"status": 404, "message": f"La mesa {station_id} no existe"}), 404 # Error de mesa no encontrada
        
    connection.commit() # Guarda el cambio de nombre permanentemente
    connection.close() # Cierra la conexion final
    
    return jsonify({"status": 200, "message": f"Mesa {station_id} ha sido renombrada a '{updated_name}'"}), 200 # Confirma exito

@app.route('/stations/<int:station_id>', methods=['GET']) # Vincula endpoint para una estacion
def get_single_station(station_id): # Obtiene una estacion especifica
    auth_header = request.headers.get("Authorization", "") # Obtiene el encabezado
    username = validate_jwt_local(auth_header) # Analiza el token
    if not username: # Si el token falla
        return jsonify({"status": 401, "message": "Unauthorized"}), 401 # Devuelve 401
        
    connection = database.get_connection() # Abre conexion a DB
    cursor = connection.cursor() # Crea cursor
    cursor.execute("SELECT id, nombre FROM stations WHERE id = %s", (station_id,)) # Lee fila
    row = cursor.fetchone() # Extrae datos de fila
    connection.close() # Cierra DB normalmente
    
    if not row: # Verifica si la estacion existe
        return jsonify({"status": 404, "message": "Station not found"}), 404 # Devuelve no encontrado 
    return jsonify({"status": 200, "data": {"id": row[0], "nombre": row[1]}}), 200 # Devuelve el payload

if __name__ == '__main__': # Verifica ejecucion directa
    database.init_db() # Prepara esquema
    service_port = int(os.getenv("STATION_SERVICE_PORT", 5002)) # Obtiene puerto de entorno
    app.run(host='0.0.0.0', port=service_port) # Inicia proceso del servidor
