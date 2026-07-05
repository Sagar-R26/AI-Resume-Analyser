# Smart AI Resume Analyzer

An intelligent web application that analyzes resumes using AI-powered Natural Language Processing, provides ATS compatibility scoring, generates professional resumes with multiple templates, and delivers personalized career recommendations to job applicants.

---

## Features

### User Features
- Resume parsing (name, email, phone, skills, education, experience, projects)
- ATS compatibility scoring with detailed section-wise analysis
- AI-powered deep resume analysis via Google Gemini (strengths, weaknesses, skill gaps)
- Professional resume builder with 4 customizable templates (Modern, Professional, Minimal, Creative)
- Keyword matching against target job roles (16 roles across 6 categories)
- Personalized course & certification recommendations
- Resume writing & interview preparation video resources
- Job search with LinkedIn integration and featured company listings
- Industry insights and career guidance

### Admin Features
- Analytics dashboard with interactive charts (gauge, pie, line, bar)
- View all applicant data in tabular format with export capabilities
- AI analysis statistics (model usage, score distribution, daily trends)
- User feedback overview with ratings and category breakdown
- Admin activity logs
- Reset analytics data

### Feedback Features
- Submit feedback with rating (1-5)
- Categorize feedback by type (Bug, Feature Request, UX, etc.)
- View overall rating distribution and category breakdown
- Export feedback data as CSV

---

## System Architecture

```
User Browser (Streamlit Frontend)
         |
         v
   Streamlit Server (app.py)
         |
    +----+----+
    |         |
   SQLite   Google
  Database  Gemini AI
 (resume_   (gemini-
  data.db)   2.5-flash)
    |
+---+---+---+---+
|       |       |
ATS    Resume  Job Role
Scoring Builder Mapper
       |
   4 Templates
 (DOCX Output)
```

**Flow:**
1. User uploads PDF/DOCX resume through Streamlit UI
2. Text is extracted using pdfplumber & PyPDF2 (with OCR fallback via Tesseract)
3. ATS analyzer scores the resume against target role keywords
4. Google Gemini AI performs deep analysis with contextual recommendations
5. Resume Builder generates professional DOCX resumes in 4 templates
6. All data is persisted in SQLite database for analytics
7. Admin dashboard visualizes aggregated data with Plotly charts
8. Job search module fetches listings and recommends relevant roles

---

## Software Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, HTML, CSS (dark theme) |
| **Backend** | Python 3.9+ |
| **Database** | SQLite (embedded, zero configuration) |
| **AI Engine** | Google Gemini 2.5 Flash API |
| **PDF Processing** | pdfplumber, PyPDF2, pypdf, pdf2image |
| **OCR** | pytesseract (Tesseract OCR) |
| **DOCX Generation** | python-docx |
| **Visualization** | Plotly, Plotly Express |
| **Web Scraping** | BeautifulSoup4, Requests |

---

## Requirements

- Python 3.9 or higher
- Google Gemini API key (free tier available)
- Internet connection (for AI analysis & job search)
- Optional: Tesseract OCR + Poppler (for scanned/image-based PDFs)

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sagar-R26/AI-Resume-Analyser.git
cd "AI Resume Analyser"
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux / macOS
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

   Get your free API key at: https://aistudio.google.com/apikey

### 5. Run the application

```bash
streamlit run app.py
```

### 6. Access the app

   - Open the URL shown in terminal (default: `http://localhost:8501`)
   - Register an admin account via the Dashboard page to access analytics

---

## Optional: OCR Setup for Scanned PDFs

For image-based/scanned PDFs, install:

- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
- **Poppler**: https://github.com/oschwartz10612/poppler-windows/releases/

Then install Python bindings:

```bash
pip install pytesseract pdf2image
```

---

## Project Structure

```
smart-ai-resume-analyzer/
├── app.py                    # Main Streamlit entry point (7 pages)
├── ui_components.py          # Reusable UI helpers
├── style/style.css           # Dark theme stylesheet
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
├── config/
│   ├── database.py           # SQLite schema & CRUD operations
│   ├── job_roles.py          # 16 job roles with skill mappings
│   └── courses.py            # Course & video recommendations
├── utils/
│   ├── resume_analyzer.py    # ATS scoring engine
│   ├── resume_builder.py     # 4 DOCX resume templates
│   └── ai_resume_analyzer.py # Google Gemini integration
├── dashboard/
│   ├── dashboard.py          # Admin panel & analytics
│   └── components.py         # Plotly chart renderers
├── feedback/
│   └── feedback.py           # Feedback CRUD & export
└── jobs/
    ├── job_search.py         # Job search UI
    ├── job_portals.py        # Portal integrations
    ├── suggestions.py        # Role matching engine
    ├── companies.py          # Featured companies data
    └── linkedin_scraper.py   # LinkedIn job fetching
```

---

## Job Roles Supported

| Category | Roles |
|----------|-------|
| Software Development | Frontend, Backend, Full Stack, Mobile, Game Developer |
| Data Science & Analytics | Data Scientist, Data Analyst, ML Engineer |
| Cloud & DevOps | Cloud Architect, DevOps Engineer, SRE |
| Cybersecurity | Security Analyst, Penetration Tester |
| UI/UX Design | UI Designer, UX Designer |
| Project Management | Project Manager, Product Manager |

---

## Author

**Sagar R**
- GitHub: https://github.com/Sagar-R26
- Project: AI Resume Analyser

