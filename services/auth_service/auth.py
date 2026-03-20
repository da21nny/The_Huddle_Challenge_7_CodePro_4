from flask import Flask, request, jsonify
import sqlite3
import uuid
import database
import os

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    
    if user:
        token = "token-" + str(uuid.uuid4())
        c.execute("INSERT INTO tokens (token, username) VALUES (?, ?)", (token, username))
        conn.commit()
        conn.close()
        return jsonify({"status": 200, "token": token}), 200
    
    conn.close()
    return jsonify({"status": 401, "message": "Credenciales inválidas"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"status": 400, "message": "Faltan credenciales"}), 400
        
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"status": 201, "message": "Usuario registrado exitosamente"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": 409, "message": "El usuario ya existe"}), 409

@app.route('/verify', methods=['GET'])
def verify():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM tokens WHERE token=?", (token,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": 200, "username": user[0]}), 200
    return jsonify({"status": 401, "message": "No autorizado"}), 401

if __name__ == '__main__':
    database.init_db()
    # Usamos el puerto 5001 para Auth Service
    port = int(os.getenv("AUTH_SERVICE_PORT", 5001))
    app.run(host='0.0.0.0', port=port)
