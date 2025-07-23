import pandas as pd
import pdfplumber
import re
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import streamlit as st

def parse_csv_file(uploaded_file):
    """Parse CSV file and return DataFrame"""
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_columns = ['Subject']
        optional_columns = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total', 'SGPA']
        
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV must contain at least these columns: {required_columns}")
            return None
        
        # Clean and standardize column names
        df.columns = df.columns.str.strip()
        
        # Handle missing optional columns
        for col in optional_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Convert numeric columns
        numeric_columns = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total', 'SGPA']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Remove rows with empty subjects
        df = df.dropna(subset=['Subject'])
        df = df[df['Subject'].str.strip() != '']
        
        return df
        
    except Exception as e:
        st.error(f"Error parsing CSV file: {str(e)}")
        return None

def parse_pdf_file(uploaded_file):
    """Parse PDF file and extract student result data"""
    try:
        # Read PDF content
        pdf_content = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                pdf_content += page.extract_text() + "\n"
        
        if not pdf_content.strip():
            st.error("Could not extract text from PDF. Please ensure it's not a scanned image.")
            return None
        
        # Parse the extracted text to create DataFrame
        df = extract_results_from_text(pdf_content)
        return df
        
    except Exception as e:
        st.error(f"Error parsing PDF file: {str(e)}")
        return None

def extract_results_from_text(text):
    """Extract student results from text content"""
    try:
        lines = text.split('\n')
        results = []
        
        # Common patterns for different marksheet formats
        patterns = [
            # Pattern 1: Subject | CA | ESE | Lab | Total | SGPA
            r'([A-Za-z\s]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.?\d*)',
            # Pattern 2: Subject CA ESE Lab Total
            r'([A-Za-z\s]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
            # Pattern 3: Subject marks format
            r'([A-Za-z\s]+).*?(\d+).*?(\d+).*?(\d+).*?(\d+)'
        ]
        
        # Look for SGPA pattern
        sgpa_pattern = r'SGPA[:\s]*(\d+\.?\d*)'
        semester_sgpa = 0
        
        sgpa_match = re.search(sgpa_pattern, text, re.IGNORECASE)
        if sgpa_match:
            semester_sgpa = float(sgpa_match.group(1))
        
        # Try to extract subject-wise data
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    
                    if len(groups) >= 4:
                        subject = groups[0].strip()
                        # Skip header lines
                        if any(word in subject.lower() for word in ['subject', 'course', 'marks', 'total', 'sgpa']):
                            continue
                        
                        # Extract marks
                        ca_marks = int(groups[1]) if groups[1].isdigit() else 0
                        ese_marks = int(groups[2]) if groups[2].isdigit() else 0
                        lab_marks = int(groups[3]) if groups[3].isdigit() else 0
                        total_marks = int(groups[4]) if len(groups) > 4 and groups[4].isdigit() else ca_marks + ese_marks + lab_marks
                        
                        subject_sgpa = float(groups[5]) if len(groups) > 5 and groups[5].replace('.', '').isdigit() else semester_sgpa
                        
                        results.append({
                            'Subject': subject,
                            'CA_Marks': ca_marks,
                            'ESE_Marks': ese_marks,
                            'Lab_Marks': lab_marks,
                            'Total': total_marks,
                            'SGPA': subject_sgpa
                        })
                        break
        
        if not results:
            # Fallback: Create sample structure if no pattern matches
            st.warning("Could not parse PDF automatically. Please check the format and try again.")
            return None
        
        df = pd.DataFrame(results)
        return df
        
    except Exception as e:
        st.error(f"Error extracting results from text: {str(e)}")
        return None

def validate_file_format(file_path, file_type):
    """Validate uploaded file format"""
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
            required_columns = ['Subject']
            return all(col in df.columns for col in required_columns)
        
        elif file_type == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages[:2]:  # Check first 2 pages
                    text += page.extract_text()
                return len(text.strip()) > 0
        
        return False
        
    except Exception:
        return False

def generate_pdf_report(user_data, username, report_type):
    """Generate PDF report using reportlab"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        story.append(Paragraph(f"Student Performance Report - {report_type}", title_style))
        story.append(Spacer(1, 12))
        
        # Student info
        story.append(Paragraph(f"<b>Student:</b> {username}", styles['Normal']))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if report_type == "Academic Summary":
            generate_academic_summary(story, user_data, styles)
        elif report_type == "Semester Report":
            generate_semester_report(story, user_data, styles)
        elif report_type == "Subject Analysis":
            generate_subject_analysis(story, user_data, styles)
        elif report_type == "Complete Transcript":
            generate_complete_transcript(story, user_data, styles)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Error generating PDF report: {str(e)}")
        return None

def generate_academic_summary(story, user_data, styles):
    """Generate academic summary section"""
    story.append(Paragraph("<b>Academic Performance Summary</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Calculate overall statistics
    all_sgpa = []
    total_subjects = 0
    
    for record in user_data:
        if 'SGPA' in record['data'].columns:
            sgpa_values = record['data']['SGPA'].dropna()
            if len(sgpa_values) > 0:
                semester_sgpa = sgpa_values.iloc[0]  # Take first SGPA value
                all_sgpa.append(semester_sgpa)
        total_subjects += len(record['data'])
    
    if all_sgpa:
        avg_sgpa = sum(all_sgpa) / len(all_sgpa)
        cgpa = avg_sgpa  # Simplified CGPA calculation
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Semesters', str(len(user_data))],
            ['Total Subjects Completed', str(total_subjects)],
            ['Average SGPA', f"{avg_sgpa:.2f}"],
            ['Current CGPA', f"{cgpa:.2f}"],
            ['Highest SGPA', f"{max(all_sgpa):.2f}"],
            ['Lowest SGPA', f"{min(all_sgpa):.2f}"]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)

def generate_semester_report(story, user_data, styles):
    """Generate semester-wise report"""
    story.append(Paragraph("<b>Semester-wise Performance</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    for record in user_data:
        story.append(Paragraph(f"<b>{record['academic_year']} - {record['semester']}</b>", styles['Heading3']))
        
        # Create semester data table
        df = record['data']
        table_data = [list(df.columns)]
        
        for _, row in df.iterrows():
            table_data.append([str(row[col]) for col in df.columns])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))

def generate_subject_analysis(story, user_data, styles):
    """Generate subject-wise analysis"""
    story.append(Paragraph("<b>Subject-wise Performance Analysis</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Aggregate subject data
    subject_data = {}
    
    for record in user_data:
        df = record['data']
        for _, row in df.iterrows():
            subject = row['Subject']
            if subject not in subject_data:
                subject_data[subject] = []
            
            subject_data[subject].append({
                'semester': record['semester'],
                'ca_marks': row.get('CA_Marks', 0),
                'ese_marks': row.get('ESE_Marks', 0),
                'total': row.get('Total', 0)
            })
    
    # Create analysis table
    analysis_data = [['Subject', 'Avg CA', 'Avg ESE', 'Avg Total', 'Best Performance']]
    
    for subject, performances in subject_data.items():
        avg_ca = sum(p['ca_marks'] for p in performances) / len(performances)
        avg_ese = sum(p['ese_marks'] for p in performances) / len(performances)
        avg_total = sum(p['total'] for p in performances) / len(performances)
        best_total = max(p['total'] for p in performances)
        
        analysis_data.append([
            subject,
            f"{avg_ca:.1f}",
            f"{avg_ese:.1f}",
            f"{avg_total:.1f}",
            f"{best_total}"
        ])
    
    table = Table(analysis_data, colWidths=[2.5*inch, inch, inch, inch, inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)

def generate_complete_transcript(story, user_data, styles):
    """Generate complete academic transcript"""
    story.append(Paragraph("<b>Complete Academic Transcript</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    for record in user_data:
        # Semester header
        story.append(Paragraph(f"<b>{record['academic_year']} - {record['semester']}</b>", styles['Heading3']))
        
        # Subject details
        df = record['data']
        for _, row in df.iterrows():
            subject_info = f"<b>{row['Subject']}</b> - CA: {row.get('CA_Marks', 0)}, ESE: {row.get('ESE_Marks', 0)}, Lab: {row.get('Lab_Marks', 0)}, Total: {row.get('Total', 0)}"
            story.append(Paragraph(subject_info, styles['Normal']))
        
        # Semester SGPA
        if 'SGPA' in df.columns and not df['SGPA'].empty:
            sgpa = df['SGPA'].iloc[0]
            story.append(Paragraph(f"<b>Semester SGPA: {sgpa}</b>", styles['Normal']))
        
        story.append(Spacer(1, 15))

def calculate_cgpa(user_data):
    """Calculate CGPA from all semester data"""
    try:
        all_sgpa = []
        
        for record in user_data:
            if 'SGPA' in record['data'].columns:
                sgpa_values = record['data']['SGPA'].dropna()
                if len(sgpa_values) > 0:
                    # Take the first non-zero SGPA value
                    semester_sgpa = sgpa_values[sgpa_values > 0].iloc[0] if any(sgpa_values > 0) else 0
                    if semester_sgpa > 0:
                        all_sgpa.append(semester_sgpa)
        
        if all_sgpa:
            return sum(all_sgpa) / len(all_sgpa)
        return 0.0
        
    except Exception:
        return 0.0
