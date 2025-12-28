import bcrypt
import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from database import db

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(email: str, password: str, name: str = "", organization: str = "", country: str = ""):
    """Register new user"""
    import sqlite3
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, name, organization, country) VALUES (?, ?, ?, ?, ?)",
            (email, password_hash, name, organization, country)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Email already exists"
    finally:
        conn.close()

def login_user(email: str, password: str):
    """Authenticate user"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, email, password_hash, name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return True, {
            'user_id': user[0],
            'email': user[1],
            'name': user[3]
        }
    return False, None

def is_logged_in():
    """Check if user is logged in"""
    return 'user' in st.session_state and st.session_state.user is not None

def logout_user():
    """Logout user"""
    if 'user' in st.session_state:
        st.session_state.user = None
    if 'analysis_config' in st.session_state:
        st.session_state.analysis_config = None