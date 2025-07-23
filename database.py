"""
Database management system supporting PostgreSQL and MongoDB
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import logging

# Database imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.postgres_url = os.getenv('DATABASE_URL')
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
        self.database_type = os.getenv('DB_TYPE', 'postgres')  # 'postgres', 'mongodb', or 'json'
        
    def get_database_type(self):
        """Determine which database to use based on availability and configuration"""
        if self.database_type == 'postgres' and POSTGRES_AVAILABLE and self.postgres_url:
            return 'postgres'
        elif self.database_type == 'mongodb' and MONGODB_AVAILABLE:
            return 'mongodb'
        else:
            return 'json'  # Fallback to file-based storage

class PostgreSQLManager:
    """PostgreSQL database manager"""
    
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.engine = None
        if SQLALCHEMY_AVAILABLE:
            self.engine = create_engine(connection_url, poolclass=StaticPool)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    # Users table
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            full_name VARCHAR(255) NOT NULL,
                            email VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP
                        )
                    """))
                    
                    # Student results table
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS student_results (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            academic_year VARCHAR(50) NOT NULL,
                            semester VARCHAR(50) NOT NULL,
                            subject VARCHAR(255) NOT NULL,
                            ca_marks FLOAT DEFAULT 0,
                            ese_marks FLOAT DEFAULT 0,
                            lab_marks FLOAT DEFAULT 0,
                            total_marks FLOAT DEFAULT 0,
                            sgpa FLOAT DEFAULT 0,
                            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (username) REFERENCES users(username)
                        )
                    """))
                    
                    conn.commit()
                    logger.info("PostgreSQL tables initialized successfully")
            else:
                # Fallback using psycopg2 directly
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_results (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) NOT NULL,
                        academic_year VARCHAR(50) NOT NULL,
                        semester VARCHAR(50) NOT NULL,
                        subject VARCHAR(255) NOT NULL,
                        ca_marks FLOAT DEFAULT 0,
                        ese_marks FLOAT DEFAULT 0,
                        lab_marks FLOAT DEFAULT 0,
                        total_marks FLOAT DEFAULT 0,
                        sgpa FLOAT DEFAULT 0,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                cursor.close()
                conn.close()
                logger.info("PostgreSQL tables initialized with psycopg2")
                
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL tables: {e}")
    
    def create_user(self, username: str, password_hash: str, full_name: str, email: str) -> bool:
        """Create a new user"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO users (username, password_hash, full_name, email)
                        VALUES (:username, :password_hash, :full_name, :email)
                    """), {
                        'username': username,
                        'password_hash': password_hash,
                        'full_name': full_name,
                        'email': email
                    })
                    conn.commit()
            else:
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, email)
                    VALUES (%s, %s, %s, %s)
                """, (username, password_hash, full_name, email))
                conn.commit()
                cursor.close()
                conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT username, password_hash, full_name, email, created_at, last_login
                        FROM users WHERE username = :username
                    """), {'username': username})
                    row = result.fetchone()
                    if row:
                        return dict(row._mapping)
            else:
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT username, password_hash, full_name, email, created_at, last_login
                    FROM users WHERE username = %s
                """, (username,))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def save_results(self, username: str, academic_year: str, semester: str, df: pd.DataFrame) -> bool:
        """Save student results"""
        try:
            # First, delete existing data for this semester
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        DELETE FROM student_results 
                        WHERE username = :username AND academic_year = :academic_year AND semester = :semester
                    """), {
                        'username': username,
                        'academic_year': academic_year,
                        'semester': semester
                    })
                    
                    # Insert new data
                    for _, row in df.iterrows():
                        conn.execute(text("""
                            INSERT INTO student_results 
                            (username, academic_year, semester, subject, ca_marks, ese_marks, lab_marks, total_marks, sgpa)
                            VALUES (:username, :academic_year, :semester, :subject, :ca_marks, :ese_marks, :lab_marks, :total_marks, :sgpa)
                        """), {
                            'username': username,
                            'academic_year': academic_year,
                            'semester': semester,
                            'subject': row.get('Subject', ''),
                            'ca_marks': float(row.get('CA_Marks', 0)),
                            'ese_marks': float(row.get('ESE_Marks', 0)),
                            'lab_marks': float(row.get('Lab_Marks', 0)),
                            'total_marks': float(row.get('Total', 0)),
                            'sgpa': float(row.get('SGPA', 0))
                        })
                    conn.commit()
            else:
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM student_results 
                    WHERE username = %s AND academic_year = %s AND semester = %s
                """, (username, academic_year, semester))
                
                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO student_results 
                        (username, academic_year, semester, subject, ca_marks, ese_marks, lab_marks, total_marks, sgpa)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        username, academic_year, semester,
                        row.get('Subject', ''),
                        float(row.get('CA_Marks', 0)),
                        float(row.get('ESE_Marks', 0)),
                        float(row.get('Lab_Marks', 0)),
                        float(row.get('Total', 0)),
                        float(row.get('SGPA', 0))
                    ))
                
                conn.commit()
                cursor.close()
                conn.close()
            
            return True
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def get_user_data(self, username: str) -> List[Dict]:
        """Get all data for a user"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT academic_year, semester, subject, ca_marks, ese_marks, lab_marks, total_marks, sgpa, uploaded_at
                        FROM student_results 
                        WHERE username = :username
                        ORDER BY academic_year, semester, subject
                    """), {'username': username})
                    rows = result.fetchall()
            else:
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT academic_year, semester, subject, ca_marks, ese_marks, lab_marks, total_marks, sgpa, uploaded_at
                    FROM student_results 
                    WHERE username = %s
                    ORDER BY academic_year, semester, subject
                """, (username,))
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
            
            # Group by semester
            semesters = {}
            for row in rows:
                key = f"{row['academic_year']}_{row['semester']}"
                if key not in semesters:
                    semesters[key] = {
                        'academic_year': row['academic_year'],
                        'semester': row['semester'],
                        'uploaded_at': row['uploaded_at'].isoformat() if row['uploaded_at'] else None,
                        'data': []
                    }
                
                semesters[key]['data'].append({
                    'Subject': row['subject'],
                    'CA_Marks': row['ca_marks'],
                    'ESE_Marks': row['ese_marks'],
                    'Lab_Marks': row['lab_marks'],
                    'Total': row['total_marks'],
                    'SGPA': row['sgpa']
                })
            
            # Convert to list and add DataFrame
            result = []
            for semester_data in semesters.values():
                semester_data['data'] = pd.DataFrame(semester_data['data'])
                result.append(semester_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return []
    
    def clear_user_data(self, username: str) -> bool:
        """Clear all data for a user"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        DELETE FROM student_results WHERE username = :username
                    """), {'username': username})
                    conn.commit()
            else:
                conn = psycopg2.connect(self.connection_url)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student_results WHERE username = %s", (username,))
                conn.commit()
                cursor.close()
                conn.close()
            return True
        except Exception as e:
            logger.error(f"Error clearing user data: {e}")
            return False

class MongoDBManager:
    """MongoDB database manager"""
    
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.client = None
        self.db = None
        
        try:
            self.client = MongoClient(connection_url)
            self.db = self.client['student_analytics']
            # Test connection
            self.client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
    
    def create_user(self, username: str, password_hash: str, full_name: str, email: str) -> bool:
        """Create a new user"""
        try:
            if not self.db:
                return False
                
            user_doc = {
                'username': username,
                'password_hash': password_hash,
                'full_name': full_name,
                'email': email,
                'created_at': datetime.now(),
                'last_login': None
            }
            
            self.db.users.insert_one(user_doc)
            return True
        except Exception as e:
            logger.error(f"Error creating user in MongoDB: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            if not self.db:
                return None
                
            user = self.db.users.find_one({'username': username}, {'_id': 0})
            return user
        except Exception as e:
            logger.error(f"Error getting user from MongoDB: {e}")
            return None
    
    def save_results(self, username: str, academic_year: str, semester: str, df: pd.DataFrame) -> bool:
        """Save student results"""
        try:
            if not self.db:
                return False
            
            # Delete existing data
            self.db.student_results.delete_many({
                'username': username,
                'academic_year': academic_year,
                'semester': semester
            })
            
            # Insert new data
            documents = []
            for _, row in df.iterrows():
                doc = {
                    'username': username,
                    'academic_year': academic_year,
                    'semester': semester,
                    'subject': row.get('Subject', ''),
                    'ca_marks': float(row.get('CA_Marks', 0)),
                    'ese_marks': float(row.get('ESE_Marks', 0)),
                    'lab_marks': float(row.get('Lab_Marks', 0)),
                    'total_marks': float(row.get('Total', 0)),
                    'sgpa': float(row.get('SGPA', 0)),
                    'uploaded_at': datetime.now()
                }
                documents.append(doc)
            
            if documents:
                self.db.student_results.insert_many(documents)
            
            return True
        except Exception as e:
            logger.error(f"Error saving results to MongoDB: {e}")
            return False
    
    def get_user_data(self, username: str) -> List[Dict]:
        """Get all data for a user"""
        try:
            if not self.db:
                return []
            
            pipeline = [
                {'$match': {'username': username}},
                {'$sort': {'academic_year': 1, 'semester': 1, 'subject': 1}},
                {'$group': {
                    '_id': {'academic_year': '$academic_year', 'semester': '$semester'},
                    'academic_year': {'$first': '$academic_year'},
                    'semester': {'$first': '$semester'},
                    'uploaded_at': {'$first': '$uploaded_at'},
                    'data': {'$push': {
                        'Subject': '$subject',
                        'CA_Marks': '$ca_marks',
                        'ESE_Marks': '$ese_marks',
                        'Lab_Marks': '$lab_marks',
                        'Total': '$total_marks',
                        'SGPA': '$sgpa'
                    }}
                }}
            ]
            
            results = list(self.db.student_results.aggregate(pipeline))
            
            # Convert to required format
            formatted_results = []
            for result in results:
                semester_data = {
                    'academic_year': result['academic_year'],
                    'semester': result['semester'],
                    'uploaded_at': result['uploaded_at'].isoformat() if result['uploaded_at'] else None,
                    'data': pd.DataFrame(result['data'])
                }
                formatted_results.append(semester_data)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting user data from MongoDB: {e}")
            return []
    
    def clear_user_data(self, username: str) -> bool:
        """Clear all data for a user"""
        try:
            if not self.db:
                return False
            
            self.db.student_results.delete_many({'username': username})
            return True
        except Exception as e:
            logger.error(f"Error clearing user data from MongoDB: {e}")
            return False

class UnifiedDatabaseManager:
    """Unified database manager that supports multiple backends"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.db_type = self.config.get_database_type()
        self.db_manager = None
        
        # Initialize appropriate database manager
        if self.db_type == 'postgres':
            self.db_manager = PostgreSQLManager(self.config.postgres_url)
            logger.info("Using PostgreSQL database")
        elif self.db_type == 'mongodb':
            self.db_manager = MongoDBManager(self.config.mongo_url)
            logger.info("Using MongoDB database")
        else:
            # Use the original JSON-based manager as fallback
            try:
                from db import DatabaseManager as JSONDatabaseManager
                self.db_manager = JSONDatabaseManager()
                logger.info("Using JSON file-based storage")
            except ImportError:
                # If db.py is not available, create a simple fallback
                self.db_manager = self._create_fallback_manager()
                logger.info("Using fallback JSON storage")
    
    def _create_fallback_manager(self):
        """Create a simple fallback manager"""
        class SimpleFallbackManager:
            def __init__(self):
                self.users_file = "users.json"
                self.data_file = "student_data.json"
            
            def create_user(self, username: str, password_hash: str, full_name: str, email: str) -> bool:
                try:
                    users = self._load_json(self.users_file, {})
                    users[username] = {
                        'password_hash': password_hash,
                        'full_name': full_name,
                        'email': email,
                        'created_at': datetime.now().isoformat()
                    }
                    return self._save_json(self.users_file, users)
                except:
                    return False
            
            def get_user(self, username: str) -> Optional[Dict]:
                try:
                    users = self._load_json(self.users_file, {})
                    return users.get(username)
                except:
                    return None
            
            def save_results(self, username: str, academic_year: str, semester: str, df: pd.DataFrame) -> bool:
                return True  # Simplified implementation
            
            def get_user_data(self, username: str) -> List[Dict]:
                return []  # Simplified implementation
            
            def _load_json(self, filename: str, default: Any) -> Any:
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        return json.load(f)
                return default
            
            def _save_json(self, filename: str, data: Any) -> bool:
                try:
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    return True
                except:
                    return False
        
        return SimpleFallbackManager()
    
    def create_user(self, username: str, password_hash: str, full_name: str, email: str) -> bool:
        """Create a new user"""
        return self.db_manager.create_user(username, password_hash, full_name, email)
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.db_manager.get_user(username)
    
    def save_results(self, username: str, academic_year: str, semester: str, df: pd.DataFrame) -> bool:
        """Save student results"""
        return self.db_manager.save_results(username, academic_year, semester, df)
    
    def get_user_data(self, username: str) -> List[Dict]:
        """Get all data for a user"""
        return self.db_manager.get_user_data(username)
    
    def clear_user_data(self, username: str) -> bool:
        """Clear all data for a user"""
        if hasattr(self.db_manager, 'clear_user_data'):
            return self.db_manager.clear_user_data(username)
        return False
    
    def get_database_type(self) -> str:
        """Get current database type"""
        return self.db_type
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and status"""
        info = {
            'type': self.db_type,
            'available_types': []
        }
        
        if POSTGRES_AVAILABLE and self.config.postgres_url:
            info['available_types'].append('postgres')
        if MONGODB_AVAILABLE:
            info['available_types'].append('mongodb')
        info['available_types'].append('json')
        
        return info