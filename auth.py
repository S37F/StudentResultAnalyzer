import hashlib
import json
import os
from datetime import datetime
from database import UnifiedDatabaseManager

# Database manager instance
db_manager = UnifiedDatabaseManager()

def load_users():
    """Load users from database (backward compatibility)"""
    # This function is kept for backward compatibility
    # but now uses the database manager
    return {}

def save_users(users):
    """Save users to database (backward compatibility)"""
    # This function is kept for backward compatibility
    return True

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user login"""
    user = db_manager.get_user(username)
    
    if user:
        stored_hash = user.get('password_hash')
        return stored_hash == hash_password(password)
    
    return False

def create_user(username, password, full_name, email):
    """Create new user account"""
    # Check if user already exists
    if check_user_exists(username):
        return False
    
    # Create new user
    password_hash = hash_password(password)
    return db_manager.create_user(username, password_hash, full_name, email)

def check_user_exists(username):
    """Check if username already exists"""
    user = db_manager.get_user(username)
    return user is not None

def update_last_login(username):
    """Update user's last login timestamp"""
    # This functionality would need to be implemented in the database managers
    # For now, we'll skip this update as it's not critical
    pass

def get_user_info(username):
    """Get user information"""
    return db_manager.get_user(username) or {}
