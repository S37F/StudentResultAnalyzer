import hashlib
import json
import os
from datetime import datetime

# Simple file-based user storage for demo purposes
USERS_FILE = "users.json"

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except:
        return False

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user login"""
    users = load_users()
    
    if username in users:
        stored_hash = users[username]['password']
        return stored_hash == hash_password(password)
    
    return False

def create_user(username, password, full_name, email):
    """Create new user account"""
    users = load_users()
    
    # Check if user already exists
    if username in users:
        return False
    
    # Create new user
    users[username] = {
        'password': hash_password(password),
        'full_name': full_name,
        'email': email,
        'created_at': datetime.now().isoformat(),
        'last_login': None
    }
    
    return save_users(users)

def check_user_exists(username):
    """Check if username already exists"""
    users = load_users()
    return username in users

def update_last_login(username):
    """Update user's last login timestamp"""
    users = load_users()
    
    if username in users:
        users[username]['last_login'] = datetime.now().isoformat()
        save_users(users)

def get_user_info(username):
    """Get user information"""
    users = load_users()
    return users.get(username, {})
