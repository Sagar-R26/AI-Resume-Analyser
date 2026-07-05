from config.job_roles import JOB_ROLES
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS

def get_job_suggestions(skills):
    if not skills:
        return []
    suggestions = []
    skills_lower = [s.lower() for s in skills]
    for category, roles in JOB_ROLES.items():
        for role_name, role_info in roles.items():
            required = role_info.get('required_skills', [])
            matched = sum(1 for rs in required if rs.lower() in ' '.join(skills_lower))
            if matched >= len(required) * 0.3:
                suggestions.append({
                    'role': role_name,
                    'category': category,
                    'match_percentage': round((matched / len(required)) * 100, 1),
                    'description': role_info.get('description', ''),
                    'missing_skills': [s for s in required if s.lower() not in ' '.join(skills_lower)]
                })
    suggestions.sort(key=lambda x: x['match_percentage'], reverse=True)
    return suggestions[:5]

def get_career_recommendations(job_role):
    recommendations = {'courses': [], 'resume_videos': [], 'interview_videos': []}
    for category, roles in COURSES_BY_CATEGORY.items():
        if job_role in roles:
            recommendations['courses'] = roles[job_role]
            break
    recommendations['resume_videos'] = []
    for section, videos in RESUME_VIDEOS.items():
        recommendations['resume_videos'].extend(videos)
    recommendations['interview_videos'] = []
    for section, videos in INTERVIEW_VIDEOS.items():
        recommendations['interview_videos'].extend(videos)
    return recommendations

def get_role_requirements(job_role):
    for category, roles in JOB_ROLES.items():
        if job_role in roles:
            return roles[job_role]
    return None

def get_all_roles():
    roles = []
    for category, category_roles in JOB_ROLES.items():
        for role_name in category_roles:
            roles.append({'name': role_name, 'category': category})
    return roles
