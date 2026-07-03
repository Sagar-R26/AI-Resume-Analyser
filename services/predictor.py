from .nlp_parser import SKILLS_DB, JOB_ROLES


def predict_job_role(skills):
    if not skills:
        return "General / Entry Level"

    skill_set = set(skills)
    role_scores = {}
    for role, required_skills in JOB_ROLES.items():
        req_set = set(required_skills)
        if not req_set:
            continue
        overlap = len(skill_set & req_set)
        score = overlap / len(req_set)
        role_scores[role] = score

    if not role_scores:
        return "General / Entry Level"

    best_role = max(role_scores, key=role_scores.get)
    best_score = role_scores[best_role]

    if best_score < 0.15:
        return "General / Entry Level"

    return best_role.title()
