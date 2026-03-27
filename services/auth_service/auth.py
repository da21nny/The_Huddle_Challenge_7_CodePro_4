from flask import Flask, request, jsonify # Importa herramientas de Flask
import psycopg2 # Importa motor de base de datos PostgreSQL
import jwt # Importa libreria para procesar JWT
import datetime # Importa modulo de tiempo para expiracion
import database # Importa manejador de DB local
import os # Importa utilidades del sistema operativo

SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_penguin_key") # Establece el secreto compartido

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
    
    if user_found: # Si el usuario existe
        payload = {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)} # Crea el payload del token
        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256") # Firma el nuevo JWT
        
        connection.close() # Cierra la conexion
        return jsonify({"status": 200, "token": access_token}), 200 # Devuelve el JWT generado
    
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

@app.route('/verify', methods=['GET']) # Define ruta de validacion
def verify(): # Funcion para validar token
    auth_header = request.headers.get("Authorization", "") # Obtiene el encabezado
    received_token = auth_header.replace("Bearer ", "") # Extrae la cadena JWT
    
    if not received_token: # Si falta el token
        return jsonify({"status": 401, "message": "Missing token"}), 401 # Error de token faltante
        
    try: # Intenta decodificar el token
        payload = jwt.decode(received_token, SECRET_KEY, algorithms=["HS256"]) # Decodifica y valida
        return jsonify({"status": 200, "username": payload["username"]}), 200 # Devuelve usuario valido
    except jwt.ExpiredSignatureError: # Si el token expiro
        return jsonify({"status": 401, "message": "Token expired"}), 401 # Error por caducidad
    except jwt.InvalidTokenError: # Si el token es invalido
        return jsonify({"status": 401, "message": "Invalid token"}), 401 # Error de formato invalido

if __name__ == '__main__': # Punto de entrada del script
    database.init_db() # Crea las tablas si no existen
    port = int(os.getenv("AUTH_SERVICE_PORT", 5001)) # Obtiene el puerto de configuracion
    app.run(host='0.0.0.0', port=port) # Inicia el servidor en todas las interfaces
