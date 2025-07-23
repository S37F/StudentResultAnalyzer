import json
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """In-memory database manager for student results"""
    
    def __init__(self):
        self.data_file = "student_data.json"
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load data from JSON file"""
        if not os.path.exists(self.data_file):
            return {}
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Convert string data back to DataFrames
                for username in data:
                    for record in data[username]:
                        if 'data' in record and isinstance(record['data'], dict):
                            record['data'] = pd.DataFrame(record['data'])
                return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self) -> bool:
        """Save data to JSON file"""
        try:
            # Convert DataFrames to dict for JSON serialization
            serializable_data = {}
            for username in self.data:
                serializable_data[username] = []
                for record in self.data[username]:
                    serialized_record = record.copy()
                    if 'data' in record and isinstance(record['data'], pd.DataFrame):
                        serialized_record['data'] = record['data'].to_dict('records')
                    serializable_data[username].append(serialized_record)
            
            with open(self.data_file, 'w') as f:
                json.dump(serializable_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def save_results(self, username: str, academic_year: str, semester: str, df: pd.DataFrame) -> bool:
        """Save student results to database"""
        try:
            if username not in self.data:
                self.data[username] = []
            
            # Check if record already exists
            existing_record = None
            for i, record in enumerate(self.data[username]):
                if record['academic_year'] == academic_year and record['semester'] == semester:
                    existing_record = i
                    break
            
            # Create new record
            new_record = {
                'academic_year': academic_year,
                'semester': semester,
                'data': df,
                'uploaded_at': datetime.now().isoformat()
            }
            
            if existing_record is not None:
                # Update existing record
                self.data[username][existing_record] = new_record
            else:
                # Add new record
                self.data[username].append(new_record)
            
            return self.save_data()
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
    
    def get_user_data(self, username: str) -> List[Dict]:
        """Get all data for a specific user"""
        return self.data.get(username, [])
    
    def get_semester_data(self, username: str, academic_year: str, semester: str) -> Optional[pd.DataFrame]:
        """Get data for a specific semester"""
        user_data = self.get_user_data(username)
        
        for record in user_data:
            if record['academic_year'] == academic_year and record['semester'] == semester:
                return record['data']
        
        return None
    
    def get_all_semesters(self, username: str) -> List[Dict]:
        """Get list of all semesters for a user"""
        user_data = self.get_user_data(username)
        semesters = []
        
        for record in user_data:
            semesters.append({
                'academic_year': record['academic_year'],
                'semester': record['semester'],
                'uploaded_at': record['uploaded_at']
            })
        
        return sorted(semesters, key=lambda x: (x['academic_year'], x['semester']))
    
    def delete_semester_data(self, username: str, academic_year: str, semester: str) -> bool:
        """Delete data for a specific semester"""
        try:
            if username not in self.data:
                return False
            
            self.data[username] = [
                record for record in self.data[username]
                if not (record['academic_year'] == academic_year and record['semester'] == semester)
            ]
            
            return self.save_data()
            
        except Exception as e:
            print(f"Error deleting semester data: {e}")
            return False
    
    def clear_user_data(self, username: str) -> bool:
        """Clear all data for a user"""
        try:
            if username in self.data:
                self.data[username] = []
                return self.save_data()
            return True
            
        except Exception as e:
            print(f"Error clearing user data: {e}")
            return False
    
    def get_subject_list(self, username: str) -> List[str]:
        """Get unique list of subjects for a user"""
        user_data = self.get_user_data(username)
        subjects = set()
        
        for record in user_data:
            if 'Subject' in record['data'].columns:
                subjects.update(record['data']['Subject'].tolist())
        
        return sorted(list(subjects))
    
    def backup_data(self, backup_file: str) -> bool:
        """Create backup of all data"""
        try:
            import shutil
            shutil.copy2(self.data_file, backup_file)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_data(self, backup_file: str) -> bool:
        """Restore data from backup"""
        try:
            import shutil
            shutil.copy2(backup_file, self.data_file)
            self.data = self.load_data()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
