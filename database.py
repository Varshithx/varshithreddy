"""
database.py — Centralized Data Storage

Currently uses in-memory lists (for testing without MySQL).
When you connect Flask + MySQL, replace these lists with actual MySQL queries.

============================================================
MySQL TABLE STRUCTURES — Create these in MySQL Workbench
============================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT DEFAULT '',
    done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

============================================================
API ENDPOINTS — Your Flask routes should handle these:
============================================================

POST   /api/register          → register a new user
POST   /api/login             → login and start session
POST   /api/logout            → logout and clear session
GET    /api/tasks             → get all tasks for logged-in user
POST   /api/tasks             → create a new task
PUT    /api/tasks/<id>        → update a task
DELETE /api/tasks/<id>        → delete a task
PUT    /api/tasks/<id>/toggle → toggle done/not done

============================================================
"""

# ── Temporary in-memory storage (replace with MySQL later) ──
users_db = []
tasks_db = []

next_user_id = 1
next_task_id = 1


def get_next_user_id():
    """Returns a unique ID for a new user and increments the counter."""
    global next_user_id
    uid = next_user_id
    next_user_id += 1
    return uid


def get_next_task_id():
    """Returns a unique ID for a new task and increments the counter."""
    global next_task_id
    tid = next_task_id
    next_task_id += 1
    return tid


def print_all_data():
    """Prints all stored users and tasks — useful for debugging."""
    print("=" * 50)
    print("ALL USERS IN DATABASE")
    print("=" * 50)
    if not users_db:
        print("  (no users)")
    for user in users_db:
        print(f"  id={user['id']}, username={user['username']}, email={user['email']}")
        print(f"  password_hash={user['password_hash']}")
        print()

    print("=" * 50)
    print("ALL TASKS IN DATABASE")
    print("=" * 50)
    if not tasks_db:
        print("  (no tasks)")
    for task in tasks_db:
        check = "✓" if task["done"] else " "
        print(f"  [{check}] #{task['id']} — {task['title']} (user_id={task['user_id']})")
        if task["content"]:
            print(f"       Details: {task['content']}")
        print(f"       Created: {task['created_at']}")
        print()
