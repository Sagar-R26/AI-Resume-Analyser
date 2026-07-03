import re
import pdfplumber
from collections import Counter

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'shall', 'can', 'need',
    'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
    'we', 'us', 'our', 'you', 'your', 'he', 'she', 'him', 'her', 'his',
    'not', 'no', 'nor', 'so', 'if', 'then', 'than', 'too', 'very', 'just',
    'about', 'above', 'after', 'again', 'all', 'also', 'any', 'because',
    'been', 'before', 'between', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'only', 'own', 'same', 'into', 'over', 'under',
    'up', 'out', 'off', 'down', 'here', 'there', 'when', 'where', 'why',
    'how', 'what', 'which', 'who', 'whom', 'while', 'during', 'through',
    'ago', 'ever', 'never', 'now', 'once', 'since', 'until', 'yet',
}

KNOWN_LOCATIONS = {
    'new york', 'san francisco', 'los angeles', 'chicago', 'houston',
    'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas',
    'austin', 'seattle', 'denver', 'boston', 'nashville', 'portland',
    'miami', 'atlanta', 'washington dc', 'london', 'berlin', 'paris',
    'sydney', 'toronto', 'vancouver', 'mumbai', 'delhi', 'bangalore',
    'hyderabad', 'chennai', 'pune', 'kolkata', 'dubai', 'singapore',
    'hong kong', 'tokyo', 'shanghai', 'beijing', 'amsterdam', 'dublin',
    'barcelona', 'madrid', 'rome', 'milan', 'zurich', 'stockholm',
    'oslo', 'copenhagen', 'helsinki', 'auckland', 'melbourne', 'brisbane',
    'united states', 'united kingdom', 'india', 'canada', 'australia',
    'germany', 'france', 'spain', 'italy', 'netherlands', 'switzerland',
    'sweden', 'norway', 'denmark', 'finland', 'japan', 'china', 'south korea',
    'brazil', 'mexico', 'usa', 'uk',
}


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_contact_info(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    email = emails[0] if emails else None
    phone = phones[0] if phones else None

    name = _extract_name(text)
    location = _extract_location(text)

    return name, email, phone, location


def _extract_name(text):
    lines = text.split('\n')
    for line in lines[:15]:
        line = line.strip()
        if not line or len(line) > 40:
            continue
        words = line.split()
        if len(words) < 2 or len(words) > 5:
            continue
        if all(w[0].isupper() for w in words if w[0].isalpha()):
            has_lower = any(w[0].islower() for w in words if w[0].isalpha())
            if not has_lower and not re.search(r'[@#\$%^&*()_+=<>]', line):
                return line.strip()
    return None


def _extract_location(text):
    text_lower = text.lower()
    found = []
    for loc in KNOWN_LOCATIONS:
        if loc in text_lower:
            found.append(loc.title())
    if found:
        return found[0]

    lines = text.split('\n')
    for line in lines[:20]:
        line_clean = line.strip().strip(',.').strip()
        if len(line_clean) < 3 or len(line_clean) > 60:
            continue
        if re.match(r'^[A-Z][a-zA-Z\s,.]+$', line_clean):
            words = line_clean.split()
            if len(words) <= 4:
                return line_clean
    return None


def extract_skills(text):
    text_lower = text.lower()
    found_skills = set()
    for skill in SKILLS_DB:
        if skill in text_lower:
            found_skills.add(skill)
    return sorted(found_skills)


def extract_keywords(text):
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    words = [w for w in words if w not in STOPWORDS]
    word_freq = Counter(words)
    return word_freq.most_common(30)


def extract_education(text):
    patterns = [
        r'(?:B\.?\s*[ATechBE]\.?\s*(?:[Ee]ng\.?)?(?:\s*\([^)]*\))?)',
        r'(?:M\.?\s*[STechA]\.?\s*(?:[Ee]ng\.?)?(?:\s*\([^)]*\))?)',
        r'(?:PhD|Ph\.D\.|Doctorate)',
        r'(?:Bachelor[’\']?s?(?:\s+of\s+|\s+in\s+)?\w+(?:\s+\w+)?)',
        r'(?:Master[’\']?s?(?:\s+of\s+|\s+in\s+)?\w+(?:\s+\w+)?)',
        r'(?:B\.\s*[AE]\.)',
        r'(?:M\.\s*[BC]\.?\s*[ATech]?)',
        r'MBA',
        r'(?:Associate[’\']?s?\s+(?:of\s+)?\w+)',
        r'(?:Diploma\s+in\s+\w+)',
        r'(?:B\.Com|M\.Com|BBA|MBA|BCA|MCA)',
    ]
    found_education = []
    lines = text.split('\n')
    for line in lines:
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                found_education.append(line.strip())
                break
    return found_education[:5]


def extract_experience_years(text):
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        r'(?:experience|exp)\s*(?:of|:)?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*\+\s*(?:years?|yrs?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0


SKILLS_DB = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
    'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'sql', 'html',
    'css', 'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js',
    'express', 'fastapi', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'docker', 'kubernetes', 'aws',
    'azure', 'gcp', 'git', 'linux', 'redis', 'mongodb', 'postgresql', 'mysql',
    'graphql', 'rest', 'api', 'machine learning', 'deep learning', 'nlp',
    'computer vision', 'data science', 'data analysis', 'data engineering',
    'devops', 'ci/cd', 'agile', 'scrum', 'jira', 'tableau', 'power bi',
    'excel', 'spark', 'hadoop', 'kafka', 'airflow', 'jenkins', 'terraform',
    'ansible', 'prometheus', 'grafana', 'elasticsearch', 'logstash', 'kibana',
    'figma', 'sketch', 'photoshop', 'illustrator', 'ui/ux', 'product management',
    'project management', 'leadership', 'communication', 'teamwork',
    'problem solving', 'critical thinking', 'time management', 'public speaking',
    'salesforce', 'sap', 'oracle', 'blockchain', 'cybersecurity', 'networking',
}

JOB_ROLES = {
    'software engineer': ['python', 'java', 'c++', 'javascript', 'git', 'docker', 'kubernetes', 'aws', 'agile', 'rest', 'api'],
    'data scientist': ['python', 'r', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'sql', 'statistics'],
    'data analyst': ['sql', 'excel', 'python', 'tableau', 'power bi', 'pandas', 'numpy', 'data analysis', 'statistics'],
    'web developer': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'rest'],
    'devops engineer': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'git'],
    'product manager': ['agile', 'scrum', 'jira', 'product management', 'leadership', 'communication', 'teamwork'],
    'machine learning engineer': ['python', 'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'docker', 'aws'],
    'backend developer': ['python', 'java', 'node.js', 'django', 'flask', 'spring', 'sql', 'mongodb', 'redis', 'docker', 'rest'],
    'frontend developer': ['html', 'css', 'javascript', 'typescript', 'react', 'angular', 'vue', 'rest', 'api', 'figma'],
    'full stack developer': ['html', 'css', 'javascript', 'react', 'node.js', 'python', 'sql', 'mongodb', 'docker', 'git', 'rest'],
    'cybersecurity analyst': ['cybersecurity', 'networking', 'linux', 'python', 'aws', 'azure', 'risk assessment'],
}

COURSES = {
    'python': 'Python for Everybody (Coursera)',
    'machine learning': 'Machine Learning by Andrew Ng (Coursera)',
    'deep learning': 'Deep Learning Specialization (Coursera)',
    'data science': 'Data Science Professional Certificate (IBM - Coursera)',
    'web development': 'The Complete Web Developer Bootcamp (Udemy)',
    'react': 'React - The Complete Guide (Udemy)',
    'aws': 'AWS Certified Solutions Architect (Udemy/Coursera)',
    'docker': 'Docker Mastery (Udemy)',
    'kubernetes': 'Kubernetes for Developers (Udemy)',
    'sql': 'SQL for Data Science (Coursera)',
    'devops': 'DevOps Bootcamp (Udemy)',
    'nlp': 'Natural Language Processing with Python (Coursera)',
    'tensorflow': 'TensorFlow Developer Certificate (Coursera)',
    'pytorch': 'PyTorch for Deep Learning (Udemy)',
    'tableau': 'Tableau 2024 A-Z (Udemy)',
    'product management': 'Product Management Certification (Coursera)',
    'cybersecurity': 'Cybersecurity Professional Certificate (Google - Coursera)',
    'project management': 'Google Project Management Certificate (Coursera)',
}

VIDEOS = [
    {'title': 'How to Write a Killer Resume', 'url': 'https://www.youtube.com/watch?v=Tt08KmFfIYQ'},
    {'title': 'Resume Tips from Recruiters', 'url': 'https://www.youtube.com/watch?v=5fzTrS3uKtE'},
    {'title': 'Top Interview Tips', 'url': 'https://www.youtube.com/watch?v=HG68Ymzo18E'},
    {'title': '5 Resume Mistakes to Avoid', 'url': 'https://www.youtube.com/watch?v=h6LwUJ2BO00'},
    {'title': 'How to Talk About Your Experience', 'url': 'https://www.youtube.com/watch?v=J4n9GZ3TzT4'},
    {'title': 'Write an ATS-Friendly Resume', 'url': 'https://www.youtube.com/watch?v=u75hUs4v3iM'},
    {'title': 'LinkedIn Profile Optimization', 'url': 'https://www.youtube.com/watch?v=Z0lTqMlK8sQ'},
    {'title': 'Skills to Put on Your Resume', 'url': 'https://www.youtube.com/watch?v=5YqU7A-6h6o'},
    {'title': 'Common Interview Questions', 'url': 'https://www.youtube.com/watch?v=1mHjMNZZvFo'},
    {'title': 'Negotiating Your Salary', 'url': 'https://www.youtube.com/watch?v=XY5F8p1J4pA'},
]
