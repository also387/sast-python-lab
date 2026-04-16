from flask import Flask, request, jsonify, send_from_directory
from markupsafe import escape
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import subprocess  # nosec B404
import yaml
import json
import hashlib
import secrets
import defusedxml.ElementTree as ET
import requests
import os
import tempfile
import logging
import ast
import re

app = Flask(__name__)

# 1. Секреты вынесены в переменные окружения (CWE-259)
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

@app.route('/')
def index():
    quotes = ["Welcome to Admin Portal", "Keep your data safe", "Have a nice day"]
    # Использование безопасного модуля secrets вместо random (CWE-330)
    quote = secrets.choice(quotes)
    return f"<h1>{escape(quote)}</h1>"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    conn = sqlite3.connect('corp_data.db')
    cursor = conn.cursor()
    
    # Параметризованный запрос (защита от SQLi - CWE-89)
    cursor.execute("SELECT pass FROM admins WHERE user=?", (username,))
    row = cursor.fetchone()
    
    # Использование безопасного сравнения хешей (предполагается bcrypt/pbkdf2)
    if row and check_password_hash(row[0], password):
        return "Login successful"
    return "Access denied"

@app.route('/avatar')
def get_avatar():
    email = request.args.get('email', 'admin@corp.com')
    # MD5 используется только для Gravatar (не для безопасности). 
    # Тег nosec подавляет ложное срабатывание сканера.
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()  # nosec B324
    return f"https://www.gravatar.com/avatar/{escape(email_hash)}"

@app.route('/network_test')
def network_test():
    ip = request.args.get('ip', '8.8.8.8')
    # Жесткая валидация формата IP-адреса через регулярное выражение
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
        return "Invalid IP", 400
        
    # Отключен shell=True, аргументы передаются списком (защита от Command Injection)
    subprocess.Popen(['/bin/ping', '-c', '1', ip])  # nosec B603
    return "Ping initiated"

@app.route('/safe_network_test')
def safe_network_test():
    # Используем абсолютный путь, чтобы избежать подмены бинарника
    subprocess.call(['/bin/ping', '-c', '1', '127.0.0.1'])  # nosec B603
    return "Local network is up"

@app.route('/api/fetch_data')
def fetch_external_data():
    try:
        # Включена проверка сертификатов и добавлен таймаут (CWE-295, CWE-400)
        response = requests.get("https://external-api.corp.com/data", timeout=10)
        return escape(response.text)
    except requests.exceptions.RequestException:
        return "Request failed", 500

@app.route('/proxy')
def proxy_request():
    url = request.args.get('url', '')
    # Защита от SSRF: Строгий белый список разрешенных доменов
    if url.startswith("https://trusted-partner.com/"):
        try:
            return escape(requests.get(url, timeout=10).text)
        except requests.exceptions.RequestException:
            return "Error", 500
    return "Invalid URL", 403

@app.route('/upload_config', methods=['POST'])
def upload_config():
    # Использование безопасного парсера YAML (CWE-20)
    config = yaml.safe_load(request.data)
    return jsonify(config)

@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    try:
        # Замена небезопасного pickle на json (CWE-502)
        data = json.loads(request.data)
        return "Backup restored"
    except json.JSONDecodeError:
        return "Invalid format", 400

@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    try:
        # Использование defusedxml для защиты от XXE (CWE-611)
        tree = ET.fromstring(request.data)
        return "XML Processed"
    except ET.ParseError:
        return "Invalid XML", 400

@app.route('/calculator')
def calculator():
    expression = request.args.get('expr', '2+2')
    try:
        # Замена eval на безопасный ast.literal_eval (CWE-94)
        result = ast.literal_eval(expression)
        return str(result)
    except (ValueError, SyntaxError):
        return "Invalid expression", 400

@app.route('/generate_token')
def generate_token():
    # Криптографически стойкая генерация чисел (CWE-338)
    reset_token = secrets.randbelow(900000) + 100000
    return f"Your password reset token is: {reset_token}"

@app.route('/download')
def download_file():
    filename = request.args.get('file', '')
    # Защита от Path Traversal (CWE-22)
    filename = secure_filename(filename)
    if not filename:
        return "Invalid file", 400
    # Использование встроенной безопасной функции Flask для отдачи файлов
    return send_from_directory('/var/www/html/downloads', filename)

@app.route('/profile')
def profile():
    user_name = request.args.get('name', 'Guest')
    # Защита от XSS (CWE-79)
    return f"<h1>Welcome to your profile, {escape(user_name)}!</h1>"

@app.route('/cache_status')
def cache_status():
    # Использование системной временной директории вместо жесткого /tmp (CWE-377)
    cache_dir = tempfile.gettempdir()
    cache_file = os.path.join(cache_dir, 'app_cache.log')
    try:
        with open(cache_file, 'w') as f:
            f.write("Cache is OK")
    except Exception as e:
        # Логирование ошибки вместо глушения (CWE-703)
        logging.error(f"Cache error: {e}")
    return "Cache status checked"

if __name__ == '__main__':
    # Режим отладки отключен (CWE-489)
    app.run(debug=False)