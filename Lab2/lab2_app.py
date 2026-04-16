from flask import Flask, request, jsonify, make_response
import sqlite3
import subprocess
import yaml
import pickle
import hashlib
import random
import xml.etree.ElementTree as ET
import requests
import os

app = Flask(__name__)


AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
DB_PASSWORD = "super_secret_production_password_999"

TEST_DUMMY_PASSWORD = "default_placeholder_password"


@app.route('/')
def index():
    quotes =["Welcome to Admin Portal", "Keep your data safe", "Have a nice day"]
    quote = random.choice(quotes)
    return f"<h1>{quote}</h1>"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    pwd_hash = hashlib.md5(password.encode()).hexdigest()
    
    conn = sqlite3.connect('corp_data.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM admins WHERE user='{username}' AND pass='{pwd_hash}'")
    
    if cursor.fetchone():
        return "Login successful"
    return "Access denied"

@app.route('/avatar')
def get_avatar():
    email = request.args.get('email', 'admin@corp.com')
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}"

@app.route('/network_test')
def network_test():
    ip = request.args.get('ip', '8.8.8.8')
    cmd = f"ping -c 1 {ip}"
    subprocess.Popen(cmd, shell=True)
    return "Ping initiated"

@app.route('/safe_network_test')
def safe_network_test():
    subprocess.call(['ping', '-c', '1', '127.0.0.1'])
    return "Local network is up"

@app.route('/api/fetch_data')
def fetch_external_data():
    response = requests.get("https://external-api.corp.com/data", verify=False)
    return response.text

@app.route('/proxy')
def proxy_request():
    url = request.args.get('url')
    if url:
        return requests.get(url).text
    return "No URL provided"

@app.route('/upload_config', methods=['POST'])
def upload_config():
    config = yaml.load(request.data)
    return jsonify(config)

@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    data = pickle.loads(request.data)
    return "Backup restored"

@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    tree = ET.fromstring(request.data)
    return "XML Processed"

@app.route('/calculator')
def calculator():
    expression = request.args.get('expr', '2+2')
    result = eval(expression)
    return str(result)

@app.route('/generate_token')
def generate_token():
    reset_token = random.randint(100000, 999999)
    return f"Your password reset token is: {reset_token}"

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    with open(os.path.join('/var/www/html/downloads', filename), 'r') as f:
        return f.read()

@app.route('/profile')
def profile():
    user_name = request.args.get('name', 'Guest')
    return f"<h1>Welcome to your profile, {user_name}!</h1>"

@app.route('/cache_status')
def cache_status():
    try:
        with open('/tmp/app_cache.log', 'w') as f:
            f.write("Cache is OK")
    except Exception:
        pass
    return "Cache status checked"

if __name__ == '__main__':
    app.run(debug=True)