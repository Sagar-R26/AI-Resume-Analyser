def calculate_resume_score(skills, experience_years, education, text_length, has_email, has_phone, has_name):
    score = 0
    max_score = 100

    if has_email:
        score += 10
    if has_phone:
        score += 10
    if has_name:
        score += 5

    skills_count = len(skills)
    if skills_count >= 15:
        score += 25
    elif skills_count >= 10:
        score += 20
    elif skills_count >= 5:
        score += 15
    elif skills_count >= 3:
        score += 10
    elif skills_count > 0:
        score += 5

    if experience_years >= 10:
        score += 20
    elif experience_years >= 5:
        score += 15
    elif experience_years >= 2:
        score += 10
    elif experience_years > 0:
        score += 5

    if education:
        score += 10

    if 500 < text_length < 5000:
        score += 10
    elif text_length >= 5000:
        score += 5

    recency_bonus = 10
    if any(kw in ' '.join(skills).lower() for kw in ['tensorflow', 'pytorch', 'react', 'kubernetes', 'aws', 'docker', 'ai', 'machine learning', 'deep learning']):
        score += recency_bonus

    return min(score, max_score)


def get_score_grade(score):
    if score >= 85:
        return "Excellent", "success"
    elif score >= 70:
        return "Good", "primary"
    elif score >= 50:
        return "Average", "warning"
    else:
        return "Needs Improvement", "danger"


def generate_suggestions(skills, predicted_role, score):
    suggestions = []
    high_value_skills = {
        'docker', 'kubernetes', 'aws', 'git', 'python', 'sql',
        'machine learning', 'react', 'node.js', 'ci/cd', 'terraform',
        'jenkins', 'linux', 'rest', 'api', 'devops', 'agile',
    }
    missing_high_value = high_value_skills - set(skills)
    if missing_high_value:
        top_missing = list(missing_high_value)[:5]
        suggestions.append(f"Consider adding high-demand skills: {', '.join(top_missing)}")

    if score < 50:
        suggestions.append("Add more quantifiable achievements to your experience section.")
    elif score < 70:
        suggestions.append("Your resume is decent. Try adding more specific keywords and metrics.")

    if predicted_role:
        suggestions.append(f"Tailor your resume summary to target '{predicted_role}' roles.")

    suggestions.append("Ensure your resume is ATS-friendly by using standard section headings.")
    suggestions.append("Use action verbs (e.g., 'Developed', 'Implemented', 'Optimized').")

    return suggestions
