import streamlit as st
from config.database import (get_resume_stats, get_admin_logs, log_admin_action,
                              get_detailed_ai_analysis_stats, reset_ai_analysis_stats,
                              get_all_resume_data, verify_admin)
from dashboard.components import DashboardComponents

class DashboardManager:
    def __init__(self):
        self.components = DashboardComponents()

    def show_admin_login(self):
        st.markdown("<h2>Admin Login</h2>", unsafe_allow_html=True)
        with st.form("admin_login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("Login", use_container_width=True)
            with col2:
                if st.form_submit_button("Register", use_container_width=True):
                    st.session_state.show_register = True

            if submitted:
                if verify_admin(email, password):
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_email = email
                    log_admin_action(email, "Admin logged in")
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    def show_register(self):
        st.markdown("<h2>Admin Registration</h2>", unsafe_allow_html=True)
        with st.form("admin_register_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Register", use_container_width=True):
                if password != confirm:
                    st.error("Passwords do not match")
                elif not email or not password:
                    st.error("All fields are required")
                else:
                    from config.database import add_admin
                    if add_admin(email, password):
                        st.success("Admin registered successfully! Please login.")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error("Registration failed")

    def show_dashboard_ui(self):
        st.markdown("<h1>Analytics Dashboard</h1>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Overview", "AI Analysis Stats", "Admin Panel"])

        with tab1:
            self.show_overview_tab()

        with tab2:
            self.show_ai_analysis_tab()

        with tab3:
            self.show_admin_panel()

    def show_overview_tab(self):
        stats = get_resume_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                self.components.render_metric_card("Total Resumes", stats.get('total_resumes', 0), "📄")
            with col2:
                self.components.render_metric_card("Avg ATS Score", f"{stats.get('avg_ats_score', 0):.1f}%", "🎯")
            with col3:
                self.components.render_metric_card("Active Now", "Live", "✅")

        st.markdown("<h3>Recent Activity</h3>", unsafe_allow_html=True)
        if stats and stats.get('recent_activity'):
            for act in stats['recent_activity']:
                name, role, ts = act[0], act[1], act[2]
                st.markdown(f"""
                <div class="activity-item">
                    <strong>{name}</strong> applied for <em>{role}</em>
                    <span style="color: #888; float: right;">{ts}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity")

    def show_ai_analysis_tab(self):
        stats = get_detailed_ai_analysis_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            self.components.render_metric_card("Total Analyses", stats.get('total_analyses', 0), "🤖")
        with col2:
            self.components.render_metric_card("Avg Score", f"{stats.get('average_score', 0):.1f}%", "📊")
        with col3:
            self.components.render_metric_card("Models Used", len(stats.get('model_usage', [])), "🧠")
        with col4:
            self.components.render_metric_card("Top Roles", len(stats.get('top_job_roles', [])), "🏆")

        if stats.get('model_usage'):
            st.markdown("<h3>Model Usage Distribution</h3>", unsafe_allow_html=True)
            labels = [m['model'] for m in stats['model_usage']]
            values = [m['count'] for m in stats['model_usage']]
            self.components.render_pie_chart(labels, values, "Model Usage")

        if stats.get('daily_trend'):
            st.markdown("<h3>Daily Trend (Last 7 Days)</h3>", unsafe_allow_html=True)
            dates = [d['date'] for d in stats['daily_trend']]
            counts = [d['count'] for d in stats['daily_trend']]
            self.components.render_line_chart(dates, counts, "Daily Analyses")

        if stats.get('score_distribution'):
            st.markdown("<h3>Score Distribution</h3>", unsafe_allow_html=True)
            ranges = [s['range'] for s in stats['score_distribution']]
            counts = [s['count'] for s in stats['score_distribution']]
            self.components.render_bar_chart(ranges, counts, "Score Ranges")

        if stats.get('recent_analyses'):
            st.markdown("<h3>Recent AI Analyses</h3>", unsafe_allow_html=True)
            for ra in stats['recent_analyses']:
                st.markdown(f"""
                <div class="activity-item">
                    <strong>{ra.get('job_role', 'N/A')}</strong> - Score: {ra.get('score', 0)}%
                    <span style="color: #888;">{ra.get('date', '')}</span>
                </div>
                """, unsafe_allow_html=True)

    def show_admin_panel(self):
        st.markdown("<h3>Admin Actions</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset AI Analysis Stats", use_container_width=True):
                result = reset_ai_analysis_stats()
                if result.get('success'):
                    st.success(result.get('message'))
                    st.rerun()
                else:
                    st.error(result.get('message'))

        with col2:
            if st.button("Refresh Dashboard", use_container_width=True):
                st.rerun()

        st.markdown("<h3>Resume Data</h3>", unsafe_allow_html=True)
        all_data = get_all_resume_data()
        if all_data:
            import pandas as pd
            df = pd.DataFrame(all_data, columns=[
                'ID', 'Name', 'Email', 'Phone', 'LinkedIn', 'GitHub', 'Portfolio',
                'Target Role', 'Target Category', 'Created At',
                'ATS Score', 'Keyword Match', 'Format Score', 'Section Score'
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No resume data found")

        st.markdown("<h3>Admin Logs</h3>", unsafe_allow_html=True)
        logs = get_admin_logs()
        if logs:
            for log in logs:
                admin_email, action, timestamp = log
                st.markdown(f"""
                <div class="activity-item">
                    <strong>{admin_email}</strong> - {action}
                    <span style="color: #888; float: right;">{timestamp}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No admin logs found")
