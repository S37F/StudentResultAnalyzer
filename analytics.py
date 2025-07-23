import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class PerformanceAnalytics:
    """Analytics engine for student performance data"""
    
    def __init__(self, user_data: List[Dict]):
        self.user_data = user_data
        self.combined_data = self._combine_all_data()
    
    def _combine_all_data(self) -> pd.DataFrame:
        """Combine all semester data into a single DataFrame"""
        all_records = []
        
        for record in self.user_data:
            df = record['data'].copy()
            df['academic_year'] = record['academic_year']
            df['semester'] = record['semester']
            df['semester_num'] = self._extract_semester_number(record['semester'])
            all_records.append(df)
        
        if all_records:
            return pd.concat(all_records, ignore_index=True)
        return pd.DataFrame()
    
    def _extract_semester_number(self, semester_str: str) -> int:
        """Extract numeric semester value"""
        try:
            # Extract number from "Semester X" format
            import re
            match = re.search(r'(\d+)', semester_str)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def get_average_sgpa(self) -> float:
        """Calculate average SGPA across all semesters"""
        try:
            if self.combined_data.empty or 'SGPA' not in self.combined_data.columns:
                return 0.0
            
            # Get unique SGPA values per semester
            semester_sgpa = self.combined_data.groupby(['academic_year', 'semester'])['SGPA'].first()
            valid_sgpa = semester_sgpa[semester_sgpa > 0]
            
            return float(valid_sgpa.mean()) if not valid_sgpa.empty else 0.0
        except:
            return 0.0
    
    def get_total_subjects(self) -> int:
        """Get total number of unique subjects"""
        try:
            if self.combined_data.empty:
                return 0
            return len(self.combined_data['Subject'].unique())
        except:
            return 0
    
    def get_best_semester(self) -> str:
        """Find semester with highest SGPA"""
        try:
            if self.combined_data.empty or 'SGPA' not in self.combined_data.columns:
                return "N/A"
            
            semester_sgpa = self.combined_data.groupby(['academic_year', 'semester'])['SGPA'].first()
            valid_sgpa = semester_sgpa[semester_sgpa > 0]
            
            if valid_sgpa.empty:
                return "N/A"
            
            best_semester_idx = valid_sgpa.idxmax()
            return f"{best_semester_idx[0]} - {best_semester_idx[1]}"
        except:
            return "N/A"
    
    def get_worst_semester(self) -> str:
        """Find semester with lowest SGPA"""
        try:
            if self.combined_data.empty or 'SGPA' not in self.combined_data.columns:
                return "N/A"
            
            semester_sgpa = self.combined_data.groupby(['academic_year', 'semester'])['SGPA'].first()
            valid_sgpa = semester_sgpa[semester_sgpa > 0]
            
            if valid_sgpa.empty:
                return "N/A"
            
            worst_semester_idx = valid_sgpa.idxmin()
            return f"{worst_semester_idx[0]} - {worst_semester_idx[1]}"
        except:
            return "N/A"
    
    def get_best_worst_semesters(self) -> Tuple[str, str]:
        """Get both best and worst semesters"""
        return self.get_best_semester(), self.get_worst_semester()
    
    def calculate_cgpa(self) -> float:
        """Calculate CGPA (same as average SGPA for simplicity)"""
        return self.get_average_sgpa()
    
    def get_subject_wise_average(self) -> pd.DataFrame:
        """Calculate subject-wise average marks"""
        try:
            if self.combined_data.empty:
                return pd.DataFrame()
            
            numeric_columns = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total']
            available_columns = [col for col in numeric_columns if col in self.combined_data.columns]
            
            if not available_columns:
                return pd.DataFrame()
            
            subject_avg = self.combined_data.groupby('Subject')[available_columns].mean().round(2)
            return subject_avg.reset_index()
        except:
            return pd.DataFrame()
    
    def get_semester_wise_performance(self) -> pd.DataFrame:
        """Get semester-wise performance summary"""
        try:
            if self.combined_data.empty:
                return pd.DataFrame()
            
            semester_summary = []
            
            for record in self.user_data:
                df = record['data']
                
                summary = {
                    'Academic Year': record['academic_year'],
                    'Semester': record['semester'],
                    'Total Subjects': len(df),
                    'Average CA': df['CA_Marks'].mean() if 'CA_Marks' in df.columns else 0,
                    'Average ESE': df['ESE_Marks'].mean() if 'ESE_Marks' in df.columns else 0,
                    'Average Total': df['Total'].mean() if 'Total' in df.columns else 0,
                    'SGPA': df['SGPA'].iloc[0] if 'SGPA' in df.columns and not df['SGPA'].empty else 0
                }
                
                semester_summary.append(summary)
            
            return pd.DataFrame(semester_summary)
        except:
            return pd.DataFrame()
    
    def get_statistical_summary(self) -> pd.DataFrame:
        """Get statistical summary of marks"""
        try:
            if self.combined_data.empty:
                return pd.DataFrame()
            
            numeric_columns = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total']
            available_columns = [col for col in numeric_columns if col in self.combined_data.columns]
            
            if not available_columns:
                return pd.DataFrame()
            
            stats_summary = self.combined_data[available_columns].describe().round(2)
            return stats_summary
        except:
            return pd.DataFrame()
    
    def get_performance_categories(self) -> Dict[str, int]:
        """Categorize performance into High/Medium/Low"""
        try:
            if self.combined_data.empty or 'Total' not in self.combined_data.columns:
                return {'High': 0, 'Medium': 0, 'Low': 0}
            
            total_marks = self.combined_data['Total']
            
            # Define thresholds (assuming out of 100)
            high_threshold = 75
            medium_threshold = 50
            
            categories = {
                'High': len(total_marks[total_marks >= high_threshold]),
                'Medium': len(total_marks[(total_marks >= medium_threshold) & (total_marks < high_threshold)]),
                'Low': len(total_marks[total_marks < medium_threshold])
            }
            
            return categories
        except:
            return {'High': 0, 'Medium': 0, 'Low': 0}
    
    def get_ca_ese_correlation(self) -> float:
        """Calculate correlation between CA and ESE marks"""
        try:
            if self.combined_data.empty:
                return 0.0
            
            if 'CA_Marks' in self.combined_data.columns and 'ESE_Marks' in self.combined_data.columns:
                correlation = self.combined_data['CA_Marks'].corr(self.combined_data['ESE_Marks'])
                return float(correlation) if not pd.isna(correlation) else 0.0
            
            return 0.0
        except:
            return 0.0
    
    def get_improvement_suggestions(self) -> List[str]:
        """Generate performance improvement suggestions"""
        suggestions = []
        
        try:
            if self.combined_data.empty:
                return ["Upload more data to get personalized suggestions"]
            
            # Analyze CA vs ESE performance
            if 'CA_Marks' in self.combined_data.columns and 'ESE_Marks' in self.combined_data.columns:
                avg_ca = self.combined_data['CA_Marks'].mean()
                avg_ese = self.combined_data['ESE_Marks'].mean()
                
                if avg_ca < avg_ese:
                    suggestions.append("Focus on continuous assessment - your ESE performance is better than CA")
                elif avg_ese < avg_ca:
                    suggestions.append("Prepare more for end semester exams - your CA performance is strong")
            
            # Analyze subject performance
            subject_avg = self.get_subject_wise_average()
            if not subject_avg.empty and 'Total' in subject_avg.columns:
                weak_subjects = subject_avg[subject_avg['Total'] < subject_avg['Total'].mean()]
                if not weak_subjects.empty:
                    suggestions.append(f"Focus on improving: {', '.join(weak_subjects['Subject'].head(3).tolist())}")
            
            # SGPA trend analysis
            avg_sgpa = self.get_average_sgpa()
            if avg_sgpa > 0:
                if avg_sgpa < 6.0:
                    suggestions.append("Consider studying strategies to improve overall SGPA")
                elif avg_sgpa >= 8.0:
                    suggestions.append("Excellent performance! Maintain consistency across all subjects")
            
            if not suggestions:
                suggestions.append("Keep up the good work! Continue consistent performance across all subjects")
            
            return suggestions
            
        except:
            return ["Upload more data to get personalized suggestions"]
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            if self.combined_data.empty:
                return {}
            
            # Semester-wise SGPA trend
            semester_perf = self.get_semester_wise_performance()
            
            if semester_perf.empty:
                return {}
            
            # Sort by semester number for trend analysis
            semester_perf['Semester_Num'] = semester_perf['Semester'].apply(self._extract_semester_number)
            semester_perf = semester_perf.sort_values('Semester_Num')
            
            sgpa_trend = semester_perf['SGPA'].tolist()
            
            # Calculate trend direction
            if len(sgpa_trend) >= 2:
                recent_trend = "improving" if sgpa_trend[-1] > sgpa_trend[-2] else "declining"
                overall_trend = "improving" if sgpa_trend[-1] > sgpa_trend[0] else "declining"
            else:
                recent_trend = "stable"
                overall_trend = "stable"
            
            return {
                'sgpa_values': sgpa_trend,
                'recent_trend': recent_trend,
                'overall_trend': overall_trend,
                'best_sgpa': max(sgpa_trend) if sgpa_trend else 0,
                'worst_sgpa': min(sgpa_trend) if sgpa_trend else 0,
                'average_sgpa': sum(sgpa_trend) / len(sgpa_trend) if sgpa_trend else 0
            }
            
        except:
            return {}
