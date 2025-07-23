# Student Result Analytics Platform

A comprehensive web-based analytics platform for students to upload, analyze, and visualize their academic performance data. Built with Streamlit and featuring advanced analytics including machine learning insights.

## 🚀 Features

### 🔐 Authentication System
- Secure user registration and login
- Password hashing using SHA256
- Session-based user management

### 📁 Data Management
- **File Upload Support**: CSV and PDF format support
- **PDF Text Extraction**: Uses pdfplumber for text extraction from PDF marksheets
- **Data Validation**: Automatic validation and cleaning of uploaded data
- **Persistent Storage**: JSON-based data storage with user isolation

### 📊 Analytics Dashboard
- **Performance Metrics**: Average SGPA, CGPA calculation, total subjects
- **SGPA Trends**: Interactive line charts showing semester-wise progress
- **Subject Analysis**: Bar charts for subject-wise performance comparison
- **Statistical Summary**: Comprehensive statistics for all performance metrics

### 📈 Advanced Analytics
- **Histogram Analysis**: Mark distribution patterns
- **Performance Categories**: High/Medium/Low performance classification
- **CA vs ESE Correlation**: Scatter plots with regression analysis
- **Semester Comparison**: Best and worst semester identification

### 🤖 Machine Learning Insights
- **K-means Clustering**: Subject performance grouping
- **PCA Analysis**: Principal component analysis for performance factors
- **SGPA Prediction**: Linear regression-based future performance prediction
- **Pattern Recognition**: Automated performance pattern analysis

### 📄 Report Generation
- **PDF Reports**: Professional academic reports using ReportLab
- **Multiple Report Types**: Academic summary, semester reports, subject analysis
- **Export Functionality**: CSV export for complete academic history
- **Download Features**: One-click report and data downloads

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Data Processing
- **PDFplumber**: PDF text extraction
- **JSON**: Data persistence and user management
- **Hashlib**: Secure password hashing

### Visualization
- **Plotly**: Interactive charts and graphs
- **Matplotlib**: Statistical visualizations

### Machine Learning
- **Scikit-learn**: ML algorithms and preprocessing
- **K-means Clustering**: Performance grouping
- **Linear Regression**: SGPA prediction
- **PCA**: Dimensionality reduction

### Report Generation
- **ReportLab**: PDF generation
- **Custom Templates**: Professional report layouts

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/student-analytics-platform.git
   cd student-analytics-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`

## 📊 Expected Data Format

### CSV Format
Your CSV files should contain these columns:
- `Subject`: Subject name
- `CA_Marks`: Continuous Assessment marks
- `ESE_Marks`: End Semester Examination marks
- `Lab_Marks`: Laboratory marks
- `Total`: Total marks
- `SGPA`: Semester Grade Point Average

### PDF Format
- Standard university marksheet format
- Clear text (not scanned images)
- Contains subject names and corresponding marks

## 🎯 Usage

1. **Create Account**: Register with username, password, full name, and email
2. **Login**: Access your personal dashboard
3. **Upload Data**: Upload your semester results in CSV or PDF format
4. **View Analytics**: Explore various analytics and visualizations
5. **Generate Reports**: Create and download professional PDF reports
6. **ML Insights**: Get machine learning-powered insights and predictions

## 📁 Project Structure

```
student-analytics-platform/
│
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication system
├── db.py                 # Database management
├── utils.py              # Utility functions
├── analytics.py          # Performance analytics engine
├── visualizations.py     # Chart creation functions
├── ml_models.py          # Machine learning analytics
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── config.toml      # Streamlit configuration
└── README.md            # Project documentation
```

## 🔧 Configuration

The application uses Streamlit's configuration system. Key settings are in `.streamlit/config.toml`:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "light"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/student-analytics-platform/issues) page
2. Create a new issue with detailed description
3. Include screenshots if applicable

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time data synchronization
- [ ] Mobile responsive design
- [ ] Advanced ML models (Neural Networks)
- [ ] Multi-language support
- [ ] OAuth integration
- [ ] API endpoints for external integrations

## 📸 Screenshots

*Add screenshots of your application here*

## 🏆 Acknowledgments

- Streamlit team for the amazing framework
- Plotly for interactive visualizations
- Scikit-learn for machine learning capabilities
- ReportLab for PDF generation

---

**Built with ❤️ using Python and Streamlit**