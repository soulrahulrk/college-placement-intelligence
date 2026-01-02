"""
Streamlit Dashboard for College Placement Intelligence Agent
Interactive UI for placement matching and analytics
"""

import streamlit as st
import pandas as pd
from data_engine import load_from_json, StudentProfile, JobDescription, PlacementLog
from intelligence import (
    match_all_students_to_job,
    match_student_to_all_jobs,
    generate_match_summary,
    analyze_placement_patterns,
    feedback_loop,
    MatchResult
)
from typing import List, Tuple
import plotly.express as px
import plotly.graph_objects as go


# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="College Placement Intelligence",
    page_icon="🎓",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .highly-recommended {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .recommended {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .marginal {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .rejected {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==================== DATA LOADING ====================

@st.cache_data
def load_data():
    """Load all data with caching"""
    students, jobs, logs = load_from_json()
    return students, jobs, logs


@st.cache_data
def compute_all_matches(_students, _jobs):
    """Precompute all matches for performance"""
    all_matches = {}
    for job in _jobs:
        matches = match_all_students_to_job(_students, job)
        all_matches[job.id] = matches
    return all_matches


# ==================== HELPER FUNCTIONS ====================

def get_status_color(status: str) -> str:
    """Get color code for status"""
    colors = {
        "Highly Recommended": "#28a745",
        "Recommended": "#17a2b8",
        "Marginal": "#ffc107",
        "Not Recommended": "#dc3545",
        "Rejected": "#dc3545"
    }
    return colors.get(status, "#6c757d")


def create_student_dataframe(matches: List[Tuple[StudentProfile, MatchResult]]) -> pd.DataFrame:
    """Convert matches to DataFrame for display"""
    data = []
    for student, match in matches:
        data.append({
            "Rank": len(data) + 1,
            "Student ID": student.id,
            "Name": student.name,
            "GPA": student.gpa,
            "Backlogs": student.backlogs,
            "Experience (Years)": student.experience_years,
            "Skills Count": len(student.skills),
            "Match Score": match.score,
            "Status": match.status,
            "Hard Constraint Failed": "Yes" if match.hard_constraint_failed else "No"
        })
    return pd.DataFrame(data)


def display_skill_breakdown(student: StudentProfile):
    """Display student's skills with proficiency"""
    skill_data = []
    for skill in student.skills:
        skill_data.append({
            "Skill": skill.name,
            "Proficiency": skill.proficiency_score,
            "Evidence": skill.evidence_source
        })
    
    df = pd.DataFrame(skill_data)
    df = df.sort_values("Proficiency", ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        df,
        x="Proficiency",
        y="Skill",
        orientation='h',
        color="Proficiency",
        color_continuous_scale="Blues",
        title="Skill Proficiency Breakdown",
        labels={"Proficiency": "Proficiency Score (0-10)"}
    )
    fig.update_layout(height=max(300, len(skill_data) * 25), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display evidence table
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_match_breakdown(match: MatchResult):
    """Display detailed match breakdown"""
    st.subheader("Match Score Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Must-Have Skills",
            f"{match.breakdown.get('must_have_score', 0)}/10",
            f"{match.breakdown.get('must_have_matched', 0)}/{match.breakdown.get('must_have_total', 0)} matched"
        )
    
    with col2:
        st.metric(
            "Good-To-Have Skills",
            f"{match.breakdown.get('good_to_have_score', 0)}/10",
            f"{match.breakdown.get('good_to_have_matched', 0)} matched"
        )
    
    with col3:
        st.metric(
            "Proficiency Depth",
            f"{match.breakdown.get('proficiency_score', 0)}/10",
            f"Avg: {match.breakdown.get('avg_proficiency', 0)}/10"
        )
    
    # Visual breakdown
    breakdown_data = {
        "Component": ["Must-Have Skills", "Good-To-Have Skills", "Proficiency Depth"],
        "Score": [
            match.breakdown.get('must_have_score', 0),
            match.breakdown.get('good_to_have_score', 0),
            match.breakdown.get('proficiency_score', 0)
        ]
    }
    
    fig = px.bar(
        breakdown_data,
        x="Component",
        y="Score",
        title="Score Components",
        color="Score",
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown('<div class="main-header">🎓 College Placement Intelligence Agent</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    try:
        students, jobs, logs = load_data()
        
        if not students or not jobs:
            st.error("⚠️ No data found! Please run `python data_engine.py` first to generate synthetic data.")
            st.stop()
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("💡 Run `python data_engine.py` to generate the required data files.")
        st.stop()
    
    # ==================== SIDEBAR ====================
    
    with st.sidebar:
        st.header("🎯 Navigation")
        
        page = st.radio(
            "Select View",
            ["📊 Job-Based Matching", "👤 Student-Based Matching", "📈 Analytics Dashboard", "🔄 Feedback Loop"]
        )
        
        st.markdown("---")
        st.subheader("📚 Dataset Info")
        st.metric("Students", len(students))
        st.metric("Jobs", len(jobs))
        st.metric("Placement Logs", len(logs))
        
        # Quick stats
        star_students = sum(1 for s in students if s.gpa >= 8.5 and s.backlogs == 0)
        at_risk = sum(1 for s in students if s.gpa < 7.0 or s.backlogs > 0)
        
        st.markdown("---")
        st.subheader("📊 Student Distribution")
        st.write(f"⭐ Star Students: {star_students}")
        st.write(f"⚠️ At-Risk: {at_risk}")
        st.write(f"📚 Average: {len(students) - star_students - at_risk}")
    
    # ==================== PAGE ROUTING ====================
    
    if page == "📊 Job-Based Matching":
        show_job_matching(students, jobs, logs)
    
    elif page == "👤 Student-Based Matching":
        show_student_matching(students, jobs, logs)
    
    elif page == "📈 Analytics Dashboard":
        show_analytics(students, jobs, logs)
    
    elif page == "🔄 Feedback Loop":
        show_feedback_loop(students, jobs, logs)


# ==================== JOB-BASED MATCHING ====================

def show_job_matching(students, jobs, logs):
    """Show students ranked for a selected job"""
    
    st.header("📊 Job-Based Student Ranking")
    st.markdown("Select a job to see all students ranked by match score")
    
    # Job selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_options = {f"{j.company_name} - {j.role} ({j.company_type})": j for j in jobs}
        selected_job_name = st.selectbox("Select Job/Company", list(job_options.keys()))
        selected_job = job_options[selected_job_name]
    
    with col2:
        st.markdown("### Job Requirements")
        st.write(f"**Min GPA:** {selected_job.min_gpa}")
        st.write(f"**Max Backlogs:** {selected_job.max_backlogs_allowed}")
        st.write(f"**Min Experience:** {selected_job.min_experience_years}y")
    
    # Display job skills
    st.markdown("### Required Skills")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Must-Have Skills:**")
        for skill in selected_job.must_have_skills:
            st.markdown(f"- {skill}")
    
    with col2:
        st.markdown("**Good-To-Have Skills:**")
        for skill in selected_job.good_to_have_skills:
            st.markdown(f"- {skill}")
    
    st.markdown("---")
    
    # Compute matches
    with st.spinner("Computing matches..."):
        matches = match_all_students_to_job(students, selected_job)
        summary = generate_match_summary(matches)
    
    # Display summary metrics
    st.subheader("📊 Match Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Students", summary['total_students'])
    
    with col2:
        st.metric("Highly Recommended", summary['highly_recommended'], 
                 f"{summary['distribution']['highly_recommended_pct']}%")
    
    with col3:
        st.metric("Recommended", summary['recommended'],
                 f"{summary['distribution']['recommended_pct']}%")
    
    with col4:
        st.metric("Marginal", summary['marginal'],
                 f"{summary['distribution']['marginal_pct']}%")
    
    with col5:
        st.metric("Hard Constraint Failed", summary['hard_constraint_failures'],
                 f"{summary['distribution']['hard_constraint_pct']}%")
    
    # Score distribution chart
    st.subheader("📈 Score Distribution")
    scores = [match.score for _, match in matches]
    fig = px.histogram(
        scores,
        nbins=20,
        title="Match Score Distribution",
        labels={"value": "Match Score", "count": "Number of Students"},
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Student ranking table
    st.subheader("🏆 Student Rankings")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["Highly Recommended", "Recommended", "Marginal", "Not Recommended"],
            default=["Highly Recommended", "Recommended"]
        )
    
    with col2:
        show_failed = st.checkbox("Show Hard Constraint Failures", value=False)
    
    with col3:
        top_n = st.slider("Show top N students", 5, len(matches), min(20, len(matches)))
    
    # Apply filters
    filtered_matches = matches
    if not show_failed:
        filtered_matches = [(s, m) for s, m in filtered_matches if not m.hard_constraint_failed]
    if status_filter:
        filtered_matches = [(s, m) for s, m in filtered_matches if m.status in status_filter]
    
    filtered_matches = filtered_matches[:top_n]
    
    # Create dataframe
    df = create_student_dataframe(filtered_matches)
    
    # Color-code status
    def highlight_status(row):
        if row['Status'] == 'Highly Recommended':
            return ['background-color: #d4edda'] * len(row)
        elif row['Status'] == 'Recommended':
            return ['background-color: #d1ecf1'] * len(row)
        elif row['Status'] == 'Marginal':
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #f8d7da'] * len(row)
    
    st.dataframe(
        df.style.apply(highlight_status, axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    # Detailed view
    st.markdown("---")
    st.subheader("🔍 Student Details")
    
    selected_student_id = st.selectbox(
        "Select a student to view details",
        [s.id for s, _ in filtered_matches],
        format_func=lambda x: f"{x} - {next(s.name for s, _ in filtered_matches if s.id == x)}"
    )
    
    if selected_student_id:
        student = next(s for s, _ in filtered_matches if s.id == selected_student_id)
        match = next(m for s, m in filtered_matches if s.id == selected_student_id)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"### {student.name}")
            st.write(f"**Student ID:** {student.id}")
            st.write(f"**Email:** {student.email}")
            st.write(f"**Phone:** {student.phone}")
            st.write(f"**GPA:** {student.gpa}/10")
            st.write(f"**Backlogs:** {student.backlogs}")
            st.write(f"**Experience:** {student.experience_years} years")
            
            st.markdown("---")
            st.markdown(f"### Match Score: {match.score}/10")
            st.markdown(f"**Status:** :{get_status_color(match.status)}[{match.status}]")
            
            # Reason in expandable section
            with st.expander("📝 Why this score?", expanded=True):
                st.write(match.detailed_reason)
        
        with col2:
            display_match_breakdown(match)
        
        # Skills breakdown
        display_skill_breakdown(student)


# ==================== STUDENT-BASED MATCHING ====================

def show_student_matching(students, jobs, logs):
    """Show jobs ranked for a selected student"""
    
    st.header("👤 Student-Based Job Recommendations")
    st.markdown("Select a student to see their best job matches")
    
    # Student selection
    student_options = {f"{s.name} (ID: {s.id}, GPA: {s.gpa})": s for s in students}
    selected_student_name = st.selectbox("Select Student", list(student_options.keys()))
    selected_student = student_options[selected_student_name]
    
    # Student profile
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("GPA", selected_student.gpa)
        st.metric("Backlogs", selected_student.backlogs)
    
    with col2:
        st.metric("Experience", f"{selected_student.experience_years}y")
        st.metric("Total Skills", len(selected_student.skills))
    
    with col3:
        avg_proficiency = sum(s.proficiency_score for s in selected_student.skills) / len(selected_student.skills)
        st.metric("Avg Proficiency", f"{avg_proficiency:.1f}/10")
        high_prof_skills = sum(1 for s in selected_student.skills if s.proficiency_score >= 7)
        st.metric("High Proficiency Skills", high_prof_skills)
    
    # Top skills
    st.markdown("### Top Skills")
    top_skills = sorted(selected_student.skills, key=lambda s: s.proficiency_score, reverse=True)[:10]
    skill_cols = st.columns(5)
    for i, skill in enumerate(top_skills):
        with skill_cols[i % 5]:
            st.markdown(f"**{skill.name}**")
            st.progress(skill.proficiency_score / 10)
            st.caption(f"{skill.proficiency_score}/10")
    
    st.markdown("---")
    
    # Compute matches
    with st.spinner("Finding best job matches..."):
        job_matches = match_student_to_all_jobs(selected_student, jobs)
    
    # Display recommendations
    st.subheader("💼 Recommended Jobs")
    
    # Filter by eligibility
    show_ineligible = st.checkbox("Show ineligible jobs (hard constraint failures)", value=False)
    
    if not show_ineligible:
        job_matches = [(j, m) for j, m in job_matches if not m.hard_constraint_failed]
    
    # Create job cards
    for job, match in job_matches[:15]:  # Top 15 matches
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_emoji = {
                    "Highly Recommended": "🌟",
                    "Recommended": "✅",
                    "Marginal": "⚠️",
                    "Not Recommended": "❌",
                    "Rejected": "🚫"
                }
                
                st.markdown(f"### {status_emoji.get(match.status, '📍')} {job.company_name} - {job.role}")
                st.write(f"**Company Type:** {job.company_type}")
                st.write(f"**Requirements:** GPA ≥ {job.min_gpa}, Backlogs ≤ {job.max_backlogs_allowed}, Experience ≥ {job.min_experience_years}y")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Must-Have:** {', '.join(job.must_have_skills[:3])}{' ...' if len(job.must_have_skills) > 3 else ''}")
                with col_b:
                    st.write(f"**Good-To-Have:** {', '.join(job.good_to_have_skills[:3])}{' ...' if len(job.good_to_have_skills) > 3 else ''}")
            
            with col2:
                st.markdown(f"### {match.score}/10")
                st.markdown(f"**{match.status}**")
                
                with st.expander("Why?"):
                    st.write(match.detailed_reason)
            
            st.markdown("---")


# ==================== ANALYTICS DASHBOARD ====================

def show_analytics(students, jobs, logs):
    """Show overall analytics and insights"""
    
    st.header("📈 Analytics Dashboard")
    
    # Analyze placement patterns
    patterns = analyze_placement_patterns(logs)
    
    # Overall metrics
    st.subheader("📊 Overall Placement Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    hired_count = sum(1 for log in logs if log.status == "Hired")
    rejected_count = sum(1 for log in logs if log.status == "Rejected")
    success_rate = hired_count / len(logs) * 100 if logs else 0
    
    with col1:
        st.metric("Total Placement Attempts", len(logs))
    
    with col2:
        st.metric("Hired", hired_count, f"{success_rate:.1f}%")
    
    with col3:
        st.metric("Rejected", rejected_count)
    
    with col4:
        hard_constraint_rejects = sum(1 for log in logs if "Hard Constraint" in log.reason)
        st.metric("Hard Constraint Rejects", hard_constraint_rejects,
                 f"{hard_constraint_rejects/rejected_count*100:.1f}%" if rejected_count > 0 else "0%")
    
    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['Hired', 'Rejected'],
        values=[hired_count, rejected_count],
        hole=.3,
        marker_colors=['#28a745', '#dc3545']
    )])
    fig.update_layout(title="Placement Outcome Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top rejection reasons
    st.subheader("🔍 Top Rejection Reasons")
    
    rejection_df = pd.DataFrame(
        patterns['top_rejection_reasons'],
        columns=['Reason', 'Count']
    )
    
    fig = px.bar(
        rejection_df,
        x='Count',
        y='Reason',
        orientation='h',
        title="Most Common Rejection Reasons",
        color='Count',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Company success rates
    st.subheader("🏢 Company-wise Success Rates")
    
    company_data = []
    for company_id, stats in patterns['company_success_rates'].items():
        job = next((j for j in jobs if j.id == company_id), None)
        if job:
            company_data.append({
                "Company": job.company_name,
                "Type": job.company_type,
                "Success Rate": stats['success_rate'] * 100,
                "Hired": stats['hired'],
                "Rejected": stats['rejected'],
                "Total": stats['total']
            })
    
    company_df = pd.DataFrame(company_data).sort_values("Success Rate", ascending=False)
    
    fig = px.bar(
        company_df,
        x='Company',
        y='Success Rate',
        color='Type',
        title="Success Rate by Company",
        labels={'Success Rate': 'Success Rate (%)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(company_df, use_container_width=True, hide_index=True)
    
    # Student performance distribution
    st.subheader("🎓 Student Performance Distribution")
    
    student_data = []
    for student in students:
        category = "Star" if student.gpa >= 8.5 and student.backlogs == 0 else \
                   "At-Risk" if student.gpa < 7.0 or student.backlogs > 0 else \
                   "Average"
        student_data.append({
            "Category": category,
            "GPA": student.gpa,
            "Skills": len(student.skills),
            "Avg Proficiency": sum(s.proficiency_score for s in student.skills) / len(student.skills)
        })
    
    student_df = pd.DataFrame(student_data)
    
    fig = px.scatter(
        student_df,
        x='GPA',
        y='Avg Proficiency',
        color='Category',
        size='Skills',
        title="Student Distribution by GPA and Proficiency",
        labels={'Avg Proficiency': 'Average Skill Proficiency'},
        color_discrete_map={'Star': '#28a745', 'Average': '#17a2b8', 'At-Risk': '#dc3545'}
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================== FEEDBACK LOOP ====================

def show_feedback_loop(students, jobs, logs):
    """Show feedback loop and weight adjustments"""
    
    st.header("🔄 Feedback Loop & Weight Optimization")
    st.markdown("Analyze historical data to optimize matching weights per company")
    
    # Compute adjusted weights
    with st.spinner("Analyzing placement history..."):
        adjusted_weights = feedback_loop(logs, students, jobs)
    
    st.subheader("📊 Company-Specific Weight Adjustments")
    
    default_weights = {"must_have": 0.5, "good_to_have": 0.3, "proficiency": 0.2}
    
    weight_comparison = []
    for company_id, weights in adjusted_weights.items():
        job = next((j for j in jobs if j.id == company_id), None)
        if job:
            weight_comparison.append({
                "Company": job.company_name,
                "Type": job.company_type,
                "Must-Have (Default)": default_weights["must_have"],
                "Must-Have (Adjusted)": weights["must_have"],
                "Good-To-Have (Default)": default_weights["good_to_have"],
                "Good-To-Have (Adjusted)": weights["good_to_have"],
                "Proficiency (Default)": default_weights["proficiency"],
                "Proficiency (Adjusted)": weights["proficiency"],
                "Change": abs(weights["must_have"] - default_weights["must_have"]) + 
                         abs(weights["good_to_have"] - default_weights["good_to_have"]) +
                         abs(weights["proficiency"] - default_weights["proficiency"])
            })
    
    weight_df = pd.DataFrame(weight_comparison).sort_values("Change", ascending=False)
    
    # Visualization
    st.markdown("### Weight Comparison")
    
    for idx, row in weight_df.head(5).iterrows():
        with st.expander(f"{row['Company']} ({row['Type']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Must-Have Weight",
                    f"{row['Must-Have (Adjusted)']:.2f}",
                    f"{(row['Must-Have (Adjusted)'] - row['Must-Have (Default)']):.2f}"
                )
            
            with col2:
                st.metric(
                    "Good-To-Have Weight",
                    f"{row['Good-To-Have (Adjusted)']:.2f}",
                    f"{(row['Good-To-Have (Adjusted)'] - row['Good-To-Have (Default)']):.2f}"
                )
            
            with col3:
                st.metric(
                    "Proficiency Weight",
                    f"{row['Proficiency (Adjusted)']:.2f}",
                    f"{(row['Proficiency (Adjusted)'] - row['Proficiency (Default)']):.2f}"
                )
    
    st.dataframe(weight_df, use_container_width=True, hide_index=True)
    
    # Insights
    st.subheader("💡 Key Insights")
    
    high_must_have = weight_df[weight_df['Must-Have (Adjusted)'] > 0.6]
    high_proficiency = weight_df[weight_df['Proficiency (Adjusted)'] > 0.25]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Companies Prioritizing Must-Haves")
        if len(high_must_have) > 0:
            for _, row in high_must_have.iterrows():
                st.write(f"- **{row['Company']}**: {row['Must-Have (Adjusted)']:.2%} weight on must-haves")
        else:
            st.write("No companies with significantly high must-have weights")
    
    with col2:
        st.markdown("### Companies Prioritizing Proficiency")
        if len(high_proficiency) > 0:
            for _, row in high_proficiency.iterrows():
                st.write(f"- **{row['Company']}**: {row['Proficiency (Adjusted)']:.2%} weight on proficiency")
        else:
            st.write("No companies with significantly high proficiency weights")


# ==================== RUN APP ====================

if __name__ == "__main__":
    main()
