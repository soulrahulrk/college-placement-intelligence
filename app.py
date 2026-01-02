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

from data_engine import load_from_json, StudentProfile, JobDescription, PlacementLog
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
                " Overview Dashboard",
                " Student Analysis",
                " Company Analysis",
                " Credibility Dashboard",
                " Risk Assessment",
                " Fake Skill Detection",
                " Placement Analytics"
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


# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    
    # Load data
    students, companies, logs = load_data()
    
    if not students:
        st.error("No data available. Please run data_engine.py first to generate sample data.")
        return
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
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
    else:
        st.info("Select a page from the sidebar")


if __name__ == "__main__":
    main()
