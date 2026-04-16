from flask import Flask, request, render_template_string
import os
import sqlite3
import secrets

app = Flask(__name__)

# Уязвимости для SAST:
SECRET_KEY = "hardcoded_secret_key_123"  # SPA7 secret detection
SQL_QUERY = "SELECT * FROM users WHERE id = '" + request.args.get('id') + "'"  # SQLi CWE-89

@app.route('/')
def index():
    user_input = request.args.get('search', '')  # XSS CWE-79
    return f"<h1>Search: {user_input}</h1>"  # НЕ экранировано!

@app.route('/login')
def login():
    username = request.args.get('user')
    password = request.args.get('pass')
    # Buffer overflow simulation в Python
    result = username * 10000  # Memory issue
    return f"Welcome {username}"

if __name__ == '__main__':
    app.run(debug=True)
