FEATURED_COMPANIES = {
    "Technology": [
        {"name": "Google", "logo": "🔍", "description": "Search and cloud computing giant",
         "careers_url": "https://careers.google.com/"},
        {"name": "Microsoft", "logo": "🪟", "description": "Software and cloud services leader",
         "careers_url": "https://careers.microsoft.com/"},
        {"name": "Amazon", "logo": "📦", "description": "E-commerce and cloud computing",
         "careers_url": "https://amazon.jobs/"},
        {"name": "Apple", "logo": "🍎", "description": "Consumer electronics and software",
         "careers_url": "https://apple.com/careers/"},
        {"name": "Meta", "logo": "🌐", "description": "Social media and technology",
         "careers_url": "https://metacareers.com/"}
    ],
    "Finance": [
        {"name": "JPMorgan Chase", "logo": "🏦", "description": "Investment banking and financial services",
         "careers_url": "https://jpmorganchase.com/careers/"},
        {"name": "Goldman Sachs", "logo": "💼", "description": "Investment banking and securities",
         "careers_url": "https://goldmansachs.com/careers/"}
    ],
    "Consulting": [
        {"name": "McKinsey & Company", "logo": "📊", "description": "Management consulting",
         "careers_url": "https://mckinsey.com/careers/"},
        {"name": "Boston Consulting Group", "logo": "📈", "description": "Strategy consulting",
         "careers_url": "https://bcg.com/careers/"}
    ],
    "Startups": [
        {"name": "Stripe", "logo": "💳", "description": "Online payment processing",
         "careers_url": "https://stripe.com/jobs/"},
        {"name": "Airbnb", "logo": "🏠", "description": "Travel and hospitality marketplace",
         "careers_url": "https://airbnb.com/careers/"},
        {"name": "Uber", "logo": "🚗", "description": "Ride-sharing and delivery",
         "careers_url": "https://uber.com/careers/"}
    ]
}

JOB_PORTALS = {
    "LinkedIn": {
        "url": "https://www.linkedin.com/jobs/",
        "description": "Professional networking and job search",
        "icon": "🔗"
    },
    "Indeed": {
        "url": "https://www.indeed.com/",
        "description": "World's largest job search platform",
        "icon": "💼"
    },
    "Glassdoor": {
        "url": "https://www.glassdoor.com/",
        "description": "Company reviews and job listings",
        "icon": "🏢"
    },
    "Naukri": {
        "url": "https://www.naukri.com/",
        "description": "India's leading job portal",
        "icon": "🇮🇳"
    },
    "AngelList": {
        "url": "https://angel.co/jobs",
        "description": "Startup and tech jobs",
        "icon": "🚀"
    },
    "Remote OK": {
        "url": "https://remoteok.com/",
        "description": "Remote work opportunities",
        "icon": "🏠"
    }
}

INDUSTRY_INSIGHTS = [
    {
        "sector": "Technology",
        "growth": "15%",
        "trends": ["AI/ML adoption increasing", "Cloud migration continues", "Cybersecurity demand rises"],
        "top_skills": ["Python", "Cloud Computing", "AI/ML", "DevOps", "Cybersecurity"]
    },
    {
        "sector": "Data Science",
        "growth": "22%",
        "trends": ["Big data analytics expansion", "MLOps emergence", "Data privacy focus"],
        "top_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Deep Learning"]
    },
    {
        "sector": "DevOps",
        "growth": "18%",
        "trends": ["Kubernetes adoption", "GitOps practices", "Platform engineering"],
        "top_skills": ["Docker", "Kubernetes", "CI/CD", "Terraform", "Cloud Platforms"]
    },
    {
        "sector": "Cybersecurity",
        "growth": "25%",
        "trends": ["Zero Trust architecture", "Cloud security", "AI-powered threats"],
        "top_skills": ["Network Security", "Cloud Security", "Ethical Hacking", "Compliance"]
    }
]

def get_companies_by_sector(sector=None):
    if sector and sector in FEATURED_COMPANIES:
        return FEATURED_COMPANIES[sector]
    all_companies = []
    for sector_companies in FEATURED_COMPANIES.values():
        all_companies.extend(sector_companies)
    return all_companies

def get_all_sectors():
    return list(FEATURED_COMPANIES.keys())
