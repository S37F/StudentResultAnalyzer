import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64

# Import custom modules
from auth import authenticate_user, create_user, check_user_exists
from db import DatabaseManager
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
    st.session_state.db_manager = DatabaseManager()

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📁 Upload Data", 
        "📊 Dashboard", 
        "📈 Analytics", 
        "🤖 ML Insights", 
        "📄 Reports", 
        "📚 History"
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

if __name__ == "__main__":
    main()
