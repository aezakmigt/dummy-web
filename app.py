#
# This is the file: app.py
#
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for session management
USERS_FILE = 'users.json'

# --- Helper Functions for File Operations ---

def load_users():
    """Loads users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users_data):
    """Saves the users dictionary to the JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

# --- Initialization ---
# Ensure the user file exists when the app starts
if not os.path.exists(USERS_FILE):
    save_users({})
    print(f"Created empty user file: {USERS_FILE}")

# --- Registration Routes ---
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    
    users = load_users()

    if email in users:
        return "This email is already registered. <a href='/login'>Login here</a>."

    hashed_password = generate_password_hash(password)
    users[email] = {'password_hash': hashed_password}
    save_users(users)
    
    return redirect(url_for('login_page'))

# --- Login & Dashboard Routes ---
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    
    users = load_users()
    user_data = users.get(email)

    if user_data and check_password_hash(user_data['password_hash'], password):
        session['user_email'] = email
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password.'})

@app.route('/dashboard')
def dashboard():
    if 'user_email' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login_page'))

# --- Root Route ---
@app.route('/')
def home():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)