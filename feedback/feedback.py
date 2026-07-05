import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

def get_feedback_db():
    conn = sqlite3.connect('feedback/feedback.db')
    return conn

def init_feedback_db():
    conn = get_feedback_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        category TEXT,
        rating INTEGER,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def save_feedback(name, email, category, rating, message):
    conn = get_feedback_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO feedback (name, email, category, rating, message)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, email, category, rating, message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False
    finally:
        conn.close()

def get_all_feedback():
    conn = get_feedback_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
        return cursor.fetchall()
    except:
        return []
    finally:
        conn.close()

def get_feedback_stats():
    conn = get_feedback_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total = cursor.fetchone()[0] or 0
        cursor.execute('SELECT AVG(rating) FROM feedback')
        avg_rating = cursor.fetchone()[0] or 0
        cursor.execute('SELECT category, COUNT(*) FROM feedback GROUP BY category')
        categories = cursor.fetchall()
        return {
            'total': total,
            'avg_rating': round(avg_rating, 1),
            'categories': categories
        }
    except:
        return {'total': 0, 'avg_rating': 0, 'categories': []}
    finally:
        conn.close()

def export_feedback_csv():
    conn = get_feedback_db()
    try:
        df = pd.read_sql_query('SELECT * FROM feedback ORDER BY created_at DESC', conn)
        return df.to_csv(index=False).encode('utf-8')
    except:
        return None
    finally:
        conn.close()

class FeedbackManager:
    def __init__(self):
        init_feedback_db()

    def show_feedback_form(self):
        st.markdown("<h2>We Value Your Feedback</h2>", unsafe_allow_html=True)
        st.markdown("Help us improve this tool by sharing your experience.")

        with st.form("feedback_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name")
            with col2:
                email = st.text_input("Your Email (optional)")

            category = st.selectbox("Feedback Category", [
                "General Feedback", "Bug Report", "Feature Request",
                "Resume Analysis", "Resume Builder", "User Experience", "Other"
            ])

            rating = st.slider("Rating", 1, 5, 5, help="Rate your experience")

            message = st.text_area("Your Message", height=150,
                placeholder="Tell us about your experience...")

            if st.form_submit_button("Submit Feedback", use_container_width=True):
                if not name or not message:
                    st.error("Please fill in your name and message.")
                else:
                    if save_feedback(name, email, category, rating, message):
                        st.success("Thank you for your feedback!")
                        st.balloons()
                    else:
                        st.error("Failed to save feedback. Please try again.")

    def show_feedback_admin(self):
        st.markdown("<h2>Feedback Dashboard</h2>", unsafe_allow_html=True)

        stats = get_feedback_stats()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Feedback", stats['total'])
        with col2:
            st.metric("Average Rating", f"{stats['avg_rating']}/5")
        with col3:
            csv = export_feedback_csv()
            if csv:
                st.download_button(
                    label="Export CSV",
                    data=csv,
                    file_name=f"feedback_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        if stats['categories']:
            st.markdown("<h3>Feedback by Category</h3>", unsafe_allow_html=True)
            for cat, count in stats['categories']:
                st.markdown(f"**{cat}**: {count} entries")

        st.markdown("<h3>All Feedback</h3>", unsafe_allow_html=True)
        feedback_list = get_all_feedback()
        if feedback_list:
            for fb in feedback_list:
                with st.expander(f"#{fb[0]} - {fb[1]} ({fb[2]}) - {'⭐' * fb[4]}"):
                    st.markdown(f"**Category**: {fb[3]}")
                    st.markdown(f"**Rating**: {'⭐' * fb[4]}")
                    st.markdown(f"**Message**: {fb[5]}")
                    st.markdown(f"**Date**: {fb[6]}")
        else:
            st.info("No feedback yet")
