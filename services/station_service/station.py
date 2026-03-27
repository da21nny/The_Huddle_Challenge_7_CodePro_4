from flask import Flask, request, jsonify # Importa componentes para el servidor web
import psycopg2 # Importa libreria para base de datos local
import requests # Importa libreria para llamadas HTTP externas
import database # Importa configuracion de base de datos local
import os # Importa acceso a variables de entorno
import sys # Importa utilidades del sistema para rutas

# Configuracion de ruta para poder importar utilidades compartidas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Añade el directorio padre al path
from utils.retry import retry # Importa el decorador de reintentos
from utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException # Importa el circuit breaker

app = Flask(__name__) # Crea la instancia de la aplicacion Flask

@circuit_breaker(maximos_fallos=3, ventana_temporal=10) # Aplica proteccion ante fallos en cascada
@retry(max_reintentos=3, retraso=1) # Reintenta la llamada si el servicio auth falla
def verify_token_with_auth(auth_header): # Funcion que valida el token con el microservicio Auth
    return requests.get(AUTH_URL, headers={"Authorization": auth_header}, timeout=3) # Realiza la peticion GET al servicio Auth

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify") # Carga la URL de validacion desde el entorno

@app.route('/stations', methods=['GET']) # Define el endpoint para listar mesas
def get_stations(): # Funcion que maneja la obtencion de estaciones
    auth_header = request.headers.get("Authorization", "") # Obtiene el token de los headers
    try: # Inicia bloque protegido para llamadas entre servicios
        service_response = verify_token_with_auth(auth_header) # Llama al servicio de autenticacion
        if service_response.status_code != 200: # Si la respuesta no es satisfactoria
            return jsonify({"status": 401, "message": "No autorizado"}), 401 # Retorna error de permisos
    except CircuitBreakerOpenException as open_circuit_error: # Atrapa si el circuito esta abierto
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(open_circuit_error)}"}), 503 # Error por servicio bloqueado
    except requests.exceptions.RequestException: # Atrapa fallos generales de red
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Error interno de conexion
        
    db_connection = database.get_connection() # Abre la base de datos de estaciones
    db_cursor = db_connection.cursor() # Obtiene el cursor para consultas
    db_cursor.execute("SELECT id, nombre FROM stations") # Ejecuta la consulta de todas las mesas
    stations_list = [{"id": row[0], "nombre": row[1]} for row in db_cursor.fetchall()] # Formatea los resultados en una lista
    db_connection.close() # Cierra la conexion a la base de datos
    
    return jsonify({"status": 200, "data": stations_list}), 200 # Responde con la lista de estaciones encontradas

@app.route('/stations/<int:station_id>', methods=['PUT']) # Define endpoint para actualizar nombre de mesa
def update_station_name(station_id): # Funcion que procesa la actualizacion
    validation_token = request.headers.get("Authorization", "") # Extrae el token para validar permisos
    try: # Protege la operacion con validacion externa
        auth_response = verify_token_with_auth(validation_token) # Valida el usuario actual
        if auth_response.status_code != 200: # Si el usuario no tiene permisos
            return jsonify({"status": 401, "message": "No tienes permiso para editar mesas"}), 401 # Deniega el acceso
    except Exception as auth_error: # Atrapa cualquier fallo en la validacion
        return jsonify({"status": 500, "message": f"Error validando la sesión: {auth_error}"}), 500 # Informa fallo técnico

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

if __name__ == '__main__': # Comprobacion de ejecucion directa
    database.init_db() # Inicializa tablas de estaciones por defecto
    service_port = int(os.getenv("STATION_SERVICE_PORT", 5002)) # Carga puerto desde el entorno
    app.run(host='0.0.0.0', port=service_port) # Lanza el servidor en el puerto configurado
