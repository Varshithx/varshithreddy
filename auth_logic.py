"""
auth_logic.py — Registration, Login, Logout Logic

All functions return dictionaries that Flask can easily convert to JSON.
Example: return {"message": "...", "success": True/False}

Your Flask route just needs to do:
    from auth_logic import register, login
    result = register(username, email, password)
    return jsonify(result), result["status"]
"""

import hashlib
from database import users_db, get_next_user_id


# ── PASSWORD HASHING ──
def hash_password(password):
    """Convert a plain password into a hashed string that can't be reversed."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_hash, password_attempt):
    """Check if a password attempt matches the stored hash."""
    return stored_hash == hashlib.sha256(password_attempt.encode()).hexdigest()


# ── REGISTER ──
def register(username, email, password):
    """
    Registers a new user.
    Returns a dict with message, success, and HTTP status code.
    """

    # Validate — are all fields filled?
    if not username or not email or not password:
        return {"message": "All fields are required.", "success": False, "status": 400}

    # Validate — is password long enough?
    if len(password) < 6:
        return {"message": "Password must be at least 6 characters.", "success": False, "status": 400}

    # Check — is the username already taken?
    for user in users_db:
        if user["username"] == username:
            return {"message": "Username already taken.", "success": False, "status": 409}

    # Check — is the email already registered?
    for user in users_db:
        if user["email"] == email:
            return {"message": "Email already registered.", "success": False, "status": 409}

    # Create the user
    new_user = {
        "id": get_next_user_id(),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
    }
    users_db.append(new_user)

    return {"message": "Registration successful!", "success": True, "status": 201}


# ── LOGIN ──
def login(username, password):
    """
    Checks credentials.
    Returns a dict with message, success, user data (without password), and status code.
    """

    # Find the user by username
    found_user = None
    for user in users_db:
        if user["username"] == username:
            found_user = user
            break

    # If no user found
    if found_user is None:
        return {"message": "Invalid username or password.", "success": False, "status": 401}

    # Check the password
    if check_password(found_user["password_hash"], password):
        # Return user data WITHOUT the password hash (never send passwords to frontend)
        safe_user = {
            "id": found_user["id"],
            "username": found_user["username"],
            "email": found_user["email"],
        }
        return {
            "message": f"Welcome back, {found_user['username']}!",
            "success": True,
            "user": safe_user,
            "status": 200,
        }
    else:
        return {"message": "Invalid username or password.", "success": False, "status": 401}


# ── LOGOUT ──
def logout():
    """
    Logout just returns a success message.
    In Flask, your route should clear the session: session.clear()
    """
    return {"message": "Logged out successfully.", "success": True, "status": 200}


# ============================================================
# ── TEST IT ──
# ============================================================
if __name__ == "__main__":
    from database import print_all_data

    print("=" * 50)
    print("TESTING REGISTRATION")
    print("=" * 50)

    result = register("john", "john@example.com", "mypassword123")
    print(f"Register john: {result}")

    result = register("john", "other@example.com", "password456")
    print(f"Register john again: {result}")

    result = register("", "", "")
    print(f"Register empty: {result}")

    result = register("jane", "jane@example.com", "123")
    print(f"Register short password: {result}")

    print()
    print("=" * 50)
    print("TESTING LOGIN")
    print("=" * 50)

    result = login("john", "mypassword123")
    print(f"Login john (correct): {result}")

    result = login("john", "wrongpassword")
    print(f"Login john (wrong):   {result}")

    result = login("nobody", "whatever")
    print(f"Login nobody:         {result}")

    print()
    print("=" * 50)
    print("TESTING LOGOUT")
    print("=" * 50)

    result = logout()
    print(f"Logout: {result}")

    print()
    print_all_data()
