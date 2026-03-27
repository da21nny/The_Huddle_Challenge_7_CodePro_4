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
def verify_token_with_auth(cabecera_auth): # Funcion que delega la validacion al servicio experto
    return requests.get(AUTH_URL, headers={"Authorization": cabecera_auth}, timeout=3) # Llama al endpoint de verificacion

AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:5001/verify") # Carga direccion del servicio auth

@app.route('/reservations', methods=['POST', 'GET']) # Define ruta para crear y listar reservas
def reservations(): # Manejador principal de reservas
    cabecera_auth = request.headers.get("Authorization", "") # Obtiene el token de seguridad
    try: # Inicia validacion del usuario via red
        respuesta_servidor = verify_token_with_auth(cabecera_auth) # Consulta al servicio de identidad
        if respuesta_servidor.status_code != 200: # Si el token es invalido
            return jsonify({"status": 401, "message": "No autorizado"}), 401 # Bloquea el acceso a la reserva
        nombre_usuario = respuesta_servidor.json().get("username") # Obtiene el nombre del pinguino autenticado
    except CircuitBreakerOpenException as error_cb: # Captura si el circuito esta previniendo llamadas
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(error_cb)}"}), 503 # Indica servicio saturado
    except requests.exceptions.RequestException: # Captura fallos de comunicacion fisica
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Error de infraestructura
        
    conexion_sqlite = database.get_connection() # Conecta a la base de datos de reservas
    cursor_sqlite = conexion_sqlite.cursor() # Crea el cursor de comandos SQL
    
    if request.method == 'POST': # Lógica para guardar una nueva reserva
        cuerpo_json = request.json or {} # Parsea el cuerpo del mensaje
        fecha_reserva = cuerpo_json.get("fecha") # Captura el dia elegido
        hora_reserva = cuerpo_json.get("hora") # Captura el horario elegido
        id_mesa = cuerpo_json.get("mesa_id") # Captura el identificador de la mesa
        
        if not fecha_reserva or not hora_reserva or not id_mesa: # Valida integridad de los datos
            return jsonify({"status": 400, "message": "Faltan datos (fecha, hora o mesa_id)"}), 400 # Informa omision de datos
            
        try: # Intenta insertar la reserva en la tabla
            cursor_sqlite.execute("INSERT INTO reservations (fecha, hora, mesa_id, username) VALUES (%s, %s, %s, %s)",
                      (fecha_reserva, hora_reserva, id_mesa, nombre_usuario)) # Realiza insercion protegida
            conexion_sqlite.commit() # Guarda la reserva en el disco
            conexion_sqlite.close() # Libera el archivo de base de datos
            return jsonify({"status": 201, "message": "Reserva creada exitosamente."}), 201 # Confirma registro exitoso
        except psycopg2.IntegrityError: # Controla si la mesa ya esta ocupada
            conexion_sqlite.close() # Libera la conexion antes de salir
            return jsonify({"status": 409, "message": "Conflicto: La mesa ya está reservada en esa fecha y hora."}), 409 # Informa colision

    elif request.method == 'GET': # Lógica para mostrar todas las reservas existentes
        cursor_sqlite.execute("SELECT fecha, hora, mesa_id, username FROM reservations") # Consulta todos los registros
        filas_encontradas = cursor_sqlite.fetchall() # Recupera la informacion de la DB
        lista_reservas = [{"fecha": r[0], "hora": r[1], "mesa_id": r[2], "usuario": r[3]} for r in filas_encontradas] # Mapea a dicts
        conexion_sqlite.close() # Cierra la conexion a la DB
        return jsonify({"status": 200, "data": lista_reservas}), 200 # Envía la lista completa de reservas

@app.route('/reservations/<int:id_reserva>', methods=['DELETE']) # Define ruta para cancelacion de reservas
def delete_reservation(id_reserva): # Funcion para eliminar una reserva por su ID
    token_para_borrar = request.headers.get("Authorization", "") # Identifica al solicitante del borrado
    try: # Valida que el solicitante sea un usuario real
        respuesta_auth = verify_token_with_auth(token_para_borrar) # Pide confirmacion al servicio Auth
        if respuesta_auth.status_code != 200: # Si la identidad no es valida
            return jsonify({"status": 401, "message": "Prohibido. No tienes permiso para borrar."}), 401 # Deniega el borrado
    except CircuitBreakerOpenException as error_cb: # Controla disponibilidad del sistema de seguridad
        return jsonify({"status": 503, "message": f"Circuit Breaker Activo: {str(error_cb)}"}), 503 # Informa servicio ocupado
    except requests.exceptions.RequestException: # Controla fallos de enlace de red
        return jsonify({"status": 500, "message": "Auth service error: No se pudo verificar el token"}), 500 # Informa fallo de red

    conexion_db = database.get_connection() # Abre conexion a la DB de reservas
    cursor_db = conexion_db.cursor() # Inicia el cursor para borrar
    cursor_db.execute("DELETE FROM reservations WHERE id = %s", (id_reserva,)) # Intenta ejecutar el borrado fisico
    
    if cursor_db.rowcount == 0: # Comprueba si realmente se borro algo
        conexion_db.close() # Cierra la conexion si no hubo accion
        return jsonify({"status": 404, "message": f"La reserva {id_reserva} no existe o ya fue borrada"}), 404 # Informa ID invalido
        
    conexion_db.commit() # Confirma el borrado permanentemente
    conexion_db.close() # Finaliza el acceso a la DB
    
    return jsonify({"status": 200, "message": f"Reserva {id_reserva} eliminada con éxito"}), 200 # Confirma eliminacion

if __name__ == '__main__': # Verifica si el script corre individualmente
    database.init_db() # Crea el esquema de reservas si es necesario
    puerto_ejecucion = int(os.getenv("RESERVATION_SERVICE_PORT", 5003)) # Lee puerto del entorno
    app.run(host='0.0.0.0', port=puerto_ejecucion) # Inicia el servidor de reservas
