import streamlit as st
from config.database import init_database, save_resume_data, save_analysis_data, save_ai_analysis_data
from config.job_roles import JOB_ROLES
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS
from utils.resume_analyzer import ResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from utils.ai_resume_analyzer import AIResumeAnalyzer
from ui_components import (render_hero_section, render_feature_card, render_about_section,
                           render_page_header, apply_custom_css)
from dashboard.dashboard import DashboardManager
from feedback.feedback import FeedbackManager, init_feedback_db
from jobs.job_search import JobSearchManager
from jobs.suggestions import get_job_suggestions, get_career_recommendations, get_role_requirements, get_all_roles
import os
import tempfile
from io import BytesIO
import traceback

st.set_page_config(
    page_title="Smart AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'ai_analysis_results' not in st.session_state:
    st.session_state.ai_analysis_results = {}
if 'bullets_data' not in st.session_state:
    st.session_state.bullets_data = {}
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

init_database()
init_feedback_db()

resume_analyzer = ResumeAnalyzer()
resume_builder = ResumeBuilder()
ai_analyzer = AIResumeAnalyzer()
dashboard_manager = DashboardManager()
feedback_manager = FeedbackManager()
job_manager = JobSearchManager()

def sidebar_navigation():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2 style="color: white; margin: 0;">📄 Resume Analyzer</h2>
            <p style="color: #a0a0a0; font-size: 0.85rem; margin-top: 0.25rem;">AI-Powered Career Tools</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        pages = {
            "🏠 Home": "Home",
            "📊 Resume Analyzer": "Resume Analyzer",
            "📝 Resume Builder": "Resume Builder",
            "🤖 AI Analysis": "AI Analysis",
            "📈 Dashboard": "Dashboard",
            "💬 Feedback": "Feedback",
            "🔍 Job Search": "Job Search"
        }

        for label, page_name in pages.items():
            if st.button(label, key=f"nav_{page_name}", use_container_width=True,
                        help=f"Go to {page_name}"):
                st.session_state.page = page_name
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            Smart AI Resume Analyzer<br>
            v1.0.0
        </div>
        """, unsafe_allow_html=True)

def home_page():
    render_hero_section()

    st.markdown("<h2 style='text-align: center; margin: 2rem 0;'>Features</h2>", unsafe_allow_html=True)
    features = [
        ("🔍", "ATS Resume Analysis", "Get comprehensive ATS compatibility scores and detailed suggestions to optimize your resume for applicant tracking systems."),
        ("🤖", "AI-Powered Insights", "Leverage Google Gemini AI for deep resume analysis with personalized recommendations and skill gap identification."),
        ("📝", "Professional Resume Builder", "Create ATS-optimized resumes with 4 professional templates. Download in DOCX format instantly."),
        ("📊", "Analytics Dashboard", "Track resume performance, analyze trends, and monitor your job application progress."),
        ("💼", "Smart Job Matching", "Find relevant job opportunities with AI-powered suggestions matched to your skills and experience."),
        ("🎯", "Career Guidance", "Get personalized course recommendations, interview tips, and career development resources.")
    ]

    cols = st.columns(3)
    for idx, (icon, title, desc) in enumerate(features):
        render_feature_card(icon, title, desc, "Learn More", "#", cols[idx % 3])

    render_about_section()

def resume_analyzer_page():
    render_page_header("Resume Analyzer", "Upload your resume and get instant ATS analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<h3>Upload Resume</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'],
                                         help="Upload your resume in PDF, DOCX, or TXT format")

        categories = list(JOB_ROLES.keys())
        selected_category = st.selectbox("Select Job Category", categories)

        if selected_category:
            roles = list(JOB_ROLES[selected_category].keys())
            selected_role = st.selectbox("Select Target Role", roles)

        if uploaded_file is not None:
            if st.button("Analyze Resume", use_container_width=True):
                with st.spinner("Analyzing your resume..."):
                    try:
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        raw_text = ""

                        if file_ext == '.pdf':
                            raw_text = resume_analyzer.extract_text_from_pdf(uploaded_file)
                        elif file_ext == '.docx':
                            raw_text = resume_analyzer.extract_text_from_docx(uploaded_file)
                        else:
                            raw_text = uploaded_file.read().decode('utf-8')

                        if not raw_text.strip():
                            st.error("Could not extract text from the file. Ensure it contains selectable text.")
                            st.stop()

                        job_requirements = JOB_ROLES[selected_category][selected_role]
                        results = resume_analyzer.analyze_resume(
                            {'raw_text': raw_text}, job_requirements
                        )

                        st.session_state.analysis_results = results
                        st.session_state.resume_data = results

                        resume_id = save_resume_data({
                            'personal_info': {
                                'full_name': results.get('name', 'Unknown'),
                                'email': results.get('email', ''),
                                'phone': results.get('phone', '')
                            },
                            'target_role': selected_role,
                            'target_category': selected_category,
                            'summary': results.get('summary', ''),
                            'education': results.get('education', []),
                            'experience': results.get('experience', []),
                            'projects': results.get('projects', []),
                            'skills': results.get('skills', []),
                            'template': 'modern'
                        })

                        if resume_id:
                            save_analysis_data(resume_id, {
                                'ats_score': results.get('ats_score', 0),
                                'keyword_match_score': results.get('keyword_match', {}).get('score', 0),
                                'format_score': results.get('format_score', 0),
                                'section_score': results.get('section_score', 0),
                                'missing_skills': ', '.join(results.get('keyword_match', {}).get('missing_skills', [])),
                                'recommendations': '\n'.join(results.get('suggestions', []))
                            })

                        st.success("Analysis complete!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        st.code(traceback.format_exc())

    with col2:
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results

            if results.get('document_type') != 'resume':
                st.warning(f"This appears to be a {results.get('document_type')} document.")
                st.info("Please upload a resume for ATS analysis.")
            else:
                ats_score = results.get('ats_score', 0)
                if ats_score >= 70:
                    color = "#00cc66"
                elif ats_score >= 40:
                    color = "#ffaa00"
                else:
                    color = "#ff4444"

                st.markdown(f"""
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 4rem; font-weight: 700; color: {color};">{ats_score}/100</div>
                    <div style="font-size: 1.2rem; color: #a0a0a0;">ATS Compatibility Score</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<h3>Section Scores</h3>", unsafe_allow_html=True)
                section_scores = results.get('section_scores', {})
                if section_scores:
                    cols = st.columns(3)
                    labels = {"contact": "Contact", "summary": "Summary", "skills": "Skills",
                              "experience": "Experience", "education": "Education", "format": "Format"}
                    for idx, (key, val) in enumerate(section_scores.items()):
                        with cols[idx % 3]:
                            label = labels.get(key, key)
                            st.metric(label, f"{val:.0f}%")

                st.markdown("<h3>Suggestions</h3>", unsafe_allow_html=True)
                if results.get('suggestions'):
                    for s in results['suggestions'][:6]:
                        st.markdown(f'<div class="suggestion-item">• {s}</div>', unsafe_allow_html=True)

                if results.get('keyword_match', {}).get('missing_skills'):
                    with st.expander("Missing Skills"):
                        for skill in results['keyword_match']['missing_skills']:
                            st.markdown(f"• {skill}")

def resume_builder_page():
    render_page_header("Resume Builder", "Create professional, ATS-optimized resumes")

    st.markdown("""
    <style>
    .step-header { color: #667eea; font-weight: 700; margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["Personal Info", "Summary", "Experience", "Education", "Skills", "Projects", "Preview"])

    personal = {}
    summary_text = ""
    experience_list = []
    education_list = []
    skills_data = {}
    projects_list = []

    with tabs[0]:
        st.markdown("<h3>Personal Information</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            personal['full_name'] = st.text_input("Full Name",
                value=st.session_state.resume_data.get('name', ''))
            personal['email'] = st.text_input("Email",
                value=st.session_state.resume_data.get('email', ''))
            personal['phone'] = st.text_input("Phone",
                value=st.session_state.resume_data.get('phone', ''))
        with col2:
            personal['title'] = st.text_input("Professional Title",
                placeholder="e.g., Senior Software Engineer")
            personal['location'] = st.text_input("Location",
                placeholder="e.g., San Francisco, CA")
            personal['linkedin'] = st.text_input("LinkedIn URL",
                value=st.session_state.resume_data.get('linkedin', ''))
            personal['portfolio'] = st.text_input("Portfolio URL",
                value=st.session_state.resume_data.get('github', ''))

    with tabs[1]:
        st.markdown("<h3>Professional Summary</h3>", unsafe_allow_html=True)
        summary_text = st.text_area("Summary",
            value=st.session_state.resume_data.get('summary', ''),
            height=150,
            placeholder="Write a compelling professional summary...")

    with tabs[2]:
        st.markdown("<h3>Work Experience</h3>", unsafe_allow_html=True)
        num_experience = st.number_input("Number of experiences", 0, 5, 1)
        experience_list = []
        for i in range(num_experience):
            with st.expander(f"Experience {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    position = st.text_input(f"Position", key=f"exp_pos_{i}")
                    company = st.text_input(f"Company", key=f"exp_comp_{i}")
                with col2:
                    start = st.text_input(f"Start Date", key=f"exp_start_{i}")
                    end = st.text_input(f"End Date", key=f"exp_end_{i}")
                description = st.text_area(f"Description", key=f"exp_desc_{i}", height=80)
                responsibilities = st.text_area(f"Responsibilities (one per line)", key=f"exp_resp_{i}", height=100)
                experience_list.append({
                    "position": position, "company": company,
                    "start_date": start, "end_date": end,
                    "description": description,
                    "responsibilities": [r.strip() for r in responsibilities.split('\n') if r.strip()]
                })

    with tabs[3]:
        st.markdown("<h3>Education</h3>", unsafe_allow_html=True)
        num_education = st.number_input("Number of entries", 0, 3, 1)
        education_list = []
        for i in range(num_education):
            with st.expander(f"Education {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    school = st.text_input(f"Institution", key=f"edu_school_{i}")
                    degree = st.text_input(f"Degree", key=f"edu_degree_{i}")
                with col2:
                    field = st.text_input(f"Field of Study", key=f"edu_field_{i}")
                    grad_date = st.text_input(f"Graduation Date", key=f"edu_date_{i}")
                gpa = st.text_input(f"GPA (optional)", key=f"edu_gpa_{i}")
                education_list.append({
                    "school": school, "degree": degree,
                    "field": field, "graduation_date": grad_date, "gpa": gpa
                })

    with tabs[4]:
        st.markdown("<h3>Skills</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            technical_skills = st.text_area("Technical Skills (comma separated)",
                value=', '.join(st.session_state.resume_data.get('skills', [])[:8]) if st.session_state.resume_data.get('skills') else '',
                height=100,
                placeholder="Python, JavaScript, React, SQL...")
        with col2:
            soft_skills = st.text_area("Soft Skills (comma separated)",
                height=100,
                placeholder="Leadership, Communication, Problem-solving...")
        skills_data = {
            "technical": [s.strip() for s in technical_skills.split(',') if s.strip()],
            "soft": [s.strip() for s in soft_skills.split(',') if s.strip()]
        }

    with tabs[5]:
        st.markdown("<h3>Projects</h3>", unsafe_allow_html=True)
        num_projects = st.number_input("Number of projects", 0, 5, 1)
        projects_list = []
        for i in range(num_projects):
            with st.expander(f"Project {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    proj_name = st.text_input(f"Project Name", key=f"proj_name_{i}")
                with col2:
                    technologies = st.text_input(f"Technologies", key=f"proj_tech_{i}")
                description = st.text_area(f"Description", key=f"proj_desc_{i}", height=80)
                responsibilities = st.text_area(f"Key Features (one per line)", key=f"proj_resp_{i}", height=80)
                projects_list.append({
                    "name": proj_name, "technologies": technologies,
                    "description": description,
                    "responsibilities": [r.strip() for r in responsibilities.split('\n') if r.strip()]
                })

    with tabs[6]:
        st.markdown("<h3>Generate Resume</h3>", unsafe_allow_html=True)

        template = st.selectbox("Choose Template", ["Modern", "Professional", "Minimal", "Creative"])

        if st.button("Generate Resume", use_container_width=True):
            if not personal.get('full_name'):
                st.error("Please fill in your name in the Personal Info tab.")
            else:
                with st.spinner("Generating your resume..."):
                    try:
                        resume_data = {
                            'personal_info': {
                                'full_name': personal['full_name'],
                                'email': personal.get('email', ''),
                                'phone': personal.get('phone', ''),
                                'title': personal.get('title', ''),
                                'location': personal.get('location', ''),
                                'linkedin': personal.get('linkedin', ''),
                                'portfolio': personal.get('portfolio', '')
                            },
                            'summary': summary_text,
                            'experience': experience_list,
                            'education': education_list,
                            'skills': skills_data,
                            'projects': projects_list,
                            'template': template.lower()
                        }

                        doc_buffer = resume_builder.generate_resume(resume_data)

                        st.success("Resume generated successfully!")
                        st.download_button(
                            label="Download Resume (DOCX)",
                            data=doc_buffer.getvalue(),
                            file_name=f"{personal['full_name'].replace(' ', '_')}_Resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )

                        resume_id = save_resume_data(resume_data)
                        if resume_id:
                            st.info(f"Resume saved! (ID: {resume_id})")
                            st.session_state.resume_data = resume_data

                    except Exception as e:
                        st.error(f"Failed to generate resume: {str(e)}")
                        st.code(traceback.format_exc())

def ai_analysis_page():
    render_page_header("AI Analysis", "Get deep insights powered by Google Gemini AI")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<h3>Upload Resume for AI Analysis</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose resume file", type=['pdf', 'docx', 'txt'],
                                          key="ai_uploader")

        all_roles = get_all_roles()
        role_names = [r['name'] for r in all_roles]
        selected_role = st.selectbox("Target Job Role (optional)", ["None"] + role_names)

        use_job_desc = st.checkbox("Add Job Description")
        job_description = ""
        if use_job_desc:
            job_description = st.text_area("Paste Job Description", height=150)

        if uploaded_file is not None:
            if st.button("Analyze with AI", use_container_width=True):
                with st.spinner("AI is analyzing your resume... This may take a moment."):
                    try:
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        resume_text = ""

                        if file_ext == '.pdf':
                            resume_text = ai_analyzer.extract_text_from_pdf(uploaded_file)
                        elif file_ext == '.docx':
                            resume_text = ai_analyzer.extract_text_from_docx(uploaded_file)
                        else:
                            resume_text = uploaded_file.read().decode('utf-8')

                        if not resume_text.strip():
                            st.error("Could not extract text.")
                            st.stop()

                        role_info = None
                        if selected_role != "None":
                            role_info = get_role_requirements(selected_role)

                        results = ai_analyzer.analyze_resume(
                            resume_text, selected_role if selected_role != "None" else None,
                            role_info
                        )

                        st.session_state.ai_analysis_results = results

                        if results.get('score'):
                            resume_id = save_resume_data({
                                'personal_info': {'full_name': uploaded_file.name, 'email': '', 'phone': ''},
                                'target_role': selected_role if selected_role != "None" else '',
                                'target_category': '',
                                'summary': '',
                                'education': [],
                                'experience': [],
                                'projects': [],
                                'skills': [],
                                'template': ''
                            })
                            if resume_id:
                                save_ai_analysis_data(resume_id, {
                                    'model_used': results.get('model_used', 'Google Gemini'),
                                    'resume_score': results.get('score', 0),
                                    'job_role': selected_role if selected_role != "None" else 'General'
                                })

                        st.success("AI Analysis complete!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"AI Analysis failed: {str(e)}")
                        st.code(traceback.format_exc())

    with col2:
        results = st.session_state.ai_analysis_results

        if results and not results.get('error'):
            score = results.get('score', 0)
            if score >= 80:
                color = "#00cc66"
            elif score >= 60:
                color = "#ffaa00"
            else:
                color = "#ff4444"

            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3.5rem; font-weight: 700; color: {color};">{score}/100</div>
                <div style="font-size: 1rem; color: #a0a0a0;">Overall Resume Score</div>
                <div style="font-size: 0.85rem; color: #888;">Model: {results.get('model_used', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            ats = results.get('ats_score', 0)
            if ats:
                st.metric("ATS Score", f"{ats}/100")

            if results.get('strengths'):
                with st.expander("Key Strengths", expanded=True):
                    for s in results['strengths']:
                        st.markdown(f"✅ {s}")

            if results.get('weaknesses'):
                with st.expander("Areas for Improvement", expanded=True):
                    for w in results['weaknesses']:
                        st.markdown(f"⚠️ {w}")

            if results.get('suggestions'):
                with st.expander("Recommended Courses/Certifications"):
                    for s in results['suggestions']:
                        st.markdown(f"📚 {s}")

            if results.get('full_response'):
                with st.expander("View Full Analysis"):
                    st.markdown(results['full_response'])

        elif results and results.get('error'):
            st.error(results['error'])
        else:
            st.info("Upload a resume and click 'Analyze with AI' to get started")

def dashboard_page():
    render_page_header("Analytics Dashboard", "Track your resume analysis and application progress")

    if st.session_state.admin_logged_in:
        dashboard_manager.show_dashboard_ui()
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            dashboard_manager.show_admin_login()
        with col2:
            if st.session_state.show_register:
                dashboard_manager.show_register()

def feedback_page():
    render_page_header("Feedback", "Share your experience and help us improve")

    tab1, tab2 = st.tabs(["Submit Feedback", " Feedback Stats"])

    with tab1:
        feedback_manager.show_feedback_form()

    with tab2:
        from feedback.feedback import get_feedback_stats
        stats = get_feedback_stats()
        if stats['total'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Feedback", stats['total'])
            with col2:
                st.metric("Average Rating", f"{stats['avg_rating']}/5")
            with col3:
                st.metric("Categories", len(stats['categories']))

            if stats['categories']:
                st.markdown("<h3>Feedback Distribution</h3>", unsafe_allow_html=True)
                for cat, count in stats['categories']:
                    st.progress(count / stats['total'], text=f"{cat}: {count}")
        else:
            st.info("No feedback yet. Be the first to share your thoughts!")

def job_search_page():
    job_manager.show_job_search_ui()

def main():
    sidebar_navigation()

    page_routes = {
        "Home": home_page,
        "Resume Analyzer": resume_analyzer_page,
        "Resume Builder": resume_builder_page,
        "AI Analysis": ai_analysis_page,
        "Dashboard": dashboard_page,
        "Feedback": feedback_page,
        "Job Search": job_search_page
    }

    current_page = st.session_state.page
    page_func = page_routes.get(current_page, home_page)
    page_func()

if __name__ == "__main__":
    main()
