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
    """Register new user using Supabase"""
    client = db.get_client()
    if not client:
        return False, "Database connection not available"
    
    try:
        password_hash = hash_password(password)
        data = {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "organization": organization,
            "country": country
        }
        client.table("users").insert(data).execute()
        return True, "Registration successful!"
    except Exception as e:
        if "unique_violation" in str(e).lower() or "already exists" in str(e).lower():
            return False, "Email already exists"
        return False, f"Registration failed: {str(e)}"

def login_user(email: str, password: str):
    """Authenticate user using Supabase"""
    client = db.get_client()
    if not client:
        return False, None
    
    try:
        response = client.table("users").select("user_id, email, password_hash, name").eq("email", email).execute()
        user = response.data[0] if response.data else None
        
        if user and verify_password(password, user['password_hash']):
            return True, {
                'user_id': user['user_id'],
                'email': user['email'],
                'name': user['name']
            }
    except Exception as e:
        print(f"Login failed: {e}")
        
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