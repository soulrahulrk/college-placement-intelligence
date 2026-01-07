"""
Streamlit Dashboard for College Placement Intelligence Agent
REALISTIC INDIAN PLACEMENT CELL - Resume Credibility & Risk Assessment

ROLE & MINDSET:
Senior placement-analytics engineer building officer-facing dashboard.
Focus: Fake skill detection, Risk scoring, Explainable decisions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
import json
import io
from datetime import datetime
import requests

from data_engine import (
    load_from_json, 
    StudentProfile, 
    JobDescription, 
    PlacementLog,
    Skill,
    SkillEvidence,
    EligibilityRules,
    WeightPolicy,
    save_to_json
)
from intelligence import (
    calculate_credibility,
    calculate_risk,
    match_student_to_job,
    generate_student_explanation,
    generate_officer_explanation,
    analyze_placement_outcomes,
    CredibilityResult,
    RiskResult,
    MatchResult
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Grok API Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "")  # Set in .env file
GROK_API_URL = "https://api.x.ai/v1/chat/completions"


# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="College Placement Intelligence System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .danger-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


# ==================== DATA LOADING ====================

@st.cache_data
def load_data():
    """Load all data with caching"""
    try:
        students, jobs, logs = load_from_json()
        return students, jobs, logs
    except FileNotFoundError:
        st.error("Data files not found. Please generate data first by running data_engine.py")
        return [], [], []


# ==================== SIDEBAR ====================

def render_sidebar():
    """Render sidebar with navigation and filters"""
    with st.sidebar:
        st.markdown('<h1 style="color: #1f77b4;"> Placement Intelligence</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            [
                "🏠 Overview Dashboard",
                "👤 Student Analysis",
                "🏢 Company Analysis",
                "🎯 Credibility Dashboard",
                "⚠️ Risk Assessment",
                "🚨 Fake Skill Detection",
                "📊 Placement Analytics",
                "📥 Data Import",
                "🤖 AI Assistant"  # New chatbot page
            ],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "**Realistic Indian Placement Cell System**\n\n"
            " Resume Credibility Detection\n"
            " Risk Score Assessment\n"
            " Skill Inflation Detection\n"
            " Explainable AI Decisions\n\n"
            "Built with Pydantic V2 + Streamlit"
        )
        
        return page


# ==================== OVERVIEW DASHBOARD ====================

def render_overview_dashboard(students: List[StudentProfile], companies: List[JobDescription], logs: List[PlacementLog]):
    """Main overview dashboard"""
    st.markdown('<div class="main-header">College Placement Intelligence System</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Resume Credibility  Risk Assessment  Explainable Decisions</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        st.metric("Total Companies", len(companies))
    
    with col3:
        selected_count = sum(1 for log in logs if log.interview_result == "selected")
        st.metric("Successful Placements", selected_count)
    
    with col4:
        success_rate = (selected_count / len(logs) * 100) if logs else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.markdown("---")
    
    # Credibility Distribution
    st.markdown("### Resume Credibility Distribution")
    credibility_data = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    for student in students:
        cred = calculate_credibility(student)
        credibility_data[cred.level] += 1
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.pie(
            values=list(credibility_data.values()),
            names=list(credibility_data.keys()),
            title="Student Credibility Levels",
            color=list(credibility_data.keys()),
            color_discrete_map={"HIGH": "#28a745", "MEDIUM": "#ffc107", "LOW": "#dc3545"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribution")
        st.metric("HIGH Credibility", credibility_data["HIGH"], delta="Safe candidates")
        st.metric("MEDIUM Credibility", credibility_data["MEDIUM"], delta="Monitor closely")
        st.metric("LOW Credibility", credibility_data["LOW"], delta="High risk", delta_color="inverse")
    
    # Branch Distribution
    st.markdown("---")
    st.markdown("### Branch-wise Distribution")
    
    branch_counts = {}
    for student in students:
        branch_counts[student.branch] = branch_counts.get(student.branch, 0) + 1
    
    fig_branch = px.bar(
        x=list(branch_counts.keys()),
        y=list(branch_counts.values()),
        title="Students by Branch",
        labels={"x": "Branch", "y": "Number of Students"},
        color=list(branch_counts.values()),
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_branch, use_container_width=True)
    
    # Company Types
    st.markdown("---")
    st.markdown("### Company Types")
    
    company_types = {}
    for company in companies:
        company_types[company.company_type] = company_types.get(company.company_type, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    for i, (ctype, count) in enumerate(company_types.items()):
        with [col1, col2, col3, col4][i % 4]:
            st.metric(ctype, count)



# ==================== STUDENT ANALYSIS ====================

def render_student_analysis(students: List[StudentProfile], companies: List[JobDescription], logs: List[PlacementLog]):
    """Student-specific analysis page"""
    st.markdown("### Student Analysis & Matching")
    
    student_names = {f"{s.name} ({s.student_id})": s for s in students}
    selected_name = st.selectbox("Select Student", list(student_names.keys()))
    
    if selected_name:
        student = student_names[selected_name]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Student Profile")
            st.write(f"**Name:** {student.name}")
            st.write(f"**Branch:** {student.branch}")
            st.write(f"**CGPA:** {student.cgpa}")
            st.write(f"**Communication Score:** {student.communication_score}/10")
            st.write(f"**Mock Interview Score:** {student.mock_interview_score}/10")
            st.write(f"**Active Backlogs:** {student.active_backlogs}")
        
        with col2:
            # Calculate credibility
            cred = calculate_credibility(student)
            
            st.markdown("#### Resume Credibility")
            if cred.level == "HIGH":
                st.markdown(f'<div class="success-box"><b>Score: {cred.score}</b><br>Level: {cred.level}</div>', unsafe_allow_html=True)
            elif cred.level == "MEDIUM":
                st.markdown(f'<div class="warning-box"><b>Score: {cred.score}</b><br>Level: {cred.level}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="danger-box"><b>Score: {cred.score}</b><br>Level: {cred.level}</div>', unsafe_allow_html=True)
            
            if cred.red_flags:
                st.markdown("**Red Flags:**")
                for flag in cred.red_flags:
                    st.error(flag)
        
        st.markdown("---")
        st.markdown("#### Skills Portfolio")
        
        skills_data = []
        for skill in student.skills:
            skills_data.append({
                "Skill": skill.name,
                "Level": skill.claimed_level,
                "GitHub": "Yes" if skill.evidence.github else "No",
                "Projects": skill.evidence.projects,
                "Certs": skill.evidence.certifications,
                "Internship": "Yes" if skill.evidence.internship else "No"
            })
        
        st.dataframe(pd.DataFrame(skills_data), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Placement Matching Results")
        
        # Match with all companies
        matches = []
        for company in companies:
            match = match_student_to_job(student, company, logs)
            matches.append({
                "Company": company.company_name,
                "Role": company.role,
                "Type": company.company_type,
                "Decision": match.decision,
                "Match Score": match.match_score,
                "Risk": match.risk.risk_level,
                "Failure Reason": match.failure_reason if match.failure_reason else "N/A"
            })
        
        matches_df = pd.DataFrame(matches)
        
        # Color code by decision
        def color_decision(val):
            if val == "selected":
                return 'background-color: #d4edda'
            elif val == "shortlisted":
                return 'background-color: #d1ecf1'
            else:
                return 'background-color: #f8d7da'
        
        styled_df = matches_df.style.applymap(color_decision, subset=['Decision'])
        st.dataframe(styled_df, use_container_width=True)


# ==================== CREDIBILITY DASHBOARD ====================

def render_credibility_dashboard(students: List[StudentProfile]):
    """Dedicated credibility analysis dashboard"""
    st.markdown("### Resume Credibility Analysis Dashboard")
    st.info("Detects skill inflation by analyzing evidence backing claimed skills")
    
    # Calculate credibility for all students
    credibility_records = []
    for student in students:
        cred = calculate_credibility(student)
        credibility_records.append({
            "Student ID": student.student_id,
            "Name": student.name,
            "Branch": student.branch,
            "CGPA": student.cgpa,
            "Score": cred.score,
            "Level": cred.level,
            "Red Flags": len(cred.red_flags),
            "Strengths": len(cred.strengths)
        })
    
    df = pd.DataFrame(credibility_records)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        level_filter = st.multiselect("Filter by Credibility Level", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
    
    with col2:
        branch_filter = st.multiselect("Filter by Branch", df["Branch"].unique(), default=df["Branch"].unique())
    
    filtered_df = df[df["Level"].isin(level_filter) & df["Branch"].isin(branch_filter)]
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_count = len(filtered_df[filtered_df["Level"] == "HIGH"])
        st.metric("HIGH Credibility Students", high_count)
    
    with col2:
        medium_count = len(filtered_df[filtered_df["Level"] == "MEDIUM"])
        st.metric("MEDIUM Credibility Students", medium_count)
    
    with col3:
        low_count = len(filtered_df[filtered_df["Level"] == "LOW"])
        st.metric("LOW Credibility Students", low_count, delta=" Risk", delta_color="inverse")
    
    st.markdown("---")
    
    # Detailed table
    st.markdown("#### Detailed Credibility Analysis")
    st.dataframe(filtered_df.sort_values("Score", ascending=False), use_container_width=True)
    
    # Histogram
    st.markdown("---")
    st.markdown("#### Credibility Score Distribution")
    
    fig = px.histogram(
        filtered_df,
        x="Score",
        nbins=20,
        title="Distribution of Resume Credibility Scores",
        labels={"Score": "Credibility Score (0-1)"},
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================== FAKE SKILL DETECTION ====================

def render_fake_skill_detection(students: List[StudentProfile]):
    """Identify students with suspicious skill claims"""
    st.markdown("### Fake Skill Detection System")
    st.warning(" Detecting students with skill inflation (claimed 'advanced' without evidence)")
    
    suspicious_students = []
    
    for student in students:
        cred = calculate_credibility(student)
        
        # Count suspicious skills
        suspicious_count = 0
        suspicious_skills = []
        
        for skill in student.skills:
            if skill.claimed_level == "advanced":
                if not (skill.evidence.github or skill.evidence.projects >= 2):
                    suspicious_count += 1
                    suspicious_skills.append(skill.name)
        
        if suspicious_count > 0:
            suspicious_students.append({
                "Student ID": student.student_id,
                "Name": student.name,
                "Branch": student.branch,
                "Credibility Score": cred.score,
                "Credibility Level": cred.level,
                "Suspicious Skills": suspicious_count,
                "Skill Names": ", ".join(suspicious_skills)
            })
    
    df = pd.DataFrame(suspicious_students)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Students Flagged", len(suspicious_students))
    
    with col2:
        pct = (len(suspicious_students) / len(students) * 100) if students else 0
        st.metric("% of Total", f"{pct:.1f}%")
    
    with col3:
        critical = len([s for s in suspicious_students if s["Credibility Level"] == "LOW"])
        st.metric("Critical Cases (LOW Cred)", critical, delta=" High Risk", delta_color="inverse")
    
    st.markdown("---")
    st.markdown("#### Flagged Students")
    
    if not df.empty:
        st.dataframe(df.sort_values("Suspicious Skills", ascending=False), use_container_width=True)
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Report as CSV",
            data=csv,
            file_name="fake_skill_detection_report.csv",
            mime="text/csv"
        )
    else:
        st.success("No suspicious skill claims detected!")


# ==================== RISK ASSESSMENT ====================

def render_risk_assessment(students: List[StudentProfile], companies: List[JobDescription], logs: List[PlacementLog]):
    """Risk assessment dashboard"""
    st.markdown("### Risk Assessment Dashboard")
    st.info("Analyzes placement risk based on credibility, historical patterns, and communication gaps")
    
    company_names = {f"{c.company_name} - {c.role}": c for c in companies}
    selected_company = st.selectbox("Select Company", list(company_names.keys()))
    
    if selected_company:
        company = company_names[selected_company]
        
        # Calculate risk for all students
        risk_data = []
        
        for student in students:
            cred = calculate_credibility(student)
            risk = calculate_risk(student, company, logs, cred)
            
            risk_data.append({
                "Student ID": student.student_id,
                "Name": student.name,
                "Branch": student.branch,
                "CGPA": student.cgpa,
                "Communication": student.communication_score,
                "Credibility": cred.level,
                "Risk Level": risk.risk_level,
                "Risk Score": risk.risk_score,
                "Top Factor": risk.factors[0] if risk.factors else "None"
            })
        
        df = pd.DataFrame(risk_data)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            low_risk = len(df[df["Risk Level"] == "LOW"])
            st.metric("LOW Risk Students", low_risk, delta=" Safe")
        
        with col2:
            medium_risk = len(df[df["Risk Level"] == "MEDIUM"])
            st.metric("MEDIUM Risk Students", medium_risk, delta=" Monitor")
        
        with col3:
            high_risk = len(df[df["Risk Level"] == "HIGH"])
            st.metric("HIGH Risk Students", high_risk, delta=" Danger", delta_color="inverse")
        
        st.markdown("---")
        st.markdown("#### Risk Distribution")
        
        # Filter by risk level
        risk_filter = st.multiselect("Filter by Risk Level", ["LOW", "MEDIUM", "HIGH"], default=["LOW", "MEDIUM", "HIGH"])
        
        filtered_df = df[df["Risk Level"].isin(risk_filter)]
        st.dataframe(filtered_df.sort_values("Risk Score", ascending=False), use_container_width=True)


# ==================== PLACEMENT ANALYTICS ====================

def render_placement_analytics(logs: List[PlacementLog]):
    """Placement outcome analytics"""
    st.markdown("### Placement Analytics & Insights")
    
    insights = analyze_placement_outcomes(logs)
    
    # Convert to DataFrame
    data = []
    for company_name, stats in insights.items():
        data.append({
            "Company": company_name,
            "Success Rate": f"{stats['success_rate']*100:.1f}%",
            "Total Applicants": stats["total_applicants"],
            "Selected": stats["selected_count"],
            "Avg CGPA (Selected)": stats["avg_selected_cgpa"],
            "Avg Communication (Selected)": stats["avg_selected_communication"],
            "Recommendation": stats["recommendation"]
        })
    
    df = pd.DataFrame(data)
    
    st.markdown("#### Company Performance Summary")
    st.dataframe(df, use_container_width=True)
    
    # Success rate chart
    fig = px.bar(
        df,
        x="Company",
        y="Success Rate",
        title="Success Rate by Company",
        color="Success Rate",
        color_continuous_scale="RdYlGn"
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================== DATA IMPORT PAGE ====================

def render_data_import():
    """Data import page - Upload students/companies via Excel/CSV"""
    st.markdown('<div class="main-header">📥 Data Import</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("""
    **Upload student and company data** using Excel (.xlsx) or CSV (.csv) files.
    
    ✅ Supports batch imports  
    ✅ Auto-validation with Pydantic models  
    ✅ Saves to existing JSON files  
    """)
    
    tab1, tab2, tab3 = st.tabs(["📚 Import Students", "🏢 Import Companies", "📄 Download Templates"])
    
    # ==================== IMPORT STUDENTS ====================
    with tab1:
        st.subheader("Upload Student Data")
        
        uploaded_file = st.file_uploader(
            "Choose a file (Excel or CSV)",
            type=['xlsx', 'csv'],
            key='student_upload',
            help="Upload file with student data. See 'Download Templates' tab for format."
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("**Preview:**")
                st.dataframe(df.head())
                
                # Validate and convert
                if st.button("✅ Validate & Import Students", type="primary"):
                    with st.spinner("Validating student data..."):
                        students, errors = validate_and_import_students(df)
                        
                        if errors:
                            st.error(f"**Validation errors found ({len(errors)}):**")
                            for error in errors[:10]:  # Show first 10 errors
                                st.warning(error)
                        else:
                            # Load existing data
                            existing_students, companies, logs = load_from_json()
                            
                            # Append new students
                            all_students = existing_students + students
                            
                            # Save
                            save_to_json(all_students, companies, logs)
                            
                            st.success(f"✅ Successfully imported {len(students)} students!")
                            st.balloons()
                            
                            # Show summary
                            st.write("**Import Summary:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Students Added", len(students))
                            with col2:
                                high_cred = sum(1 for s in students if calculate_credibility(s).level == "HIGH")
                                st.metric("HIGH Credibility", high_cred)
                            with col3:
                                avg_cgpa = sum(s.cgpa for s in students) / len(students) if students else 0
                                st.metric("Avg CGPA", f"{avg_cgpa:.2f}")
                            
                            st.info("💡 Data saved to students.json. Refresh the page to see updated data.")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        else:
            st.info("👆 Upload a file to get started")
    
    # ==================== IMPORT COMPANIES ====================
    with tab2:
        st.subheader("Upload Company Data")
        
        uploaded_file = st.file_uploader(
            "Choose a file (Excel or CSV)",
            type=['xlsx', 'csv'],
            key='company_upload',
            help="Upload file with company data. See 'Download Templates' tab for format."
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("**Preview:**")
                st.dataframe(df.head())
                
                # Validate and convert
                if st.button("✅ Validate & Import Companies", type="primary"):
                    with st.spinner("Validating company data..."):
                        companies, errors = validate_and_import_companies(df)
                        
                        if errors:
                            st.error(f"**Validation errors found ({len(errors)}):**")
                            for error in errors[:10]:
                                st.warning(error)
                        else:
                            # Load existing data
                            students, existing_companies, logs = load_from_json()
                            
                            # Append new companies
                            all_companies = existing_companies + companies
                            
                            # Save
                            save_to_json(students, all_companies, logs)
                            
                            st.success(f"✅ Successfully imported {len(companies)} companies!")
                            st.balloons()
                            
                            # Show summary
                            st.write("**Import Summary:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Companies Added", len(companies))
                            with col2:
                                mnc_count = sum(1 for c in companies if c.company_type == "MNC")
                                st.metric("MNCs", mnc_count)
                            with col3:
                                avg_cgpa_req = sum(c.eligibility_rules.min_cgpa for c in companies) / len(companies) if companies else 0
                                st.metric("Avg CGPA Req", f"{avg_cgpa_req:.1f}")
                            
                            st.info("💡 Data saved to jobs.json. Refresh the page to see updated data.")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        else:
            st.info("👆 Upload a file to get started")
    
    # ==================== DOWNLOAD TEMPLATES ====================
    with tab3:
        st.subheader("Download Data Templates")
        
        st.info("Download Excel templates with the correct format and sample data.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📚 Student Template")
            
            # Create sample student data
            sample_students = pd.DataFrame({
                'student_id': ['S999', 'S998'],
                'name': ['Rahul Kumar', 'Priya Sharma'],
                'branch': ['CSE', 'IT'],
                'cgpa': [8.5, 7.8],
                'active_backlogs': [0, 1],
                'communication_score': [8, 7],
                'mock_interview_score': [7, 6],
                'email': ['rahul@college.edu', 'priya@college.edu'],
                'phone': ['+91-9876543210', '+91-9876543211'],
                'skills': [
                    'Python:advanced:github=True,projects=3,certifications=2,internship=True|DSA:intermediate:github=True,projects=2,certifications=1,internship=False',
                    'Java:intermediate:github=True,projects=2,certifications=1,internship=False|React:beginner:github=False,projects=1,certifications=0,internship=False'
                ]
            })
            
            # Convert to Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                sample_students.to_excel(writer, index=False, sheet_name='Students')
            
            st.download_button(
                label="⬇️ Download Student Template.xlsx",
                data=buffer.getvalue(),
                file_name="student_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("""
            **Format:**
            - `student_id`: Unique ID (e.g., S001)
            - `name`: Full name
            - `branch`: CSE/IT/AI/ECE/ME
            - `cgpa`: 5.0 to 9.8
            - `active_backlogs`: 0 to 5
            - `communication_score`: 1 to 10
            - `mock_interview_score`: 1 to 10
            - `email`: Email address
            - `phone`: Phone number
            - `skills`: Format: `SkillName:level:github=bool,projects=int,certifications=int,internship=bool|NextSkill...`
            """)
        
        with col2:
            st.markdown("### 🏢 Company Template")
            
            # Create sample company data
            sample_companies = pd.DataFrame({
                'company_id': ['C999', 'C998'],
                'company_name': ['TechCorp India', 'InnoSoft'],
                'company_type': ['MNC', 'Startup'],
                'role': ['Software Engineer', 'Full Stack Developer'],
                'open_positions': [5, 3],
                'min_cgpa': [7.5, 7.0],
                'max_backlogs': [0, 1],
                'mandatory_skills': ['DSA,Python', 'JavaScript,React'],
                'preferred_skills': ['Git,Docker', 'Node.js,MongoDB'],
                'gpa_weight': [0.3, 0.25],
                'skill_weight': [0.4, 0.5],
                'communication_weight': [0.2, 0.15],
                'mock_interview_weight': [0.1, 0.1],
                'risk_tolerance': ['low', 'medium']
            })
            
            # Convert to Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                sample_companies.to_excel(writer, index=False, sheet_name='Companies')
            
            st.download_button(
                label="⬇️ Download Company Template.xlsx",
                data=buffer.getvalue(),
                file_name="company_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("""
            **Format:**
            - `company_id`: Unique ID (e.g., C001)
            - `company_name`: Company name
            - `company_type`: MNC/Startup/Product/Service
            - `role`: Job title
            - `open_positions`: 1 to 50
            - `min_cgpa`: 6.0 to 8.5
            - `max_backlogs`: 0 to 2
            - `mandatory_skills`: Comma-separated (e.g., DSA,Python)
            - `preferred_skills`: Comma-separated
            - `gpa_weight`: 0.2 to 0.5
            - `skill_weight`: 0.3 to 0.6
            - `communication_weight`: 0.1 to 0.3
            - `mock_interview_weight`: 0.0 to 0.2
            - `risk_tolerance`: low/medium/high
            """)


def validate_and_import_students(df: pd.DataFrame) -> tuple[List[StudentProfile], List[str]]:
    """Validate and convert DataFrame to StudentProfile objects"""
    students = []
    errors = []
    
    required_columns = ['student_id', 'name', 'branch', 'cgpa', 'active_backlogs', 
                       'communication_score', 'mock_interview_score', 'email', 'phone', 'skills']
    
    # Check required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return [], errors
    
    for idx, row in df.iterrows():
        try:
            # Parse skills
            skills = []
            skills_str = str(row['skills'])
            
            if pd.notna(skills_str) and skills_str.strip():
                skill_entries = skills_str.split('|')
                
                for skill_entry in skill_entries:
                    parts = skill_entry.split(':')
                    if len(parts) >= 3:
                        skill_name = parts[0].strip()
                        claimed_level = parts[1].strip()
                        evidence_str = parts[2].strip()
                        
                        # Parse evidence
                        evidence_dict = {}
                        for pair in evidence_str.split(','):
                            if '=' in pair:
                                key, value = pair.split('=')
                                key = key.strip()
                                value = value.strip()
                                
                                if key in ['github', 'internship']:
                                    evidence_dict[key] = value.lower() == 'true'
                                elif key in ['projects', 'certifications']:
                                    evidence_dict[key] = int(value)
                        
                        skill = Skill(
                            name=skill_name,
                            claimed_level=claimed_level,
                            evidence=SkillEvidence(**evidence_dict)
                        )
                        skills.append(skill)
            
            # Create student profile
            student = StudentProfile(
                student_id=str(row['student_id']),
                name=str(row['name']),
                branch=str(row['branch']),
                cgpa=float(row['cgpa']),
                active_backlogs=int(row['active_backlogs']),
                skills=skills,
                communication_score=int(row['communication_score']),
                mock_interview_score=int(row['mock_interview_score']),
                resume_trust_score=0.5,  # Will be calculated
                email=str(row['email']),
                phone=str(row['phone'])
            )
            
            students.append(student)
        
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
    
    return students, errors


def validate_and_import_companies(df: pd.DataFrame) -> tuple[List[JobDescription], List[str]]:
    """Validate and convert DataFrame to JobDescription objects"""
    companies = []
    errors = []
    
    required_columns = ['company_id', 'company_name', 'company_type', 'role', 'open_positions',
                       'min_cgpa', 'max_backlogs', 'mandatory_skills', 'preferred_skills',
                       'gpa_weight', 'skill_weight', 'communication_weight', 
                       'mock_interview_weight', 'risk_tolerance']
    
    # Check required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return [], errors
    
    for idx, row in df.iterrows():
        try:
            # Parse skills lists
            mandatory_skills = [s.strip() for s in str(row['mandatory_skills']).split(',') if s.strip()]
            preferred_skills = [s.strip() for s in str(row['preferred_skills']).split(',') if s.strip()]
            
            # Create eligibility rules
            eligibility = EligibilityRules(
                min_cgpa=float(row['min_cgpa']),
                max_backlogs=int(row['max_backlogs']),
                mandatory_skills=mandatory_skills,
                preferred_skills=preferred_skills
            )
            
            # Create weight policy
            weights = WeightPolicy(
                gpa_weight=float(row['gpa_weight']),
                skill_weight=float(row['skill_weight']),
                communication_weight=float(row['communication_weight']),
                mock_interview_weight=float(row['mock_interview_weight'])
            )
            
            # Create job description
            company = JobDescription(
                company_id=str(row['company_id']),
                company_name=str(row['company_name']),
                company_type=str(row['company_type']),
                role=str(row['role']),
                open_positions=int(row['open_positions']),
                eligibility_rules=eligibility,
                weight_policy=weights,
                risk_tolerance=str(row['risk_tolerance'])
            )
            
            companies.append(company)
        
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
    
    return companies, errors


# ==================== AI CHATBOT ASSISTANT ====================

def get_student_statistics(students: List[StudentProfile]) -> Dict:
    """Tool: Get student statistics"""
    total = len(students)
    if total == 0:
        return {"error": "No students in database"}
    
    branches = {}
    high_cgpa = 0
    high_cred = 0
    low_cred = 0
    
    for s in students:
        branches[s.branch] = branches.get(s.branch, 0) + 1
        if s.cgpa >= 8.0:
            high_cgpa += 1
        
        cred = calculate_credibility(s)
        if cred.level == "HIGH":
            high_cred += 1
        elif cred.level == "LOW":
            low_cred += 1
    
    avg_cgpa = sum(s.cgpa for s in students) / total
    
    return {
        "total_students": total,
        "average_cgpa": round(avg_cgpa, 2),
        "high_cgpa_count": high_cgpa,
        "branches": branches,
        "high_credibility_count": high_cred,
        "low_credibility_count": low_cred
    }

def get_company_statistics(companies: List[JobDescription]) -> Dict:
    """Tool: Get company statistics"""
    total = len(companies)
    if total == 0:
        return {"error": "No companies in database"}
    
    types = {}
    total_positions = 0
    
    for c in companies:
        types[c.company_type] = types.get(c.company_type, 0) + 1
        total_positions += c.open_positions
    
    avg_cgpa_req = sum(c.eligibility_rules.min_cgpa for c in companies) / total
    
    return {
        "total_companies": total,
        "company_types": types,
        "total_open_positions": total_positions,
        "average_cgpa_requirement": round(avg_cgpa_req, 2)
    }

def search_students(students: List[StudentProfile], query: str) -> List[Dict]:
    """Tool: Search students by name, branch, or student_id"""
    query_lower = query.lower()
    results = []
    
    for s in students:
        if (query_lower in s.name.lower() or 
            query_lower in s.branch.lower() or 
            query_lower in s.student_id.lower()):
            
            cred = calculate_credibility(s)
            results.append({
                "student_id": s.student_id,
                "name": s.name,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "credibility": cred.level,
                "skills": [sk.name for sk in s.skills]
            })
    
    return results[:10]  # Limit to 10 results

def get_student_details(students: List[StudentProfile], student_id: str) -> Dict:
    """Tool: Get detailed information about a specific student"""
    student = next((s for s in students if s.student_id == student_id), None)
    
    if not student:
        return {"error": f"Student {student_id} not found"}
    
    cred = calculate_credibility(student)
    
    return {
        "student_id": student.student_id,
        "name": student.name,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "active_backlogs": student.active_backlogs,
        "communication_score": student.communication_score,
        "credibility_score": cred.score,
        "credibility_level": cred.level,
        "red_flags": cred.red_flags,
        "strengths": cred.strengths,
        "skills": [{"name": sk.name, "level": sk.claimed_level, "has_github": sk.evidence.github} for sk in student.skills]
    }

def match_student_to_companies(students: List[StudentProfile], companies: List[JobDescription], 
                                 logs: List[PlacementLog], student_id: str) -> List[Dict]:
    """Tool: Match a student to all companies and show results"""
    student = next((s for s in students if s.student_id == student_id), None)
    
    if not student:
        return [{"error": f"Student {student_id} not found"}]
    
    results = []
    for company in companies:
        match = match_student_to_job(student, company, logs)
        results.append({
            "company": company.company_name,
            "role": company.role,
            "decision": match.decision,
            "match_score": round(match.match_score, 2),
            "risk_level": match.risk.risk_level,
            "failure_reason": match.failure_reason
        })
    
    # Sort by match_score descending
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

def call_grok_api(messages: List[Dict], tools: List[Dict] = None) -> Dict:
    """Call Grok API with optional tool calling"""
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "grok-beta",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def execute_tool_call(tool_name: str, tool_args: Dict, students: List[StudentProfile], 
                      companies: List[JobDescription], logs: List[PlacementLog]) -> str:
    """Execute the requested tool and return results as JSON string"""
    try:
        if tool_name == "get_student_statistics":
            result = get_student_statistics(students)
        elif tool_name == "get_company_statistics":
            result = get_company_statistics(companies)
        elif tool_name == "search_students":
            result = search_students(students, tool_args.get("query", ""))
        elif tool_name == "get_student_details":
            result = get_student_details(students, tool_args.get("student_id", ""))
        elif tool_name == "match_student_to_companies":
            result = match_student_to_companies(students, companies, logs, tool_args.get("student_id", ""))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

def render_ai_assistant():
    """AI Assistant chatbot page with Grok API and agentic capabilities"""
    st.markdown('<div class="main-header">🤖 AI Placement Assistant</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("""
    **Intelligent AI Assistant** powered by Grok AI with access to placement data.
    
    ✅ Ask about student statistics  
    ✅ Search for students by name/branch  
    ✅ Get company information  
    ✅ Match students to companies  
    ✅ Analyze credibility and risk  
    """)
    
    # Load data
    students, companies, logs = load_data()
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Define available tools for the AI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_student_statistics",
                "description": "Get overall statistics about all students including total count, average CGPA, branch distribution, and credibility stats",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_company_statistics",
                "description": "Get statistics about companies including total count, types (MNC/Startup/Product/Service), open positions, and CGPA requirements",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_students",
                "description": "Search for students by name, branch, or student ID. Returns list of matching students with basic info",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, branch, or student ID)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_student_details",
                "description": "Get detailed information about a specific student including CGPA, skills, credibility score, and red flags",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "The student ID (e.g., S001, S002)"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "match_student_to_companies",
                "description": "Match a student to all companies and get placement recommendations with scores and risk levels",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "The student ID to match (e.g., S001, S002)"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        }
    ]
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about students, companies, or placements...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Prepare messages for Grok API
        system_message = {
            "role": "system",
            "content": f"""You are an AI assistant for a college placement intelligence system. You have access to tools that can query student data, company data, and placement logs.

Current database status:
- {len(students)} students enrolled
- {len(companies)} companies registered
- {len(logs)} placement logs

When users ask questions:
1. Use the available tools to fetch accurate data
2. Provide clear, helpful answers
3. For student queries, always mention credibility levels and red flags if present
4. For placement recommendations, explain match scores and risk levels
5. Be professional but friendly

Available branches: CSE, IT, AI, DS, ECE, EEE, ME, CE, CHE, BT, IE
"""
        }
        
        messages = [system_message] + [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.chat_history
        ]
        
        # Call Grok API with tool support
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = call_grok_api(messages, tools)
                
                if "error" in response:
                    st.error(f"API Error: {response['error']}")
                    assistant_message = f"Sorry, I encountered an error: {response['error']}"
                else:
                    # Handle tool calls
                    choice = response.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    
                    # Check if AI wants to use tools
                    tool_calls = message.get("tool_calls", [])
                    
                    if tool_calls:
                        # Execute tool calls
                        tool_messages = []
                        for tool_call in tool_calls:
                            function_name = tool_call["function"]["name"]
                            function_args = json.loads(tool_call["function"]["arguments"])
                            
                            st.info(f"🔧 Using tool: {function_name}")
                            
                            # Execute the tool
                            tool_result = execute_tool_call(
                                function_name, function_args, students, companies, logs
                            )
                            
                            tool_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": function_name,
                                "content": tool_result
                            })
                        
                        # Add assistant message with tool calls
                        messages.append(message)
                        
                        # Add tool results
                        messages.extend(tool_messages)
                        
                        # Get final response from AI
                        final_response = call_grok_api(messages)
                        assistant_message = final_response.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate a response.")
                    else:
                        # No tool calls, direct response
                        assistant_message = message.get("content", "Sorry, I couldn't generate a response.")
                    
                    st.write(assistant_message)
        
        # Add assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})
    
    # Sidebar with example queries
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💡 Example Queries")
        
        example_queries = [
            "How many students are there?",
            "Show me CSE students",
            "What companies are hiring?",
            "Get details for student S001",
            "Match student S001 to companies",
            "Which students have low credibility?",
            "Show me MNC companies",
            "What is the average CGPA?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    
    # Render sidebar first (always available)
    page = render_sidebar()
    
    # Load data
    students, companies, logs = load_data()
    
    # Allow Data Import even when no data exists
    if "Data Import" in page:
        render_data_import()
        return
    
    if not students:
        st.warning("⚠️ No data available. You can either:")
        st.info("1. Run `python data_engine.py` to generate sample data, OR")
        st.info("2. Use the **📥 Data Import** page to upload your own student/company data")
        return
    
    # Route to appropriate page
    if "Overview" in page:
        render_overview_dashboard(students, companies, logs)
    elif "Student Analysis" in page:
        render_student_analysis(students, companies, logs)
    elif "Credibility" in page:
        render_credibility_dashboard(students)
    elif "Fake Skill" in page:
        render_fake_skill_detection(students)
    elif "Risk Assessment" in page:
        render_risk_assessment(students, companies, logs)
    elif "Placement Analytics" in page:
        render_placement_analytics(logs)
    elif "AI Assistant" in page:
        render_ai_assistant()
    else:
        st.info("Select a page from the sidebar")


if __name__ == "__main__":
    main()
