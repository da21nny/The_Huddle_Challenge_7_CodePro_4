from flask import Flask, request, jsonify # Importa componentes para el servidor web
import sqlite3 # Importa libreria para base de datos local
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
def verify_token_with_auth(cabecera_auth): # Funcion que valida el token con el microservicio Auth
    return requests.get(AUTH_URL, headers={"Authorization": cabecera_auth}, timeout=3) # Realiza la peticion GET al servicio Auth

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify") # Carga la URL de validacion desde el entorno

@app.route('/stations', methods=['GET']) # Define el endpoint para listar mesas
def get_stations(): # Funcion que maneja la obtencion de estaciones
    cabecera_auth = request.headers.get("Authorization", "") # Obtiene el token de los headers
    try: # Inicia bloque protegido para llamadas entre servicios
        respuesta_servicio = verify_token_with_auth(cabecera_auth) # Llama al servicio de autenticacion
        if respuesta_servicio.status_code != 200: # Si la respuesta no es satisfactoria
            return jsonify({"status": 401, "message": "No autorizado"}), 401 # Retorna error de permisos
    except CircuitBreakerOpenException as error_bloqueo: # Atrapa si el circuito esta abierto
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(error_bloqueo)}"}), 503 # Error por servicio bloqueado
    except requests.exceptions.RequestException: # Atrapa fallos generales de red
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Error interno de conexion
        
    conexion_db = sqlite3.connect(database.DB_PATH) # Abre la base de datos de estaciones
    cursor_db = conexion_db.cursor() # Obtiene el cursor para consultas
    cursor_db.execute("SELECT id, nombre FROM stations") # Ejecuta la consulta de todas las mesas
    lista_mesas = [{"id": fila[0], "nombre": fila[1]} for fila in cursor_db.fetchall()] # Formatea los resultados en una lista
    conexion_db.close() # Cierra la conexion a la base de datos
    
    return jsonify({"status": 200, "data": lista_mesas}), 200 # Responde con la lista de estaciones encontradas

@app.route('/stations/<int:id_mesa>', methods=['PUT']) # Define endpoint para actualizar nombre de mesa
def update_station_name(id_mesa): # Funcion que procesa la actualizacion
    token_validacion = request.headers.get("Authorization", "") # Extrae el token para validar permisos
    try: # Protege la operacion con validacion externa
        respuesta_auth = verify_token_with_auth(token_validacion) # Valida el usuario actual
        if respuesta_auth.status_code != 200: # Si el usuario no tiene permisos
            return jsonify({"status": 401, "message": "No tienes permiso para editar mesas"}), 401 # Deniega el acceso
    except Exception as error_autorizacion: # Atrapa cualquier fallo en la validacion
        return jsonify({"status": 500, "message": f"Error validando la sesión: {error_autorizacion}"}), 500 # Informa fallo técnico

    cuerpo_peticion = request.json or {} # Lee los datos enviados en el PUT
    nombre_actualizado = cuerpo_peticion.get("nombre") # Extrae el nuevo nombre deseado
    
    if not nombre_actualizado: # Valida que se haya enviado un nombre
        return jsonify({"status": 400, "message": "Debes especificar el campo 'nombre'"}), 400 # Informa falta de dato

    conexion = sqlite3.connect(database.DB_PATH) # Conecta a la base de datos local
    cursor = conexion.cursor() # Crea cursor de ejecucion SQL
    
    cursor.execute("UPDATE stations SET nombre = ? WHERE id = ?", (nombre_actualizado, id_mesa)) # Ejecuta actualizacion segura
    
    if cursor.rowcount == 0: # Verifica si se encontro la mesa solicitada
        conexion.close() # Cierra la DB si no hubo cambios
        return jsonify({"status": 404, "message": f"La mesa {id_mesa} no existe"}), 404 # Error de mesa no encontrada
        
    conexion.commit() # Guarda el cambio de nombre permanentemente
    conexion.close() # Cierra la conexion final
    
    return jsonify({"status": 200, "message": f"Mesa {id_mesa} ha sido renombrada a '{nombre_actualizado}'"}), 200 # Confirma exito

if __name__ == '__main__': # Comprobacion de ejecucion directa
    database.init_db() # Inicializa tablas de estaciones por defecto
    puerto_servicio = int(os.getenv("STATION_SERVICE_PORT", 5002)) # Carga puerto desde el entorno
    app.run(host='0.0.0.0', port=puerto_servicio) # Lanza el servidor en el puerto configurado
