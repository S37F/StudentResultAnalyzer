#!/usr/bin/env python3
"""
Simple download server for the zip file
"""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

class DownloadHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/download':
            zip_file = 'student-analytics-platform.zip'
            if os.path.exists(zip_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename="{zip_file}"')
                self.send_header('Content-Length', str(os.path.getsize(zip_file)))
                self.end_headers()
                
                with open(zip_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'Zip file not found')
        else:
            # Serve a simple HTML page
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Student Analytics Platform - Download</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .download-btn { background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; font-size: 18px; }
                    .download-btn:hover { background: #0056b3; }
                    .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .file-list { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Student Analytics Platform</h1>
                    <p>Your complete Student Result Analytics Platform is ready for download!</p>
                    
                    <a href="/download" class="download-btn">📦 Download student-analytics-platform.zip</a>
                    
                    <div class="info">
                        <h3>📋 What's included:</h3>
                        <ul>
                            <li>Complete Streamlit web application</li>
                            <li>Database integration (PostgreSQL, MongoDB, JSON)</li>
                            <li>Authentication system</li>
                            <li>File upload and processing (CSV/PDF)</li>
                            <li>Interactive analytics dashboard</li>
                            <li>Machine learning insights</li>
                            <li>PDF report generation</li>
                            <li>Professional documentation</li>
                        </ul>
                    </div>
                    
                    <div class="file-list">
                        <strong>Core Files:</strong><br>
                        app.py - Main application<br>
                        database.py - Multi-database support<br>
                        auth.py - Authentication system<br>
                        utils.py - File processing<br>
                        analytics.py - Performance analytics<br>
                        visualizations.py - Charts and graphs<br>
                        ml_models.py - Machine learning<br>
                        README.md - Complete documentation<br>
                        + Configuration and setup files
                    </div>
                    
                    <div class="info">
                        <h3>🚀 Quick Setup:</h3>
                        <ol>
                            <li>Extract the zip file</li>
                            <li>Install dependencies: <code>pip install streamlit pandas numpy plotly scikit-learn pdfplumber reportlab psycopg2-binary pymongo sqlalchemy</code></li>
                            <li>Run: <code>streamlit run app.py</code></li>
                        </ol>
                    </div>
                    
                    <p><small>File size: 105 KB | Created: July 23, 2025</small></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(('0.0.0.0', port), DownloadHandler)
    print(f"Download server starting on port {port}")
    print(f"Access: http://0.0.0.0:{port}")
    print(f"Direct download: http://0.0.0.0:{port}/download")
    server.serve_forever()