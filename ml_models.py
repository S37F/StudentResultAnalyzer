import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

class MLAnalytics:
    """Machine Learning analytics for student performance data"""
    
    def __init__(self, user_data):
        self.user_data = user_data
        self.combined_data = self._prepare_ml_data()
    
    def _prepare_ml_data(self):
        """Prepare data for ML analysis"""
        try:
            all_records = []
            
            for record in self.user_data:
                df = record['data'].copy()
                df['academic_year'] = record['academic_year']
                df['semester'] = record['semester']
                df['semester_num'] = self._extract_semester_number(record['semester'])
                all_records.append(df)
            
            if all_records:
                combined = pd.concat(all_records, ignore_index=True)
                
                # Ensure numeric columns
                numeric_cols = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total', 'SGPA']
                for col in numeric_cols:
                    if col in combined.columns:
                        combined[col] = pd.to_numeric(combined[col], errors='coerce').fillna(0)
                
                return combined
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error preparing ML data: {e}")
            return pd.DataFrame()
    
    def _extract_semester_number(self, semester_str):
        """Extract numeric semester value"""
        try:
            import re
            match = re.search(r'(\d+)', semester_str)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def perform_clustering(self):
        """Perform K-means clustering on subject performance"""
        try:
            if self.combined_data.empty:
                raise ValueError("No data available for clustering")
            
            # Prepare features for clustering
            feature_cols = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total']
            available_cols = [col for col in feature_cols if col in self.combined_data.columns]
            
            if len(available_cols) < 2:
                raise ValueError("Insufficient features for clustering")
            
            # Get subject-wise aggregated data
            subject_data = self.combined_data.groupby('Subject')[available_cols].mean().reset_index()
            
            if len(subject_data) < 3:
                raise ValueError("Need at least 3 subjects for clustering")
            
            # Prepare features
            X = subject_data[available_cols].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform K-means clustering
            n_clusters = min(3, len(subject_data))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Add cluster labels to data
            subject_data['Cluster'] = clusters
            subject_data['Cluster_Label'] = subject_data['Cluster'].map({
                0: 'High Performers',
                1: 'Average Performers', 
                2: 'Needs Improvement'
            })
            
            # Create visualization using PCA for 2D plot
            if len(available_cols) > 2:
                pca = PCA(n_components=2, random_state=42)
                X_pca = pca.fit_transform(X_scaled)
                
                fig = px.scatter(
                    x=X_pca[:, 0],
                    y=X_pca[:, 1],
                    color=subject_data['Cluster_Label'],
                    text=subject_data['Subject'],
                    title='Subject Performance Clusters (PCA Visualization)',
                    labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',
                           'y': f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)'}
                )
            else:
                # For 2D data, plot directly
                fig = px.scatter(
                    subject_data,
                    x=available_cols[0],
                    y=available_cols[1] if len(available_cols) > 1 else available_cols[0],
                    color='Cluster_Label',
                    text='Subject',
                    title='Subject Performance Clusters'
                )
            
            fig.update_traces(textposition='top center')
            fig.update_layout(height=500)
            
            # Generate cluster info
            cluster_info = []
            for cluster_id in range(n_clusters):
                cluster_subjects = subject_data[subject_data['Cluster'] == cluster_id]['Subject'].tolist()
                avg_total = subject_data[subject_data['Cluster'] == cluster_id]['Total'].mean()
                
                cluster_info.append(f"**Cluster {cluster_id + 1}:** {', '.join(cluster_subjects)} (Avg: {avg_total:.1f})")
            
            return fig, '\n'.join(cluster_info)
            
        except Exception as e:
            raise Exception(f"Clustering analysis failed: {str(e)}")
    
    def predict_sgpa(self):
        """Predict next semester SGPA using linear regression"""
        try:
            if self.combined_data.empty or 'SGPA' not in self.combined_data.columns:
                raise ValueError("No SGPA data available for prediction")
            
            # Get semester-wise SGPA data
            semester_sgpa = self.combined_data.groupby(['academic_year', 'semester', 'semester_num'])['SGPA'].first().reset_index()
            semester_sgpa = semester_sgpa.sort_values('semester_num')
            
            if len(semester_sgpa) < 2:
                raise ValueError("Need at least 2 semesters for prediction")
            
            # Prepare data for regression
            X = semester_sgpa['semester_num'].values.reshape(-1, 1)
            y = semester_sgpa['SGPA'].values
            
            # Fit linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next semester
            next_semester = semester_sgpa['semester_num'].max() + 1
            predicted_sgpa = model.predict([[next_semester]])[0]
            
            # Ensure prediction is within valid range
            predicted_sgpa = max(0, min(10, predicted_sgpa))
            
            # Create prediction visualization
            extended_semesters = list(range(1, next_semester + 1))
            predicted_values = model.predict(np.array(extended_semesters).reshape(-1, 1))
            
            fig = go.Figure()
            
            # Add historical data
            fig.add_trace(go.Scatter(
                x=semester_sgpa['semester_num'],
                y=semester_sgpa['SGPA'],
                mode='markers+lines',
                name='Historical SGPA',
                line=dict(color='blue'),
                marker=dict(size=8)
            ))
            
            # Add prediction line
            fig.add_trace(go.Scatter(
                x=extended_semesters,
                y=predicted_values,
                mode='lines',
                name='Trend Line',
                line=dict(color='red', dash='dash')
            ))
            
            # Highlight predicted point
            fig.add_trace(go.Scatter(
                x=[next_semester],
                y=[predicted_sgpa],
                mode='markers',
                name=f'Predicted Semester {next_semester}',
                marker=dict(size=12, color='red', symbol='star')
            ))
            
            fig.update_layout(
                title='SGPA Prediction Using Linear Regression',
                xaxis_title='Semester',
                yaxis_title='SGPA',
                height=500,
                yaxis=dict(range=[0, 10])
            )
            
            return fig, predicted_sgpa
            
        except Exception as e:
            raise Exception(f"SGPA prediction failed: {str(e)}")
    
    def perform_pca_analysis(self):
        """Perform PCA analysis on performance features"""
        try:
            if self.combined_data.empty:
                raise ValueError("No data available for PCA analysis")
            
            # Prepare features for PCA
            feature_cols = ['CA_Marks', 'ESE_Marks', 'Lab_Marks', 'Total']
            available_cols = [col for col in feature_cols if col in self.combined_data.columns]
            
            if len(available_cols) < 2:
                raise ValueError("Need at least 2 features for PCA")
            
            # Get subject-wise data
            subject_data = self.combined_data.groupby('Subject')[available_cols].mean().reset_index()
            
            if len(subject_data) < 3:
                raise ValueError("Need at least 3 subjects for PCA")
            
            # Prepare and scale features
            X = subject_data[available_cols].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform PCA
            pca = PCA(random_state=42)
            X_pca = pca.fit_transform(X_scaled)
            
            # Create biplot
            fig = go.Figure()
            
            # Add data points
            fig.add_trace(go.Scatter(
                x=X_pca[:, 0],
                y=X_pca[:, 1],
                mode='markers+text',
                text=subject_data['Subject'],
                textposition='top center',
                marker=dict(size=10, color='blue'),
                name='Subjects'
            ))
            
            # Add feature vectors
            feature_vectors = pca.components_.T * np.sqrt(pca.explained_variance_)
            
            for i, feature in enumerate(available_cols):
                fig.add_trace(go.Scatter(
                    x=[0, feature_vectors[i, 0]],
                    y=[0, feature_vectors[i, 1]],
                    mode='lines+text',
                    text=['', feature],
                    textposition='middle right',
                    line=dict(color='red', width=2),
                    name=feature
                ))
            
            fig.update_layout(
                title=f'PCA Analysis - Feature Importance<br>PC1: {pca.explained_variance_ratio_[0]:.1%}, PC2: {pca.explained_variance_ratio_[1]:.1%}',
                xaxis_title=f'First Principal Component ({pca.explained_variance_ratio_[0]:.1%} variance)',
                yaxis_title=f'Second Principal Component ({pca.explained_variance_ratio_[1]:.1%} variance)',
                height=500,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"PCA analysis failed: {str(e)}")
    
    def analyze_performance_patterns(self):
        """Analyze patterns in performance data"""
        try:
            if self.combined_data.empty:
                return {}
            
            patterns = {}
            
            # CA vs ESE pattern
            if 'CA_Marks' in self.combined_data.columns and 'ESE_Marks' in self.combined_data.columns:
                ca_avg = self.combined_data['CA_Marks'].mean()
                ese_avg = self.combined_data['ESE_Marks'].mean()
                
                if ca_avg > ese_avg * 1.1:
                    patterns['assessment_pattern'] = "Strong in continuous assessment"
                elif ese_avg > ca_avg * 1.1:
                    patterns['assessment_pattern'] = "Better at end-semester exams"
                else:
                    patterns['assessment_pattern'] = "Balanced performance"
            
            # Consistency pattern
            if 'Total' in self.combined_data.columns:
                total_std = self.combined_data['Total'].std()
                total_mean = self.combined_data['Total'].mean()
                cv = total_std / total_mean if total_mean > 0 else 0
                
                if cv < 0.15:
                    patterns['consistency'] = "Very consistent performance"
                elif cv < 0.25:
                    patterns['consistency'] = "Moderately consistent"
                else:
                    patterns['consistency'] = "Variable performance across subjects"
            
            # Improvement trend
            if 'semester_num' in self.combined_data.columns and 'SGPA' in self.combined_data.columns:
                semester_sgpa = self.combined_data.groupby('semester_num')['SGPA'].first()
                if len(semester_sgpa) >= 2:
                    trend_slope = np.polyfit(semester_sgpa.index, semester_sgpa.values, 1)[0]
                    
                    if trend_slope > 0.1:
                        patterns['trend'] = "Improving over time"
                    elif trend_slope < -0.1:
                        patterns['trend'] = "Declining trend"
                    else:
                        patterns['trend'] = "Stable performance"
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return {}
