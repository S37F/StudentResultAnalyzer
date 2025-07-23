import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from analytics import PerformanceAnalytics

class create_charts:
    """Class containing all chart creation functions"""
    
    @staticmethod
    def create_sgpa_trend(user_data):
        """Create SGPA trend line chart"""
        try:
            analytics = PerformanceAnalytics(user_data)
            semester_perf = analytics.get_semester_wise_performance()
            
            if semester_perf.empty:
                # Create empty chart with message
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available for SGPA trend",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                fig.update_layout(
                    title="SGPA Trend Over Semesters",
                    xaxis_title="Semester",
                    yaxis_title="SGPA"
                )
                return fig
            
            # Sort by semester number
            semester_perf['Semester_Num'] = semester_perf['Semester'].apply(
                lambda x: analytics._extract_semester_number(x)
            )
            semester_perf = semester_perf.sort_values('Semester_Num')
            
            fig = px.line(
                semester_perf,
                x='Semester',
                y='SGPA',
                title='SGPA Trend Over Semesters',
                markers=True,
                line_shape='spline'
            )
            
            # Add value labels on points
            fig.update_traces(
                text=semester_perf['SGPA'].round(2),
                textposition="top center",
                textfont=dict(size=12)
            )
            
            fig.update_layout(
                xaxis_title="Semester",
                yaxis_title="SGPA",
                yaxis=dict(range=[0, 10]),
                height=400
            )
            
            return fig
            
        except Exception as e:
            # Return empty chart on error
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_subject_performance(user_data):
        """Create subject-wise performance bar chart"""
        try:
            analytics = PerformanceAnalytics(user_data)
            subject_avg = analytics.get_subject_wise_average()
            
            if subject_avg.empty or 'Total' not in subject_avg.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text="No subject performance data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                fig.update_layout(title="Subject-wise Performance")
                return fig
            
            fig = px.bar(
                subject_avg,
                x='Subject',
                y='Total',
                title='Average Performance by Subject',
                color='Total',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title="Subject",
                yaxis_title="Average Marks",
                xaxis_tickangle=-45,
                height=400
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_subject_average_chart(user_data):
        """Create detailed subject average chart with CA, ESE, Lab breakdown"""
        try:
            analytics = PerformanceAnalytics(user_data)
            subject_avg = analytics.get_subject_wise_average()
            
            if subject_avg.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No subject data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            # Create grouped bar chart
            fig = go.Figure()
            
            if 'CA_Marks' in subject_avg.columns:
                fig.add_trace(go.Bar(
                    name='CA Marks',
                    x=subject_avg['Subject'],
                    y=subject_avg['CA_Marks'],
                    text=subject_avg['CA_Marks'].round(1),
                    textposition='outside'
                ))
            
            if 'ESE_Marks' in subject_avg.columns:
                fig.add_trace(go.Bar(
                    name='ESE Marks',
                    x=subject_avg['Subject'],
                    y=subject_avg['ESE_Marks'],
                    text=subject_avg['ESE_Marks'].round(1),
                    textposition='outside'
                ))
            
            if 'Lab_Marks' in subject_avg.columns:
                fig.add_trace(go.Bar(
                    name='Lab Marks',
                    x=subject_avg['Subject'],
                    y=subject_avg['Lab_Marks'],
                    text=subject_avg['Lab_Marks'].round(1),
                    textposition='outside'
                ))
            
            fig.update_layout(
                title='Subject-wise Average Marks Breakdown',
                xaxis_title='Subject',
                yaxis_title='Marks',
                barmode='group',
                xaxis_tickangle=-45,
                height=500
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_ca_ese_scatter(user_data):
        """Create scatter plot of CA vs ESE marks"""
        try:
            analytics = PerformanceAnalytics(user_data)
            combined_data = analytics.combined_data
            
            if combined_data.empty or 'CA_Marks' not in combined_data.columns or 'ESE_Marks' not in combined_data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text="CA and ESE marks data not available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            fig = px.scatter(
                combined_data,
                x='CA_Marks',
                y='ESE_Marks',
                color='Subject',
                title='CA vs ESE Performance',
                hover_data=['Subject', 'Total'],
                trendline='ols'
            )
            
            fig.update_layout(
                xaxis_title="CA Marks",
                yaxis_title="ESE Marks",
                height=500
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_semester_comparison(user_data):
        """Create semester comparison chart"""
        try:
            analytics = PerformanceAnalytics(user_data)
            semester_perf = analytics.get_semester_wise_performance()
            
            if semester_perf.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No semester data available for comparison",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            fig = px.bar(
                semester_perf,
                x='Semester',
                y='SGPA',
                title='Semester-wise SGPA Comparison',
                color='SGPA',
                color_continuous_scale='RdYlGn',
                text='SGPA'
            )
            
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Semester",
                yaxis_title="SGPA",
                height=400
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_marks_histogram(user_data):
        """Create histogram of marks distribution"""
        try:
            analytics = PerformanceAnalytics(user_data)
            combined_data = analytics.combined_data
            
            if combined_data.empty or 'Total' not in combined_data.columns:
                fig = go.Figure()
                fig.add_annotation(
                    text="No marks data available for histogram",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            fig = px.histogram(
                combined_data,
                x='Total',
                nbins=20,
                title='Distribution of Total Marks',
                color_discrete_sequence=['skyblue']
            )
            
            fig.update_layout(
                xaxis_title="Total Marks",
                yaxis_title="Frequency",
                height=400
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
    
    @staticmethod
    def create_performance_pie_chart(user_data):
        """Create pie chart of performance categories"""
        try:
            analytics = PerformanceAnalytics(user_data)
            categories = analytics.get_performance_categories()
            
            if sum(categories.values()) == 0:
                fig = go.Figure()
                fig.add_annotation(
                    text="No performance data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return fig
            
            fig = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title='Performance Category Distribution',
                color_discrete_map={
                    'High': 'green',
                    'Medium': 'orange',
                    'Low': 'red'
                }
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=14)
            )
            return fig
