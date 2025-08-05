#
# This is the updated app.py
#
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE_FILE = 'users.db'

# --- Admin Configuration ---
# In a real app, use environment variables for this!
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" # Change this to a strong password

# --- Database Initialization ---
def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

# --- User Routes (No changes needed here from your previous database version) ---
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("This email is already registered.")
        return redirect(url_for('register_page'))
    finally:
        conn.close()
    
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_email'] = user['email']
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

# --- NEW: Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Protect this route
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

# --- Root Route ---
@app.route('/')
def home():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)