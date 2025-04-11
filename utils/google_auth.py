"""
Local Authentication for AI Chat Studio
Provides secure authentication using username and password
"""

import os
import hashlib
import secrets
import streamlit as st
from utils.database import get_db_connection

def hash_password(password):
    """Hash a password for secure storage."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by the user."""
    try:
        salt, hashed = stored_password.split('$')
        return hashed == hashlib.sha256((salt + provided_password).encode()).hexdigest()
    except ValueError:
        return False

def init_auth_tables():
    """Initialize authentication tables in the database."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            # Create user table if not exists
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create sessions table if not exists
            cur.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                )
            ''')

            conn.commit()
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
    finally:
        conn.close()

def create_user(username, password, is_admin=False):
    """Create a new user in the database."""
    conn = get_db_connection()
    if conn is None:
        return False

    password_hash = hash_password(password)

    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (%s, %s, %s)
            ''', (username, password_hash, is_admin))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user with a username and password."""
    conn = get_db_connection()
    if conn is None:
        return False, None

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT password_hash, is_admin FROM users WHERE username = %s
            ''', (username,))
            result = cur.fetchone()

            if result:
                password_hash, is_admin = result
                if verify_password(password_hash, password):
                    return True, {"username": username, "is_admin": is_admin}

            return False, None
    except Exception as e:
        st.error(f"Error authenticating user: {str(e)}")
        return False, None
    finally:
        conn.close()

def create_session(username):
    """Create a new session for a user."""
    conn = get_db_connection()
    if conn is None:
        return None

    token = secrets.token_hex(32)
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=30)

    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM sessions WHERE username = %s', (username,))
            cur.execute('''
                INSERT INTO sessions (username, token, expires_at)
                VALUES (%s, %s, %s)
            ''', (username, token, expires_at))
            conn.commit()
            return token
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None
    finally:
        conn.close()

def validate_session(token):
    """Validate a session token and return user info if valid."""
    if not token:
        return False, None

    conn = get_db_connection()
    if conn is None:
        return False, None

    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT s.username, s.expires_at, u.is_admin
                FROM sessions s
                JOIN users u ON s.username = u.username
                WHERE s.token = %s
            ''', (token,))

            result = cur.fetchone()
            if not result:
                return False, None

            username, expires_at, is_admin = result

            from datetime import datetime
            if expires_at < datetime.utcnow():
                cur.execute('DELETE FROM sessions WHERE token = %s', (token,))
                conn.commit()
                return False, None

            return True, {"username": username, "is_admin": is_admin}
    except Exception as e:
        st.error(f"Error validating session: {str(e)}")
        return False, None
    finally:
        conn.close()

def end_session(token):
    """End a session."""
    if not token:
        return False

    conn = get_db_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM sessions WHERE token = %s', (token,))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error ending session: {str(e)}")
        return False
    finally:
        conn.close()

def check_login():
    """
    Check if a user is logged in via local authentication.
    """
    init_auth_tables()

    if "user" not in st.session_state:
        st.session_state.user = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if not st.session_state.is_authenticated:
        show_login_page()
        st.stop()

def show_login_page():
    """Display the login page."""
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        is_authenticated, user_info = authenticate_user(username, password)
        if is_authenticated:
            st.session_state.user = user_info
            st.session_state.is_authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout_user():
    """Log out the current user."""
    if "user" in st.session_state and st.session_state.user:
        if "token" in st.session_state.user:
            end_session(st.session_state.user["token"])

    st.session_state.user = None
    st.session_state.is_authenticated = False
    st.rerun()

def get_current_user():
    """
    Returns the currently logged-in user's username or None.
    """
    if st.session_state.is_authenticated and st.session_state.user:
        return st.session_state.user.get("username")
    return None

def is_admin():
    """
    Check if the current user is an admin.
    """
    if st.session_state.is_authenticated and st.session_state.user:
        return st.session_state.user.get("is_admin", False)
    return False

def check_google_auth():
    # ... existing code ...
    if "google_auth_state" in st.session_state:
        del st.session_state["google_auth_state"]
        st.rerun()
    
    # ... existing code ...
    if st.button("Sign out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()