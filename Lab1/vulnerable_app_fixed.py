from flask import Flask, request
from markupsafe import escape  # Функция для защиты от XSS
import os
import sqlite3
import secrets

app = Flask(__name__)

# Секретный ключ берется из переменной окружения (CWE-259/321)
# Если переменной нет, генерируется случайный безопасный ключ
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.secret_key = SECRET_KEY

# Использование параметризованного запроса вместо конкатенации (CWE-89)
# Знак '?' гарантирует, что БД воспримет ввод как текст, а не как команду
SQL_QUERY = "SELECT * FROM users WHERE id = ?" 

@app.route('/')
def index():
    user_input = request.args.get('search', '') 
    
    # Экранирование пользовательского ввода (CWE-79 - XSS)
    # escape() превращает спецсимволы (типа <script>) в безопасный текст
    safe_input = escape(user_input)
    
    return f"<h1>Search: {safe_input}</h1>"

@app.route('/login')
def login():
    username = request.args.get('user')
    password = request.args.get('pass')
    
    if username:
        # Ограничение длины ввода для предотвращения DoS (CWE-400)
        # Не даем злоумышленнику забить память огромной строкой
        if len(username) > 50:
            return "Error: Username is too long", 400
            
        result = username * 10  # Теперь умножение безопасно
        
        # Также экранируем имя пользователя при выводе на всякий случай
        return f"Welcome {escape(username)}"
        
    return "Please provide user credentials"

if __name__ == '__main__':
    # Выключение режима отладки для production (CWE-94)
    app.run(debug=False)