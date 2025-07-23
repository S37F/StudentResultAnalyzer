#!/usr/bin/env python3
"""
Create a zip file of the Student Analytics Platform project
"""
import os
import zipfile
from pathlib import Path

def create_project_zip():
    """Create a zip file of the project"""
    
    # Define the zip file name
    zip_filename = "student-analytics-platform.zip"
    
    # Files to include
    files_to_include = [
        'app.py',
        'auth.py', 
        'database.py',
        'db.py',
        'utils.py',
        'analytics.py',
        'visualizations.py',
        'ml_models.py',
        '.streamlit/config.toml',
        'pyproject.toml',
        'uv.lock',
        'README.md',
        'LICENSE',
        'CONTRIBUTING.md',
        '.gitignore',
        'dependencies.txt',
        'setup_instructions.md',
        'replit.md'
    ]
    
    # Files to exclude (sensitive or temporary)
    exclude_patterns = [
        'users.json',
        'student_data.json',
        '*.pyc',
        '__pycache__',
        '*.log',
        '*.tmp',
        '.git',
        'create_zip.py'
    ]
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            if os.path.exists(file_path):
                # Add file to zip maintaining directory structure
                zipf.write(file_path, file_path)
                print(f"Added: {file_path}")
            else:
                print(f"File not found: {file_path}")
    
    print(f"\nZip file created: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    return zip_filename

if __name__ == "__main__":
    create_project_zip()