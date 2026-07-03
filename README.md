# AI Resume Analyzer

An intelligent web application that uses Natural Language Processing to parse, analyze, and score resumes. Users upload a PDF resume and receive instant feedback including skill extraction, job role prediction, course recommendations, and personalized improvement suggestions. The admin dashboard provides analytics with pie charts, a structured resume table, and CSV export.

## Features

### User-Facing
- **PDF Upload** – Upload any resume in PDF format
- **Contact Extraction** – Automatically extracts name, email, phone, and location
- **Skill Detection** – Identifies skills from a database of 60+ technical and soft skills
- **Resume Scoring** – Scores out of 100 with grade (Excellent / Good / Average / Needs Improvement)
- **Job Role Prediction** – Matches extracted skills against 11 role profiles using similarity scoring
- **Skill Gap Analysis** – Suggests trending skills missing from the resume
- **Course Recommendations** – Suggests relevant online courses (Coursera, Udemy) based on skill gaps
- **Video Resources** – Curated YouTube playlist on resume writing and interview preparation
- **Improvement Suggestions** – Actionable tips to strengthen the resume

### Admin Dashboard (`/admin/login`)
- **Stats Overview** – Total resumes uploaded, average score, top predicted role, unique roles
- **Pie Charts** – Job role distribution and user locations
- **Score Distribution** – Bar chart showing score ranges (0–20, 21–40, etc.)
- **Resume Table** – Paginated table of all uploaded resumes with search and detail view
- **CSV Export** – Download all resume data as a CSV file (UTF-8 BOM for Excel compatibility)
- **Resume Detail** – Full detail view including extracted text toggle

## Project Preview

```
User Flow:
  Home → Upload PDF → Analysis → Score + Skills + Suggestions + Courses + Videos

Admin Flow:
  Login → Dashboard (charts) → Resumes Table → Detail View / CSV Export
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                       │
└──────────┬────────────────────────────────┬────────────────┘
           │ HTTP (Flask routes)            │
           ▼                                ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│   User Views         │    │   Admin Views                │
│  ──────────          │    │  ────────────                │
│  /                   │    │  /admin/login                │
│  /upload             │    │  /admin/dashboard            │
│  /result             │    │  /admin/resumes              │
│                      │    │  /admin/resumes/download     │
└──────────┬───────────┘    └──────────┬───────────────────┘
           │                            │
           └──────────┬─────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │   Flask App     │
            │   (app.py)      │
            └────────┬────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
   ┌──────────┐ ┌────────┐ ┌──────┐
   │ Services │ │ Models │ │ Utils │
   │ NLP      │ │ (DB)   │ │      │
   │ Scorer   │ │        │ │      │
   │ Predictor│ │        │ │      │
   │Recommender│ │        │ │      │
   └────┬─────┘ └───┬────┘ └──────┘
        │           │
        ▼           ▼
   ┌──────────┐ ┌──────────┐
   │ PDF file │ │  MySQL   │
   │ (uploads) │ │ Database │
   └──────────┘ └──────────┘
```

## Software Stack

| Layer          | Technology                            |
|----------------|---------------------------------------|
| **Backend**    | Python 3, Flask 3.0                   |
| **Frontend**   | HTML5, Bootstrap 5, Chart.js, CSS3    |
| **Database**   | MySQL 8+                              |
| **PDF Parsing**| pdfplumber                            |
| **NLP**        | Pure Python (regex + keyword matching)|
| **Charts**     | Chart.js (pie, bar charts)            |
| **CSV Export** | Python csv module (UTF-8 BOM)         |

## Requirements

- Python 3.10+
- MySQL 8.0+ running locally or remotely
- pip (Python package manager)

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd "AI Resume"
```

### 2. Configure MySQL

Make sure MySQL is running and update credentials in `config.py`:

```python
MYSQL_HOST = 'localhost'     # your MySQL host
MYSQL_USER = 'root'          # your MySQL user
MYSQL_PASSWORD = 'password'  # your MySQL password
MYSQL_DB = 'resume_analyzer' # database name (auto-created on first run)
```

Alternatively, set environment variables:

```bash
set MYSQL_PASSWORD=yourpassword
```

### 3. Set up a virtual environment (recommended)

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux / macOS
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

The app will:
- Auto-create the `resume_analyzer` database and tables on first run
- Start on `http://localhost:5000`

### 6. Access the app

| URL                          | Description          |
|------------------------------|----------------------|
| `http://localhost:5000/`     | Home page            |
| `http://localhost:5000/upload` | Resume upload      |
| `http://localhost:5000/admin/login` | Admin login |

**Default admin credentials:**  
Username: `admin`  
Password: `admin123`

## Project Structure

```
AI Resume/
├── app.py                      # Flask application entry point
├── config.py                   # Configuration (MySQL, upload settings)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── database/
│   └── schema.sql              # SQL schema for reference
├── services/
│   ├── nlp_parser.py           # PDF parsing, skill extraction, NLP utilities
│   ├── scorer.py               # Resume scoring engine
│   ├── predictor.py            # Job role prediction
│   └── recommender.py          # Course & video recommendations
├── templates/
│   ├── base.html               # Base layout (Bootstrap 5 + nav)
│   ├── index.html              # Landing page
│   ├── upload.html             # Upload form
│   ├── result.html             # Analysis results
│   └── admin/
│       ├── login.html          # Admin authentication
│       ├── dashboard.html      # Analytics dashboard (Chart.js)
│       ├── resumes.html        # Paginated resume table
│       └── resume_detail.html  # Single resume detail view
└── static/
    ├── css/
    │   └── style.css           # Custom styles
    ├── js/
    │   └── script.js           # Client-side validation
    └── uploads/                # Uploaded PDFs
```

## API Endpoints

| Method | Endpoint                   | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/`                        | Home page                      |
| GET    | `/upload`                  | Upload form                    |
| POST   | `/upload`                  | Process PDF upload             |
| GET    | `/admin/login`             | Admin login form               |
| POST   | `/admin/login`             | Admin login                    |
| GET    | `/admin/logout`            | Admin logout                   |
| GET    | `/admin/dashboard`         | Analytics dashboard            |
| GET    | `/admin/resumes`           | Paginated resume table         |
| GET    | `/admin/resumes/<id>`      | Resume detail view             |
| GET    | `/admin/resumes/download`  | Download all as CSV            |
| GET    | `/api/resume/<id>`         | Resume data as JSON            |

## Author

**Sagar R**
- GitHub: [@SagarR](https://github.com/SagarR)
- Project: AI Resume Analyzer
