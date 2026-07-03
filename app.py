import os
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, jsonify, send_file)
import mysql.connector
from mysql.connector import Error
import io
import csv

from config import Config
from services.nlp_parser import (
    extract_text_from_pdf, extract_contact_info, extract_skills,
    extract_keywords, extract_education, extract_experience_years
)
from services.scorer import calculate_resume_score, get_score_grade, generate_suggestions
from services.predictor import predict_job_role
from services.recommender import recommend_courses, recommend_videos, get_suggested_skills

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def get_db():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
    )


def init_db():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS resume_analyzer")
        cursor.close()
        conn.database = app.config['MYSQL_DB']
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) DEFAULT NULL,
                email VARCHAR(255) DEFAULT NULL,
                phone VARCHAR(50) DEFAULT NULL,
                extracted_text LONGTEXT,
                skills TEXT,
                keywords TEXT,
                score INT DEFAULT 0,
                predicted_role VARCHAR(255) DEFAULT NULL,
                suggested_skills TEXT,
                experience_years DECIMAL(4,1) DEFAULT 0,
                education TEXT,
                location VARCHAR(255) DEFAULT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM admins WHERE username='admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admins (username, password_hash) VALUES ('admin', 'admin123')")
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"DB Init Error: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please login first.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash("No file selected.", "danger")
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash("No file selected.", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Only PDF files are allowed.", "danger")
            return redirect(request.url)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            text = extract_text_from_pdf(filepath)

            name, email, phone, location = extract_contact_info(text)
            skills = extract_skills(text)
            keywords = extract_keywords(text)
            education = extract_education(text)
            experience_years = extract_experience_years(text)

            score = calculate_resume_score(
                skills, experience_years, education, len(text),
                bool(email), bool(phone), bool(name)
            )
            grade, grade_color = get_score_grade(score)
            predicted_role = predict_job_role(skills)
            suggested_skills = get_suggested_skills(skills)
            suggestions = generate_suggestions(skills, predicted_role, score)
            courses = recommend_courses(skills, suggested_skills)
            videos = recommend_videos()

            keywords_str = ", ".join([f"{k[0]}:{k[1]}" for k in keywords[:20]])
            skills_str = ", ".join(skills)
            education_str = " | ".join(education)
            suggested_str = ", ".join(suggested_skills)

            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO resumes
                    (filename, full_name, email, phone, extracted_text, skills,
                     keywords, score, predicted_role, suggested_skills,
                     experience_years, education, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    file.filename, name, email, phone, text, skills_str,
                    keywords_str, score, predicted_role, suggested_str,
                    experience_years, education_str, location
                ))
                conn.commit()
                cursor.close()
                conn.close()
            except Error as e:
                print(f"DB Error: {e}")

            return render_template('result.html',
                filename=file.filename,
                name=name,
                email=email,
                phone=phone,
                location=location,
                skills=skills,
                score=score,
                grade=grade,
                grade_color=grade_color,
                predicted_role=predicted_role,
                suggested_skills=suggested_skills,
                suggestions=suggestions,
                courses=courses,
                videos=videos,
                education=education,
                experience_years=experience_years,
            )

        except Exception as e:
            flash(f"Error processing resume: {str(e)}", "danger")
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE username=%s AND password_hash=%s", (username, password))
            admin = cursor.fetchone()
            cursor.close()
            conn.close()
            if admin:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash("Logged in successfully.", "success")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid credentials.", "danger")
        except Error as e:
            flash(f"Database error: {e}", "danger")
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("Logged out.", "info")
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    stats = {'total': 0, 'avg_score': 0, 'top_role': 'N/A', 'total_skills': 0}
    role_counts = {}
    location_counts = {}
    scores = []
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM resumes")
        stats['total'] = cursor.fetchone()['total']

        cursor.execute("SELECT AVG(score) as avg_score FROM resumes")
        row = cursor.fetchone()
        stats['avg_score'] = round(row['avg_score'], 1) if row and row['avg_score'] else 0

        cursor.execute("SELECT predicted_role FROM resumes WHERE predicted_role IS NOT NULL")
        for row in cursor.fetchall():
            role = row['predicted_role']
            role_counts[role] = role_counts.get(role, 0) + 1

        cursor.execute("SELECT location FROM resumes WHERE location IS NOT NULL AND location != ''")
        for row in cursor.fetchall():
            loc = row['location']
            location_counts[loc] = location_counts.get(loc, 0) + 1

        cursor.execute("SELECT score FROM resumes")
        scores = [row['score'] for row in cursor.fetchall()]

        if role_counts:
            stats['top_role'] = max(role_counts, key=role_counts.get)

        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "danger")

    role_data = [{'role': k, 'count': v} for k, v in sorted(role_counts.items(), key=lambda x: x[1], reverse=True)]
    location_data = [{'location': k, 'count': v} for k, v in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)]

    return render_template('admin/dashboard.html',
        stats=stats,
        role_data=role_data,
        location_data=location_data,
        scores=scores,
    )


@app.route('/admin/resumes')
@login_required
def admin_resumes():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    resumes = []
    total = 0
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM resumes")
        total = cursor.fetchone()['total']
        cursor.execute("""
            SELECT id, filename, full_name, email, score, predicted_role,
                   experience_years, location, uploaded_at
            FROM resumes ORDER BY uploaded_at DESC LIMIT %s OFFSET %s
        """, (per_page, offset))
        resumes = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "danger")

    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template('admin/resumes.html', resumes=resumes,
        page=page, total_pages=total_pages, total=total)


@app.route('/admin/resumes/<int:resume_id>')
@login_required
def admin_resume_detail(resume_id):
    resume = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM resumes WHERE id=%s", (resume_id,))
        resume = cursor.fetchone()
        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "danger")
    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for('admin_resumes'))
    return render_template('admin/resume_detail.html', resume=resume)


@app.route('/admin/resumes/download')
@login_required
def admin_download_csv():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM resumes ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for('admin_resumes'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Filename', 'Full Name', 'Email', 'Phone', 'Skills', 'Score',
                     'Predicted Role', 'Suggested Skills', 'Experience Years',
                     'Education', 'Location', 'Uploaded At'])
    for r in rows:
        writer.writerow([
            r['id'], r['filename'], r['full_name'], r['email'], r['phone'],
            r['skills'], r['score'], r['predicted_role'], r['suggested_skills'],
            r['experience_years'], r['education'], r['location'], r['uploaded_at'],
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'resumes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
    )


@app.route('/admin/analytics')
@login_required
def admin_analytics():
    return admin_dashboard()


@app.route('/api/resume/<int:resume_id>')
def api_resume(resume_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, filename, full_name, email, phone, skills, score, "
                       "predicted_role, experience_years, location, uploaded_at "
                       "FROM resumes WHERE id=%s", (resume_id,))
        resume = cursor.fetchone()
        cursor.close()
        conn.close()
        if resume:
            return jsonify(resume)
        return jsonify({'error': 'Not found'}), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
