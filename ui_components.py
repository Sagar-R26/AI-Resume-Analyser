import streamlit as st

def render_hero_section():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Smart AI Resume Analyzer</h1>
        <p class="hero-subtitle">Powered by Google Gemini AI | Intelligent Resume Analysis & Building</p>
        <p class="hero-description">
            Transform your job applications with AI-powered resume analysis, professional resume building,
            and personalized career insights. Get instant feedback, ATS optimization scores, and job recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_feature_card(icon, title, description, button_text, button_link, col):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3 class="feature-title">{title}</h3>
            <p class="feature-description">{description}</p>
        </div>
        """, unsafe_allow_html=True)

def render_about_section():
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div class="about-section">
            <h2>About This Tool</h2>
            <p>This AI-powered resume analyzer helps you optimize your resume for ATS systems and human recruiters alike. 
            Upload your resume, get instant feedback, and build professional resumes tailored to your target role.</p>
            <ul>
                <li>ATS Score Calculation</li>
                <li>Keyword Optimization</li>
                <li>Format & Structure Analysis</li>
                <li>AI-Powered Recommendations</li>
                <li>Professional Resume Builder</li>
                <li>Job Role Matching</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="how-it-works">
            <h2>How It Works</h2>
            <div class="step">1. Upload your resume (PDF/DOCX)</div>
            <div class="step">2. Select your target job role</div>
            <div class="step">3. Get comprehensive ATS analysis</div>
            <div class="step">4. Receive AI-powered improvement suggestions</div>
            <div class="step">5. Build an optimized resume</div>
        </div>
        """, unsafe_allow_html=True)

def render_page_header(title, subtitle=None):
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{title}</h1>
        {f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None):
    if delta:
        st.metric(label=label, value=value, delta=delta)
    else:
        st.metric(label=label, value=value)

def render_analytics_section(stats):
    if not stats:
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Total Resumes Analyzed", stats.get('total_resumes', 0))
    with col2:
        render_metric_card("Average ATS Score", f"{stats.get('avg_ats_score', 0):.1f}%")
    with col3:
        render_metric_card("Active Analyses", stats.get('total_analyses', 0))

def render_activity_section(activities):
    if not activities:
        st.info("No recent activity")
        return
    st.markdown("<h3>Recent Activity</h3>", unsafe_allow_html=True)
    for activity in activities:
        if isinstance(activity, (list, tuple)) and len(activity) >= 3:
            name, role, timestamp = activity[0], activity[1], activity[2]
            st.markdown(f"""
            <div class="activity-item">
                <span class="activity-name">{name}</span> - {role}
                <span class="activity-time">{timestamp}</span>
            </div>
            """, unsafe_allow_html=True)

def render_suggestions_section(suggestions, title="Suggestions"):
    if not suggestions:
        return
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    for s in suggestions:
        st.markdown(f'<div class="suggestion-item">• {s}</div>', unsafe_allow_html=True)

def apply_custom_css():
    with open('style/style.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
