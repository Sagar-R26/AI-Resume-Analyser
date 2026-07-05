import streamlit as st
from jobs.companies import (FEATURED_COMPANIES, JOB_PORTALS, INDUSTRY_INSIGHTS,
                              get_companies_by_sector, get_all_sectors)
from jobs.linkedin_scraper import search_linkedin_jobs
from jobs.suggestions import get_job_suggestions, get_career_recommendations, get_all_roles
from jobs.job_portals import JOB_PORTALS as PORTAL_DATA, CAREER_RESOURCES, get_portal_search_url
import random

class JobSearchManager:
    def __init__(self):
        if 'job_search_results' not in st.session_state:
            st.session_state.job_search_results = []
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

    def show_job_search_ui(self):
        st.markdown("<h1>Job Search & Career Resources</h1>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Search Jobs", "Featured Companies",
            "Industry Insights", "Career Resources"
        ])

        with tab1:
            self.show_search_tab()

        with tab2:
            self.show_companies_tab()

        with tab3:
            self.show_insights_tab()

        with tab4:
            self.show_resources_tab()

    def show_search_tab(self):
        st.markdown("<h2>Search for Jobs</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            keyword = st.text_input("Job Title / Keywords",
                placeholder="e.g., Python Developer, Data Scientist...")
        with col2:
            location = st.text_input("Location", placeholder="e.g., Remote, New York...")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            portal = st.selectbox("Job Portal", list(PORTAL_DATA.keys()))
        with col2:
            job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Internship", "Remote"])
        with col3:
            num_results = st.number_input("Results", min_value=5, max_value=50, value=10)

        if st.button("Search Jobs", use_container_width=True):
            with st.spinner("Searching for jobs..."):
                if keyword:
                    results = search_linkedin_jobs(keyword, location, num_results)
                    st.session_state.job_search_results = results
                else:
                    st.warning("Please enter a search keyword")

        if st.session_state.job_search_results:
            self.display_job_results(st.session_state.job_search_results)

        if portal and keyword:
            portal_url = get_portal_search_url(portal, keyword, location)
            st.markdown(f"<a href='{portal_url}' target='_blank' class='portal-link'>Search on {portal} →</a>",
                       unsafe_allow_html=True)

    def display_job_results(self, jobs):
        st.markdown(f"<h3>Found {len(jobs)} Jobs</h3>", unsafe_allow_html=True)
        for job in jobs:
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <h4>{job.get('title', 'Unknown Position')}</h4>
                    <p><strong>Company:</strong> {job.get('company', 'Unknown')}</p>
                    <p><strong>Location:</strong> {job.get('location', 'Remote')}</p>
                    <p><strong>Platform:</strong> {job.get('platform', 'LinkedIn')}</p>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"<a href='{job.get('url', '#')}' target='_blank'>Apply on {job.get('platform', 'LinkedIn')}</a>",
                              unsafe_allow_html=True)
                with col2:
                    if st.button(f"Save Job", key=f"save_{job.get('title')}_{random.randint(0, 9999)}"):
                        st.info("Job saved to favorites!")
                st.markdown("---")

    def show_companies_tab(self):
        st.markdown("<h2>Featured Companies</h2>", unsafe_allow_html=True)

        sectors = get_all_sectors()
        selected_sector = st.selectbox("Filter by Sector", ["All"] + sectors)

        companies = get_companies_by_sector(None)
        if selected_sector != "All":
            companies = get_companies_by_sector(selected_sector)

        cols = st.columns(3)
        for idx, company in enumerate(companies):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="company-card">
                    <div class="company-logo">{company['logo']}</div>
                    <h4>{company['name']}</h4>
                    <p>{company['description']}</p>
                    <a href="{company['careers_url']}" target="_blank">View Careers →</a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<h3>Top Job Portals</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, (portal_name, portal_info) in enumerate(JOB_PORTALS.items()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="company-card">
                    <div class="company-logo">{portal_info['icon']}</div>
                    <h4>{portal_name}</h4>
                    <p>{portal_info['description']}</p>
                    <a href="{portal_info['url']}" target="_blank">Visit Portal →</a>
                </div>
                """, unsafe_allow_html=True)

    def show_insights_tab(self):
        st.markdown("<h2>Industry Insights</h2>", unsafe_allow_html=True)
        st.markdown("Stay informed with the latest trends and growth projections in your industry.")

        for insight in INDUSTRY_INSIGHTS:
            with st.expander(f"{insight['sector']} - Growth: {insight['growth']}"):
                st.markdown(f"**Projected Growth:** {insight['growth']}")
                st.markdown("**Top Trends:**")
                for trend in insight['trends']:
                    st.markdown(f"• {trend}")
                st.markdown("**In-Demand Skills:**")
                for skill in insight['top_skills']:
                    st.markdown(f"• {skill}")

    def show_resources_tab(self):
        st.markdown("<h2>Career Resources</h2>", unsafe_allow_html=True)

        for resource_type, resources in CAREER_RESOURCES.items():
            st.markdown(f"<h3>{resource_type}</h3>", unsafe_allow_html=True)
            cols = st.columns(len(resources))
            for idx, resource in enumerate(resources):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="company-card">
                        <h4>{resource['title']}</h4>
                        <a href="{resource['url']}" target="_blank">Learn More →</a>
                    </div>
                    """, unsafe_allow_html=True)
