import sqlite3
from datetime import datetime

def get_database_connection():
    conn = sqlite3.connect('resume_data.db')
    return conn

def init_database():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        summary TEXT,
        target_role TEXT,
        target_category TEXT,
        education TEXT,
        experience TEXT,
        projects TEXT,
        skills TEXT,
        template TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT NOT NULL,
        skill_category TEXT NOT NULL,
        proficiency_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        ats_score REAL,
        keyword_match_score REAL,
        format_score REAL,
        section_score REAL,
        missing_skills TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume_data (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_resume_data(data):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        personal_info = data.get('personal_info', {})
        
        cursor.execute('''
        INSERT INTO resume_data (
            name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education, 
            experience, projects, skills, template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            personal_info.get('full_name', ''),
            personal_info.get('email', ''),
            personal_info.get('phone', ''),
            personal_info.get('linkedin', ''),
            personal_info.get('github', ''),
            personal_info.get('portfolio', ''),
            data.get('summary', ''),
            data.get('target_role', ''),
            data.get('target_category', ''),
            str(data.get('education', [])),
            str(data.get('experience', [])),
            str(data.get('projects', [])),
            str(data.get('skills', [])),
            data.get('template', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving resume data: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()

def save_analysis_data(resume_id, analysis):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving analysis data: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def get_resume_stats():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM resume_data')
        total_resumes = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(ats_score) FROM resume_analysis')
        avg_ats_score = cursor.fetchone()[0] or 0
        
        cursor.execute('''
        SELECT name, target_role, created_at 
        FROM resume_data 
        ORDER BY created_at DESC 
        LIMIT 5
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'total_resumes': total_resumes,
            'avg_ats_score': round(avg_ats_score, 2),
            'recent_activity': recent_activity
        }
    except Exception as e:
        print(f"Error getting resume stats: {str(e)}")
        return None
    finally:
        conn.close()

def log_admin_action(admin_email, action):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO admin_logs (admin_email, action)
        VALUES (?, ?)
        ''', (admin_email, action))
        conn.commit()
    except Exception as e:
        print(f"Error logging admin action: {str(e)}")
    finally:
        conn.close()

def get_admin_logs():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT admin_email, action, timestamp
        FROM admin_logs
        ORDER BY timestamp DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting admin logs: {str(e)}")
        return []
    finally:
        conn.close()

def get_all_resume_data():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT 
            r.id, r.name, r.email, r.phone, r.linkedin, r.github, r.portfolio,
            r.target_role, r.target_category, r.created_at,
            a.ats_score, a.keyword_match_score, a.format_score, a.section_score
        FROM resume_data r
        LEFT JOIN resume_analysis a ON r.id = a.resume_id
        ORDER BY r.created_at DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting resume data: {str(e)}")
        return []
    finally:
        conn.close()

def verify_admin(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM admin WHERE email = ? AND password = ?', (email, password))
        result = cursor.fetchone()
        return bool(result)
    except Exception as e:
        print(f"Error verifying admin: {str(e)}")
        return False
    finally:
        conn.close()

def add_admin(email, password):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding admin: {str(e)}")
        return False
    finally:
        conn.close()

def save_ai_analysis_data(resume_id, analysis_data):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                model_used TEXT,
                resume_score INTEGER,
                job_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO ai_analysis (
                resume_id, model_used, resume_score, job_role
            ) VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get('model_used', ''),
            analysis_data.get('resume_score', 0),
            analysis_data.get('job_role', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving AI analysis data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_ai_analysis_stats():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0, "model_usage": [],
                "average_score": 0, "top_job_roles": []
            }
        
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis GROUP BY model_used ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis GROUP BY job_role ORDER BY count DESC LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles
        }
    except Exception as e:
        print(f"Error getting AI analysis stats: {e}")
        return {"total_analyses": 0, "model_usage": [], "average_score": 0, "top_job_roles": []}
    finally:
        conn.close()

def get_detailed_ai_analysis_stats():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {
                "total_analyses": 0, "model_usage": [], "average_score": 0,
                "top_job_roles": [], "daily_trend": [],
                "score_distribution": [], "recent_analyses": []
            }
        
        cursor.execute("SELECT COUNT(*) FROM ai_analysis")
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT model_used, COUNT(*) as count
            FROM ai_analysis GROUP BY model_used ORDER BY count DESC
        """)
        model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
        average_score = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT job_role, COUNT(*) as count
            FROM ai_analysis GROUP BY job_role ORDER BY count DESC LIMIT 5
        """)
        top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM ai_analysis
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at) ORDER BY date
        """)
        daily_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        score_ranges = [
            {"min": 0, "max": 20, "range": "0-20"},
            {"min": 21, "max": 40, "range": "21-40"},
            {"min": 41, "max": 60, "range": "41-60"},
            {"min": 61, "max": 80, "range": "61-80"},
            {"min": 81, "max": 100, "range": "81-100"}
        ]
        
        score_distribution = []
        for range_info in score_ranges:
            cursor.execute("""
                SELECT COUNT(*) FROM ai_analysis 
                WHERE resume_score >= ? AND resume_score <= ?
            """, (range_info["min"], range_info["max"]))
            count = cursor.fetchone()[0]
            score_distribution.append({"range": range_info["range"], "count": count})
        
        cursor.execute("""
            SELECT model_used, resume_score, job_role, datetime(created_at) as date
            FROM ai_analysis ORDER BY created_at DESC LIMIT 5
        """)
        recent_analyses = [
            {"model": row[0], "score": row[1], "job_role": row[2], "date": row[3]}
            for row in cursor.fetchall()
        ]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
            "top_job_roles": top_job_roles,
            "daily_trend": daily_trend,
            "score_distribution": score_distribution,
            "recent_analyses": recent_analyses
        }
    except Exception as e:
        print(f"Error getting detailed AI analysis stats: {e}")
        return {"total_analyses": 0, "model_usage": [], "average_score": 0,
                "top_job_roles": [], "daily_trend": [], "score_distribution": [], "recent_analyses": []}
    finally:
        conn.close()

def reset_ai_analysis_stats():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
        """)
        
        if not cursor.fetchone():
            return {"success": False, "message": "AI analysis table does not exist"}
        
        cursor.execute("DELETE FROM ai_analysis")
        conn.commit()
        
        return {"success": True, "message": "AI analysis statistics have been reset successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error resetting AI analysis stats: {e}")
        return {"success": False, "message": f"Error resetting AI analysis statistics: {str(e)}"}
    finally:
        conn.close()
