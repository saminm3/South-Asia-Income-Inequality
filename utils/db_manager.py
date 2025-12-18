import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'inequality.db')

def init_db():
    """Initialize the database and create users table if not exists"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            age_range TEXT,
            gender TEXT,
            occupation TEXT,
            region TEXT,
            email TEXT,
            created_at DATETIME,
            last_visit DATETIME,
            visit_count INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(user_data):
    """Create a new user profile"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    user_id = f"USER_{str(uuid.uuid4())[:8].upper()}"
    now = datetime.now()
    
    try:
        c.execute('''
            INSERT INTO users (user_id, age_range, gender, occupation, region, email, created_at, last_visit, visit_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            user_data.get('age_range'),
            user_data.get('gender'),
            user_data.get('occupation'),
            user_data.get('region'),
            user_data.get('email'),
            now,
            now,
            1
        ))
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

def update_user_visit(user_id):
    """Update visit stats for an existing user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            UPDATE users 
            SET last_visit = ?, visit_count = visit_count + 1
            WHERE user_id = ?
        ''', (datetime.now(), user_id))
        conn.commit()
    finally:
        conn.close()

def get_user(user_id):
    """Retrieve user details"""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM users WHERE user_id = ?", conn, params=(user_id,))
        if not df.empty:
            return df.iloc[0].to_dict()
        return None
    finally:
        conn.close()

def update_user_profile(user_id, data):
    """Update specific user fields"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    fields = []
    values = []
    
    for key, value in data.items():
        if key in ['age_range', 'gender', 'occupation', 'region', 'email']:
            fields.append(f"{key} = ?")
            values.append(value)
            
    if not fields:
        return False
        
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
    
    try:
        c.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()
