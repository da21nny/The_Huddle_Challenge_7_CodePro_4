from flask import Flask, request, jsonify # Importa herramientas de Flask
import sqlite3 # Importa motor de base de datos SQLite
import uuid # Importa generador de IDs unicos
import database # Importa modulo local de base de datos
import os # Importa utilidades del sistema operativo

app = Flask(__name__) # Inicializa la aplicacion Flask

@app.route('/login', methods=['POST']) # Define ruta para iniciar sesion
def login(): # Funcion para procesar el ingreso de usuarios
    datos = request.json or {} # Obtiene datos enviados en formato JSON
    nombre_usuario = datos.get('username') # Extrae el nombre de usuario
    password = datos.get('password') # Extrae la contraseña del usuario
    
    conexion = sqlite3.connect(database.DB_PATH) # Conecta a la base de datos
    cursor = conexion.cursor() # Crea un cursor para ejecutar comandos
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (nombre_usuario, password)) # Busca al usuario
    usuario_encontrado = cursor.fetchone() # Obtiene el resultado de la busqueda
    
    if usuario_encontrado: # Si los datos son correctos
        token_acceso = "token-" + str(uuid.uuid4()) # Genera un nuevo token aleatorio
        cursor.execute("INSERT INTO tokens (token, username) VALUES (?, ?)", (token_acceso, nombre_usuario)) # Guarda el token
        conexion.commit() # Confirma los cambios en la base de datos
        conexion.close() # Cierra la conexion actual
        return jsonify({"status": 200, "token": token_acceso}), 200 # Devuelve el token exitosamente
    
    conexion.close() # Cierra la conexion si no hubo exito
    return jsonify({"status": 401, "message": "Credenciales inválidas"}), 401 # Indica error de autenticacion

@app.route('/register', methods=['POST']) # Define ruta para registrar usuarios
def register(): # Funcion para dar de alta nuevos usuarios
    datos = request.json or {} # Recibe informacion de registro
    nombre_usuario = datos.get('username') # Toma el nombre de usuario deseado
    password = datos.get('password') # Toma la contraseña elegida
    
    if not nombre_usuario or not password: # Valida que los campos no esten vacios
        return jsonify({"status": 400, "message": "Faltan credenciales"}), 400 # Error por datos incompletos
        
    conexion = sqlite3.connect(database.DB_PATH) # Abre conexion a la DB
    cursor = conexion.cursor() # Prepara el cursor de ejecucion
    try: # Intenta realizar el registro
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nombre_usuario, password)) # Inserta el usuario
        conexion.commit() # Guarda el nuevo usuario permanentemente
        conexion.close() # Finaliza la conexion
        return jsonify({"status": 201, "message": "Usuario registrado exitosamente"}), 201 # Confirma el exito
    except sqlite3.IntegrityError: # Captura si el usuario ya existe
        conexion.close() # Cierra la conexion tras el error
        return jsonify({"status": 409, "message": "El usuario ya existe"}), 409 # Informa conflicto de duplicidad

@app.route('/verify', methods=['GET']) # Define ruta para validar tokens
def verify(): # Funcion para comprobar si un token es valido
    cabecera_autorizacion = request.headers.get("Authorization", "") # Lee la cabecera de autorizacion
    token_recibido = cabecera_autorizacion.replace("Bearer ", "") # Limpia el prefijo del token
    
    conexion = sqlite3.connect(database.DB_PATH) # Conecta con la base de datos de auth
    cursor = conexion.cursor() # Inicia el cursor de busqueda
    cursor.execute("SELECT username FROM tokens WHERE token=?", (token_recibido,)) # Busca el usuario dueño del token
    usuario_dueno = cursor.fetchone() # Obtiene el nombre del usuario
    conexion.close() # Libera la conexion a la DB
    
    if usuario_dueno: # Si el token existe y es valido
        return jsonify({"status": 200, "username": usuario_dueno[0]}), 200 # Devuelve ok y el nombre de usuario
    return jsonify({"status": 401, "message": "No autorizado"}), 401 # Indica que el token no sirve

if __name__ == '__main__': # Punto de entrada del script
    database.init_db() # Crea las tablas si no existen
    puerto = int(os.getenv("AUTH_SERVICE_PORT", 5001)) # Obtiene el puerto de configuracion
    app.run(host='0.0.0.0', port=puerto) # Inicia el servidor en todas las interfaces
