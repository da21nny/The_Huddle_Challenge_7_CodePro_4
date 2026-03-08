from flask import Flask, request, jsonify
import sqlite3
import uuid
import database

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('auth.db')
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

@app.route('/verify', methods=['GET'])
def verify():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    
    conn = sqlite3.connect('auth.db')
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
    app.run(port=5001)
