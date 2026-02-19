"""
app.py — Flask Application

This is the main file that runs your web server.
It connects HTML pages to Python logic to MySQL database.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

# ── Create the Flask app ──
app = Flask(__name__)

# ── Secret key for sessions (CHANGE THIS to something random) ──
app.secret_key = 'your-super-secret-key-change-this-to-anything-random'

# ── MySQL Configuration ──
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ilensys@123'     # ← YOUR MySQL password
app.config['MYSQL_DB'] = 'task_manager_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# ── Initialize MySQL ──
mysql = MySQL(app)


# ============================================================
#  PAGE ROUTES — These serve your HTML pages
# ============================================================

@app.route('/')
def home():
    """Home page — redirect to dashboard if logged in, else login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    """Show the login page."""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Show the registration page."""
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    """Show the dashboard (only if logged in)."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')


# ============================================================
#  API ROUTES — These handle data (called by JavaScript fetch)
# ============================================================

# ── REGISTER ──
@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new user."""
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validation
    if not username or not email or not password:
        return jsonify({'message': 'All fields are required.', 'success': False}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters.', 'success': False}), 400

    try:
        cursor = mysql.connection.cursor()

        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            return jsonify({'message': 'Username already taken.', 'success': False}), 409

        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({'message': 'Email already registered.', 'success': False}), 409

        # Hash the password and save
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, password_hash)
        )
        mysql.connection.commit()

        return jsonify({'message': 'Registration successful!', 'success': True}), 201

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ── LOGIN ──
@app.route('/api/login', methods=['POST'])
def api_login():
    """Login and start a session."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            # Save user info in session (this is like a cookie on the server)
            session['user_id'] = user['id']
            session['username'] = user['username']

            return jsonify({
                'message': f"Welcome back, {user['username']}!",
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid username or password.', 'success': False}), 401

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ── LOGOUT ──
@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Clear the session."""
    session.clear()
    return jsonify({'message': 'Logged out successfully.', 'success': True}), 200


# ── GET CURRENT USER ──
@app.route('/api/me')
def api_me():
    """Check who is currently logged in."""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'user': {
                'id': session['user_id'],
                'username': session['username']
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401


# ── GET ALL TASKS for logged-in user ──
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """Get all tasks for the logged-in user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC',
            (session['user_id'],)
        )
        tasks = cursor.fetchall()

        # Convert datetime objects to strings for JSON
        for task in tasks:
            task['created_at'] = task['created_at'].strftime('%Y-%m-%dT%H:%M:%S')
            task['done'] = bool(task['done'])

        return jsonify({'success': True, 'tasks': tasks}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error.'}), 500


# ── CREATE A TASK ──
@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """Create a new task."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title:
        return jsonify({'message': 'Task title cannot be empty.', 'success': False}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO tasks (title, content, user_id) VALUES (%s, %s, %s)',
            (title, content, session['user_id'])
        )
        mysql.connection.commit()

        return jsonify({'message': 'Task created!', 'success': True}), 201

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ── UPDATE A TASK ──
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def api_update_task(task_id):
    """Update a task's title and content."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    data = request.get_json()
    new_title = data.get('title', '').strip()
    new_content = data.get('content', '').strip()

    if not new_title:
        return jsonify({'message': 'Task title cannot be empty.', 'success': False}), 400

    try:
        cursor = mysql.connection.cursor()

        # Check task exists and belongs to user
        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_id = %s', (task_id, session['user_id']))
        task = cursor.fetchone()

        if not task:
            return jsonify({'message': 'Task not found.', 'success': False}), 404

        cursor.execute(
            'UPDATE tasks SET title = %s, content = %s WHERE id = %s AND user_id = %s',
            (new_title, new_content, task_id, session['user_id'])
        )
        mysql.connection.commit()

        return jsonify({'message': 'Task updated!', 'success': True}), 200

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ── DELETE A TASK ──
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete a task."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    try:
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_id = %s', (task_id, session['user_id']))
        task = cursor.fetchone()

        if not task:
            return jsonify({'message': 'Task not found.', 'success': False}), 404

        cursor.execute('DELETE FROM tasks WHERE id = %s AND user_id = %s', (task_id, session['user_id']))
        mysql.connection.commit()

        return jsonify({'message': 'Task deleted.', 'success': True}), 200

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ── TOGGLE TASK (done/not done) ──
@app.route('/api/tasks/<int:task_id>/toggle', methods=['PUT'])
def api_toggle_task(task_id):
    """Toggle the done status of a task."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    try:
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_id = %s', (task_id, session['user_id']))
        task = cursor.fetchone()

        if not task:
            return jsonify({'message': 'Task not found.', 'success': False}), 404

        new_done = not bool(task['done'])
        cursor.execute(
            'UPDATE tasks SET done = %s WHERE id = %s AND user_id = %s',
            (new_done, task_id, session['user_id'])
        )
        mysql.connection.commit()

        status = "done" if new_done else "not done"
        return jsonify({'message': f'Task marked as {status}.', 'success': True}), 200

    except Exception as e:
        return jsonify({'message': 'Server error.', 'success': False}), 500


# ============================================================
#  RUN THE APP
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)