from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
import psycopg2

app = Flask(__name__)

# Параметры подключения к базе данных PostgreSQL
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'your_database_name'
DB_USER = 'your_database_user'
DB_PASSWORD = 'your_database_password'

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, host=DB_HOST,
        port=DB_PORT
    )

# Эндпоинт для регистрации пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    hashed_password = pbkdf2_sha256.hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Эндпоинт для аутентификации пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        row = cur.fetchone()

        if row and pbkdf2_sha256.verify(password, row[0]):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
