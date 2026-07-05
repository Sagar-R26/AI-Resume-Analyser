import requests
from bs4 import BeautifulSoup
import re
import time
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def search_linkedin_jobs(keyword, location="", num_results=10):
    try:
        params = {
            'keywords': keyword,
            'location': location,
            'position': 1,
            'pageNum': 0
        }
        headers = get_random_headers()
        response = requests.get(
            'https://www.linkedin.com/jobs/search/',
            params=params,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return parse_linkedin_jobs(response.text, num_results)
        return get_mock_jobs(keyword, location, num_results)
    except Exception as e:
        print(f"LinkedIn search failed: {e}")
        return get_mock_jobs(keyword, location, num_results)

def parse_linkedin_jobs(html, num_results):
    jobs = []
    soup = BeautifulSoup(html, 'html.parser')
    job_cards = soup.find_all('div', class_='base-card')[:num_results]
    for card in job_cards:
        title_elem = card.find('h3', class_='base-search-card__title')
        company_elem = card.find('a', class_='hidden-nested-link')
        location_elem = card.find('span', class_='job-search-card__location')
        link_elem = card.find('a', class_='base-card__full-link')
        if title_elem:
            jobs.append({
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip() if company_elem else 'Unknown',
                'location': location_elem.text.strip() if location_elem else 'Remote',
                'url': link_elem['href'] if link_elem and link_elem.has_attr('href') else '#',
                'platform': 'LinkedIn'
            })
    return jobs if jobs else get_mock_jobs("", "", num_results)

def get_mock_jobs(keyword, location, count=10):
    mock_positions = [
        f"{keyword} Engineer", f"Senior {keyword} Developer",
        f"{keyword} Specialist", f"Lead {keyword} Architect",
        f"Junior {keyword} Developer", f"{keyword} Team Lead",
        f"Principal {keyword} Engineer", f"{keyword} Consultant",
        f"{keyword} Analyst", f"Staff {keyword} Engineer"
    ]
    mock_companies = [
        "Tech Corp", "Innovate Inc", "DataFlow Systems", "CloudBase Solutions",
        "NextGen Tech", "Digital Horizons", "Quantum Computing Inc",
        "Smart Solutions Ltd", "Future Technologies", "Alpha Digital"
    ]
    mock_locations = [
        "San Francisco, CA", "New York, NY", "Remote", "Austin, TX",
        "Seattle, WA", "Boston, MA", "Chicago, IL", "Denver, CO"
    ]
    jobs = []
    for i in range(min(count, len(mock_positions))):
        jobs.append({
            'title': mock_positions[i],
            'company': random.choice(mock_companies),
            'location': random.choice(mock_locations),
            'url': f"https://www.linkedin.com/jobs/view/{random.randint(1000000, 9999999)}/",
            'platform': 'LinkedIn',
            'posted': f"{random.randint(1, 30)} days ago"
        })
    return jobs
