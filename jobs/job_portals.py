JOB_PORTALS = {
    "LinkedIn": {
        "url": "https://www.linkedin.com/jobs/",
        "description": "Professional networking and job search platform",
        "features": ["Easy Apply", "Salary insights", "Company reviews", "Network referrals"],
        "icon": "🔗"
    },
    "Indeed": {
        "url": "https://www.indeed.com/",
        "description": "World's largest job search engine",
        "features": ["Millions of jobs", "Company ratings", "Salary tools", "Remote filters"],
        "icon": "💼"
    },
    "Glassdoor": {
        "url": "https://www.glassdoor.com/",
        "description": "Jobs with company insights and reviews",
        "features": ["Company reviews", "Salary reports", "Interview tips", "Benefits info"],
        "icon": "🏢"
    },
    "Naukri": {
        "url": "https://www.naukri.com/",
        "description": "India's #1 job portal",
        "features": ["Recruiter connect", "Job alerts", "Resume display", "Skill tests"],
        "icon": "🇮🇳"
    },
    "AngelList": {
        "url": "https://angel.co/jobs",
        "description": "Startup and tech job marketplace",
        "features": ["Startup focus", "Equity info", "Direct apply", "Salary ranges"],
        "icon": "🚀"
    },
    "Remote OK": {
        "url": "https://remoteok.com/",
        "description": "Curated remote jobs worldwide",
        "features": ["Fully remote", "Global positions", "Tech focused", "No spam"],
        "icon": "🏠"
    },
    "Monster": {
        "url": "https://www.monster.com/",
        "description": "Global employment platform",
        "features": ["Career advice", "Resume services", "Job alerts", "Salary tools"],
        "icon": "👹"
    }
}

CAREER_RESOURCES = {
    "Resume Writing": [
        {"title": "How to Write a Resume That Stands Out", "url": "https://www.indeed.com/career-advice/resumes-cover-letters"},
        {"title": "ATS-Friendly Resume Tips", "url": "https://www.jobscan.co/"},
        {"title": "Professional Resume Examples", "url": "https://www.zety.com/resume-examples"}
    ],
    "Interview Preparation": [
        {"title": "Common Interview Questions", "url": "https://www.glassdoor.com/blog/common-interview-questions/"},
        {"title": "STAR Method Interviewing", "url": "https://www.themuse.com/advice/star-interview-method"},
        {"title": "Technical Interview Prep", "url": "https://leetcode.com/"}
    ],
    "Skill Development": [
        {"title": "Free Online Courses", "url": "https://www.coursera.org/"},
        {"title": "Coding Bootcamps", "url": "https://www.codecademy.com/"},
        {"title": "Professional Certifications", "url": "https://www.udemy.com/"}
    ],
    "Career Planning": [
        {"title": "Career Path Guides", "url": "https://www.careeronestop.org/"},
        {"title": "Salary Negotiation", "url": "https://www.kalzumeus.com/2012/01/23/salary-negotiation/"},
        {"title": "Networking Tips", "url": "https://www.forbes.com/sites/forbescoachescouncil/2022/01/13/networking-tips/"}
    ]
}

def get_portal_search_url(portal_name, keyword, location=""):
    portal = JOB_PORTALS.get(portal_name)
    if not portal:
        return "#"
    base_url = portal['url']
    if portal_name == "LinkedIn":
        return f"{base_url}?keywords={keyword}&location={location}"
    elif portal_name == "Indeed":
        return f"{base_url}?q={keyword}&l={location}"
    elif portal_name == "Glassdoor":
        return f"{base_url}?keyword={keyword}&locT=C&locId={location}"
    elif portal_name == "Naukri":
        return f"{base_url}{keyword}-jobs-in-{location}"
    return base_url
