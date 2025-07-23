import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64

# Import custom modules
from auth import authenticate_user, create_user, check_user_exists
from database import UnifiedDatabaseManager
from utils import parse_csv_file, parse_pdf_file, validate_file_format
from analytics import PerformanceAnalytics
from visualizations import create_charts
from ml_models import MLAnalytics

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = UnifiedDatabaseManager()

def main():
    st.set_page_config(
        page_title="Student Result Analytics Platform",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Student Result Analytics Platform")
    
    # Authentication check
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    """Display authentication page with login and signup options"""
    st.sidebar.title("Authentication")
    auth_choice = st.sidebar.selectbox("Choose an option", ["Login", "Sign Up"])
    
    if auth_choice == "Login":
        st.subheader("🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    else:  # Sign Up
        st.subheader("📝 Create Account")
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            submit_button = st.form_submit_button("Create Account")
            
            if submit_button:
                if not all([new_username, new_password, confirm_password, full_name, email]):
                    st.error("All fields are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif check_user_exists(new_username):
                    st.error("Username already exists")
                else:
                    if create_user(new_username, new_password, full_name, email):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Failed to create account")

def show_main_app():
    """Display the main application interface"""
    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📁 Upload Data", 
        "📊 Dashboard", 
        "📈 Analytics", 
        "🤖 ML Insights", 
        "📄 Reports", 
        "📚 History",
        "🗄️ Database",
        "📦 Download"
    ])
    
    with tab1:
        show_upload_tab()
    
    with tab2:
        show_dashboard_tab()
    
    with tab3:
        show_analytics_tab()
    
    with tab4:
        show_ml_tab()
    
    with tab5:
        show_reports_tab()
    
    with tab6:
        show_history_tab()
    
    with tab7:
        show_database_tab()
    
    with tab8:
        show_download_tab()

def show_upload_tab():
    """Handle file upload and data parsing"""
    st.header("📁 Upload Student Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Academic year and semester selection
        academic_year = st.selectbox(
            "Select Academic Year",
            ["2023-24", "2024-25", "2025-26", "2026-27"]
        )
        
        semester = st.selectbox(
            "Select Semester",
            ["Semester 1", "Semester 2", "Semester 3", "Semester 4", 
             "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Result File",
            type=['csv', 'pdf'],
            help="Upload CSV or PDF files containing student results"
        )
        
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            try:
                df = None
                if file_type == 'csv':
                    df = parse_csv_file(uploaded_file)
                elif file_type == 'pdf':
                    df = parse_pdf_file(uploaded_file)
                
                if df is not None and not df.empty:
                    st.success("File uploaded and parsed successfully!")
                    st.dataframe(df.head())
                    
                    if st.button("Save to Database"):
                        success = st.session_state.db_manager.save_results(
                            st.session_state.username,
                            academic_year,
                            semester,
                            df
                        )
                        
                        if success:
                            st.success("Data saved successfully!")
                        else:
                            st.error("Failed to save data")
                else:
                    st.error("Could not parse the uploaded file")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.info("""
        **File Format Requirements:**
        
        **CSV Format:**
        - Subject
        - CA_Marks
        - ESE_Marks
        - Lab_Marks
        - Total
        - SGPA
        
        **PDF Format:**
        - Standard marksheet format
        - Clear text (not scanned images)
        """)

def show_dashboard_tab():
    """Display main dashboard with key metrics"""
    st.header("📊 Performance Dashboard")
    
    # Get user data
    user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
    
    if not user_data:
        st.info("No data available. Please upload some results first.")
        return
    
    analytics = PerformanceAnalytics(user_data)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_sgpa = analytics.get_average_sgpa()
        st.metric("Average SGPA", f"{avg_sgpa:.2f}")
    
    with col2:
        total_subjects = analytics.get_total_subjects()
        st.metric("Total Subjects", total_subjects)
    
    with col3:
        best_semester = analytics.get_best_semester()
        st.metric("Best Semester", best_semester)
    
    with col4:
        cgpa = analytics.calculate_cgpa()
        st.metric("Current CGPA", f"{cgpa:.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SGPA Trend")
        sgpa_chart = create_charts.create_sgpa_trend(user_data)
        st.plotly_chart(sgpa_chart, use_container_width=True)
    
    with col2:
        st.subheader("Subject-wise Performance")
        subject_chart = create_charts.create_subject_performance(user_data)
        st.plotly_chart(subject_chart, use_container_width=True)

def show_analytics_tab():
    """Display detailed analytics and visualizations"""
    st.header("📈 Advanced Analytics")
    
    user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
    
    if not user_data:
        st.info("No data available. Please upload some results first.")
        return
    
    analytics = PerformanceAnalytics(user_data)
    
    # Analytics options
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Subject Performance", "Semester Comparison", "Mark Distribution", "Performance Categories"]
    )
    
    if analysis_type == "Subject Performance":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Average Marks by Subject")
            subject_avg_chart = create_charts.create_subject_average_chart(user_data)
            st.plotly_chart(subject_avg_chart, use_container_width=True)
        
        with col2:
            st.subheader("CA vs ESE Performance")
            scatter_chart = create_charts.create_ca_ese_scatter(user_data)
            st.plotly_chart(scatter_chart, use_container_width=True)
    
    elif analysis_type == "Semester Comparison":
        st.subheader("Semester-wise SGPA Comparison")
        semester_chart = create_charts.create_semester_comparison(user_data)
        st.plotly_chart(semester_chart, use_container_width=True)
        
        # Highlight best and worst semesters
        best_sem, worst_sem = analytics.get_best_worst_semesters()
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🏆 Best Semester: {best_sem}")
        with col2:
            st.error(f"📉 Needs Improvement: {worst_sem}")
    
    elif analysis_type == "Mark Distribution":
        st.subheader("Mark Distribution Analysis")
        hist_chart = create_charts.create_marks_histogram(user_data)
        st.plotly_chart(hist_chart, use_container_width=True)
        
        # Statistical summary
        stats_df = analytics.get_statistical_summary()
        st.dataframe(stats_df)
    
    elif analysis_type == "Performance Categories":
        st.subheader("Performance Category Distribution")
        pie_chart = create_charts.create_performance_pie_chart(user_data)
        st.plotly_chart(pie_chart, use_container_width=True)

def show_ml_tab():
    """Display machine learning insights"""
    st.header("🤖 Machine Learning Insights")
    
    user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
    
    if not user_data:
        st.info("No data available. Please upload some results first.")
        return
    
    ml_analytics = MLAnalytics(user_data)
    
    ml_option = st.selectbox(
        "Select ML Analysis",
        ["Subject Clustering", "SGPA Prediction", "Performance Analysis"]
    )
    
    if ml_option == "Subject Clustering":
        st.subheader("Subject Clustering Analysis")
        
        try:
            cluster_chart, cluster_info = ml_analytics.perform_clustering()
            st.plotly_chart(cluster_chart, use_container_width=True)
            st.write("**Cluster Analysis:**")
            st.write(cluster_info)
        except Exception as e:
            st.error(f"Clustering analysis requires more data: {str(e)}")
    
    elif ml_option == "SGPA Prediction":
        st.subheader("Future SGPA Prediction")
        
        try:
            prediction_chart, next_sgpa = ml_analytics.predict_sgpa()
            st.plotly_chart(prediction_chart, use_container_width=True)
            st.success(f"Predicted Next Semester SGPA: {next_sgpa:.2f}")
        except Exception as e:
            st.error(f"Prediction requires more historical data: {str(e)}")
    
    elif ml_option == "Performance Analysis":
        st.subheader("PCA Analysis")
        
        try:
            pca_chart = ml_analytics.perform_pca_analysis()
            st.plotly_chart(pca_chart, use_container_width=True)
            st.info("PCA helps identify the main factors affecting your performance.")
        except Exception as e:
            st.error(f"PCA analysis requires more data: {str(e)}")

def show_reports_tab():
    """Generate and download reports"""
    st.header("📄 Generate Reports")
    
    user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
    
    if not user_data:
        st.info("No data available. Please upload some results first.")
        return
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Academic Summary", "Semester Report", "Subject Analysis", "Complete Transcript"]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Generate Report"):
            try:
                from utils import generate_pdf_report
                
                pdf_buffer = generate_pdf_report(
                    user_data, 
                    st.session_state.username, 
                    report_type
                )
                
                st.success("Report generated successfully!")
                
                # Download button
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{report_type.replace(' ', '_')}_report.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    with col2:
        st.info("""
        **Report Contents:**
        - Academic performance summary
        - Semester-wise breakdown
        - Subject analysis
        - Trend visualizations
        - Recommendations
        """)

def show_history_tab():
    """Display historical data and trends"""
    st.header("📚 Academic History")
    
    user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
    
    if not user_data:
        st.info("No data available. Please upload some results first.")
        return
    
    # Data management
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("All Academic Records")
        
        # Create a comprehensive dataframe
        all_records = []
        for record in user_data:
            for _, row in record['data'].iterrows():
                all_records.append({
                    'Academic Year': record['academic_year'],
                    'Semester': record['semester'],
                    'Subject': row['Subject'],
                    'CA Marks': row.get('CA_Marks', 0),
                    'ESE Marks': row.get('ESE_Marks', 0),
                    'Lab Marks': row.get('Lab_Marks', 0),
                    'Total': row.get('Total', 0),
                    'SGPA': row.get('SGPA', 0)
                })
        
        if all_records:
            history_df = pd.DataFrame(all_records)
            st.dataframe(history_df, use_container_width=True)
            
            # Export data
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="Download Complete Data (CSV)",
                data=csv,
                file_name="academic_history.csv",
                mime="text/csv"
            )
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("Clear All Data"):
            if st.checkbox("I confirm to delete all data"):
                st.session_state.db_manager.clear_user_data(st.session_state.username)
                st.success("All data cleared!")
                st.rerun()
        
        st.subheader("Data Statistics")
        st.metric("Total Records", len(user_data))
        if all_records:
            st.metric("Total Subjects", len(set([r['Subject'] for r in all_records])))
            st.metric("Semesters Completed", len(set([r['Semester'] for r in all_records])))

def show_database_tab():
    """Display database information and configuration"""
    st.header("🗄️ Database Configuration")
    
    # Get database information
    db_info = st.session_state.db_manager.get_database_info()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Database Status")
        
        # Current database type
        db_type = db_info['type']
        st.metric("Active Database", db_type.upper())
        
        # Database type descriptions
        db_descriptions = {
            'postgres': {
                'name': 'PostgreSQL',
                'description': 'Production-ready relational database with full SQL support',
                'features': ['ACID compliance', 'Concurrent access', 'Advanced querying', 'Data integrity'],
                'status': '🟢 Connected' if db_type == 'postgres' else '🔴 Not configured'
            },
            'mongodb': {
                'name': 'MongoDB', 
                'description': 'NoSQL document database for flexible data storage',
                'features': ['Document storage', 'Flexible schema', 'Horizontal scaling', 'JSON-like documents'],
                'status': '🟢 Connected' if db_type == 'mongodb' else '🔴 Not configured'
            },
            'json': {
                'name': 'JSON Files',
                'description': 'Simple file-based storage for development and testing',
                'features': ['No setup required', 'Portable', 'Easy debugging', 'Local storage'],
                'status': '🟢 Active' if db_type == 'json' else '🔴 Inactive'
            }
        }
        
        # Show current database info
        current_db = db_descriptions[db_type]
        st.success(f"**{current_db['name']}** - {current_db['status']}")
        st.write(current_db['description'])
        
        # Features
        st.write("**Features:**")
        for feature in current_db['features']:
            st.write(f"• {feature}")
        
        # Available database types
        st.subheader("Available Database Options")
        
        for db_name, info in db_descriptions.items():
            if db_name in db_info['available_types']:
                status_icon = "🟢" if db_name == db_type else "⚪"
                st.write(f"{status_icon} **{info['name']}** - {info['description']}")
            else:
                st.write(f"🔴 **{info['name']}** - Not available")
    
    with col2:
        st.subheader("Database Statistics")
        
        try:
            # Get some basic stats
            user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
            
            total_semesters = len(user_data)
            total_subjects = 0
            total_records = 0
            
            for record in user_data:
                total_subjects += len(record['data'])
                total_records += len(record['data'])
            
            st.metric("Your Semesters", total_semesters)
            st.metric("Your Subjects", len(set([row['Subject'] for record in user_data for _, row in record['data'].iterrows()])) if user_data else 0)
            st.metric("Total Records", total_records)
            
        except Exception as e:
            st.error(f"Error getting database statistics: {e}")
        
        # Database configuration info
        st.subheader("Configuration")
        
        if db_type == 'postgres':
            st.info("""
            **PostgreSQL Configuration:**
            - Uses environment variable DATABASE_URL
            - Supports concurrent users
            - ACID transaction support
            - SQL queries and joins
            """)
        elif db_type == 'mongodb':
            st.info("""
            **MongoDB Configuration:**
            - Uses MONGODB_URL environment variable
            - Document-based storage
            - Flexible data schema
            - Aggregation pipelines
            """)
        else:
            st.info("""
            **JSON File Storage:**
            - Local file: student_data.json
            - Local file: users.json
            - No external dependencies
            - Easy backup and restore
            """)
    
    # Database operations
    st.subheader("Database Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Test Connection"):
            try:
                # Test database connection
                test_result = st.session_state.db_manager.get_database_info()
                st.success(f"✅ Database connection successful!\nType: {test_result['type'].upper()}")
            except Exception as e:
                st.error(f"❌ Database connection failed: {e}")
    
    with col2:
        if st.button("View Data Summary"):
            try:
                user_data = st.session_state.db_manager.get_user_data(st.session_state.username)
                if user_data:
                    st.json({
                        'total_semesters': len(user_data),
                        'semesters': [f"{r['academic_year']} - {r['semester']}" for r in user_data],
                        'database_type': db_type
                    })
                else:
                    st.info("No data found for current user")
            except Exception as e:
                st.error(f"Error retrieving data summary: {e}")
    
    with col3:
        if st.button("Database Info"):
            st.json(db_info)
    
    # Tips and recommendations
    st.subheader("💡 Database Recommendations")
    
    if db_type == 'json':
        st.warning("""
        **Current Setup: File-based Storage**
        
        You're using JSON file storage which is great for:
        - Development and testing
        - Single user applications
        - Simple data backup
        
        Consider upgrading to PostgreSQL for:
        - Multiple users
        - Better performance
        - Data integrity
        - Production deployment
        """)
    elif db_type == 'postgres':
        st.success("""
        **Excellent Choice: PostgreSQL**
        
        You're using a production-ready database with:
        - ACID compliance
        - Concurrent user support
        - Advanced query capabilities
        - Excellent performance
        """)
    elif db_type == 'mongodb':
        st.success("""
        **Great Choice: MongoDB**
        
        You're using a flexible NoSQL database with:
        - Document-based storage
        - Flexible schema
        - Horizontal scaling
        - JSON-native operations
        """)

def show_download_tab():
    """Display download interface for the project"""
    st.header("📦 Download Project")
    
    st.markdown("""
    Download your complete Student Result Analytics Platform with all features and documentation.
    """)
    
    # Project info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Project Size", "105 KB")
    
    with col2:
        st.metric("Files Included", "18")
    
    with col3:
        st.metric("Version", "1.0.0")
    
    # What's included
    st.subheader("📋 What's Included")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Core Application:**
        - `app.py` - Main Streamlit application
        - `database.py` - Multi-database support
        - `auth.py` - Authentication system
        - `utils.py` - File processing & PDF reports
        - `analytics.py` - Performance analytics
        - `visualizations.py` - Interactive charts
        - `ml_models.py` - Machine learning features
        """)
    
    with col2:
        st.markdown("""
        **Documentation & Setup:**
        - `README.md` - Complete documentation
        - `setup_instructions.md` - GitHub guide
        - `CONTRIBUTING.md` - Contribution guidelines
        - `LICENSE` - MIT license
        - `.gitignore` - Git configuration
        - `dependencies.txt` - Required packages
        - Configuration files
        """)
    
    # Features
    st.subheader("🎯 Features")
    features = [
        "Secure user authentication with password hashing",
        "File upload support (CSV and PDF)",
        "Interactive analytics dashboard with multiple chart types",
        "Machine learning insights (clustering, predictions, PCA)",
        "Multi-database support (PostgreSQL, MongoDB, JSON)",
        "PDF report generation",
        "Professional documentation and setup guides"
    ]
    
    for feature in features:
        st.write(f"✅ {feature}")
    
    # Download section
    st.subheader("📥 Download")
    
    # Check if zip file exists
    zip_file = "student-analytics-platform.zip"
    if os.path.exists(zip_file):
        file_size = os.path.getsize(zip_file)
        
        with open(zip_file, "rb") as file:
            st.download_button(
                label="📦 Download student-analytics-platform.zip",
                data=file.read(),
                file_name=zip_file,
                mime="application/zip",
                help="Download the complete project as a zip file"
            )
        
        st.success(f"✅ Zip file ready! Size: {file_size / 1024:.1f} KB")
        
        # Quick setup instructions
        with st.expander("🚀 Quick Setup Instructions"):
            st.markdown("""
            1. **Extract** the zip file to your desired location
            2. **Install Python 3.11+** if not already installed
            3. **Install dependencies:**
               ```bash
               pip install streamlit pandas numpy plotly scikit-learn pdfplumber reportlab psycopg2-binary pymongo sqlalchemy
               ```
            4. **Run the application:**
               ```bash
               streamlit run app.py
               ```
            5. **Access** your app at `http://localhost:8501`
            
            **For GitHub Upload:**
            - See `setup_instructions.md` for detailed GitHub upload guide
            - All sensitive files are excluded from the zip
            - Professional documentation included
            """)
    else:
        st.error("❌ Zip file not found. Please create it first.")
        if st.button("🔧 Create Zip File"):
            try:
                # Import and run zip creation
                import subprocess
                result = subprocess.run(["python3", "create_zip.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Zip file created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error creating zip: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
