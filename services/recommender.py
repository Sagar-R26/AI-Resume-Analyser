from .nlp_parser import COURSES, VIDEOS, SKILLS_DB


def recommend_courses(skills, suggested_skills):
    recommendations = []
    all_skill_names = {s.lower() for s in skills}

    if suggested_skills:
        for sk in suggested_skills:
            sk_lower = sk.lower()
            if sk_lower in COURSES and sk_lower not in all_skill_names:
                recommendations.append({
                    'skill': sk_lower,
                    'course': COURSES[sk_lower],
                })

    if not recommendations:
        for skill, course in COURSES.items():
            if skill not in all_skill_names:
                if len(recommendations) < 4:
                    recommendations.append({
                        'skill': skill,
                        'course': course,
                    })
    return recommendations[:5]


def recommend_videos():
    return VIDEOS


def get_suggested_skills(skills):
    skill_set = set(skills)
    trending = [
        'python', 'docker', 'kubernetes', 'aws', 'machine learning',
        'react', 'sql', 'git', 'devops', 'tensorflow', 'node.js',
        'typescript', 'ci/cd', 'terraform', 'nlp',
    ]
    missing = [s for s in trending if s not in skill_set]
    return missing[:6]
