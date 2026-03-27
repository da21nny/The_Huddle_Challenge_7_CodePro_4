from flask import Flask, request, jsonify # Importa herramientas de Flask
import psycopg2 # Importa motor de base de datos PostgreSQL
import uuid # Importa generador de IDs unicos
import database # Importa modulo local de base de datos
import os # Importa utilidades del sistema operativo

app = Flask(__name__) # Inicializa la aplicacion Flask

@app.route('/login', methods=['POST']) # Define ruta para iniciar sesion
def login(): # Funcion para procesar el ingreso de usuarios
    data = request.json or {} # Obtiene datos enviados en formato JSON
    username = data.get('username') # Extrae el nombre de usuario
    password = data.get('password') # Extrae la contraseña del usuario
    
    connection = database.get_connection() # Conecta a la base de datos
    cursor = connection.cursor() # Crea un cursor para ejecutar comandos
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password)) # Busca al usuario
    user_found = cursor.fetchone() # Obtiene el resultado de la busqueda
    
    if user_found: # Si los datos son correctos
        access_token = "token-" + str(uuid.uuid4()) # Genera un nuevo token aleatorio
        cursor.execute("INSERT INTO tokens (token, username) VALUES (%s, %s)", (access_token, username)) # Guarda el token
        connection.commit() # Confirma los cambios en la base de datos
        connection.close() # Cierra la conexion actual
        return jsonify({"status": 200, "token": access_token}), 200 # Devuelve el token exitosamente
    
    connection.close() # Cierra la conexion si no hubo exito
    return jsonify({"status": 401, "message": "Credenciales inválidas"}), 401 # Indica error de autenticacion

@app.route('/register', methods=['POST']) # Define ruta para registrar usuarios
def register(): # Funcion para dar de alta nuevos usuarios
    data = request.json or {} # Recibe informacion de registro
    username = data.get('username') # Toma el nombre de usuario deseado
    password = data.get('password') # Toma la contraseña elegida
    
    if not username or not password: # Valida que los campos no esten vacios
        return jsonify({"status": 400, "message": "Faltan credenciales"}), 400 # Error por datos incompletos
        
    connection = database.get_connection() # Abre conexion a la DB
    cursor = connection.cursor() # Prepara el cursor de ejecucion
    try: # Intenta realizar el registro
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password)) # Inserta el usuario
        connection.commit() # Guarda el nuevo usuario permanentemente
        connection.close() # Finaliza la conexion
        return jsonify({"status": 201, "message": "Usuario registrado exitosamente"}), 201 # Confirma el exito
    except psycopg2.IntegrityError: # Captura si el usuario ya existe
        connection.close() # Cierra la conexion tras el error
        return jsonify({"status": 409, "message": "El usuario ya existe"}), 409 # Informa conflicto de duplicidad

@app.route('/verify', methods=['GET']) # Define ruta para validar tokens
def verify(): # Funcion para comprobar si un token es valido
    auth_header = request.headers.get("Authorization", "") # Lee la cabecera de autorizacion
    received_token = auth_header.replace("Bearer ", "") # Limpia el prefijo del token
    
    connection = database.get_connection() # Conecta con la base de datos de auth
    cursor = connection.cursor() # Inicia el cursor de busqueda
    cursor.execute("SELECT username FROM tokens WHERE token=%s", (received_token,)) # Busca el usuario dueño del token
    token_owner = cursor.fetchone() # Obtiene el nombre del usuario
    connection.close() # Libera la conexion a la DB
    
    if token_owner: # Si el token existe y es valido
        return jsonify({"status": 200, "username": token_owner[0]}), 200 # Devuelve ok y el nombre de usuario
    return jsonify({"status": 401, "message": "No autorizado"}), 401 # Indica que el token no sirve

if __name__ == '__main__': # Punto de entrada del script
    database.init_db() # Crea las tablas si no existen
    port = int(os.getenv("AUTH_SERVICE_PORT", 5001)) # Obtiene el puerto de configuracion
    app.run(host='0.0.0.0', port=port) # Inicia el servidor en todas las interfaces
