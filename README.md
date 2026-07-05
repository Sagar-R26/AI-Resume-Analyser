# AI Resume Analyzer

An intelligent web application that parses resume information using Natural Language Processing (NLP), analyzes keywords, clusters them into job sectors, and provides personalized recommendations, predictions, and analytics to job applicants.

---

## Features

### User Features
- Location & device metadata capture
- Resume parsing (name, email, phone, skills, degree, pages)
- Experience level prediction (Fresher / Intermediate / Experienced)
- Job field prediction (Data Science, Web Dev, Android, iOS, UI/UX)
- Personalized skill recommendations
- Course & certificate recommendations
- Resume scoring with tips for improvement
- Resume writing & interview preparation videos

### Admin Features
- View all applicant data in tabular format
- Export user data as CSV
- View uploaded PDF resumes
- User feedback & ratings overview
- Analytics dashboard with pie charts for:
  - User ratings
  - Predicted job fields
  - Experience levels
  - Resume scores
  - User locations (City, State, Country)

### Feedback Features
- Submit feedback with rating (1-5)
- View overall rating distribution
- Browse past user comments

---

## System Architecture

```
User Browser (Streamlit Frontend)
         |
         v
   Streamlit Server (App.py)
         |
    +----+----+
    |         |
 Python     MySQL
  NLP       Database
 (spaCy,   (cv)
  NLTK)
    |
pyresparser (Resume Parsing Engine)
    |
PDF Resume (Input)
```

**Flow:**
1. User uploads PDF resume through Streamlit UI
2. `pyresparser` extracts text and entities using spaCy NLP models
3. Extracted data is analyzed against keyword mappings to predict job field
4. Skill and course recommendations are generated
5. Resume score is computed based on content completeness
6. All data is stored in MySQL database for analytics
7. Admin dashboard visualizes aggregated data

---

## Software Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, HTML, CSS |
| **Backend** | Python 3.9+ |
| **Database** | MySQL |
| **NLP Engine** | spaCy, NLTK, pyresparser |
| **PDF Processing** | pdfminer3, pdfminer.six |
| **Visualization** | Plotly |
| **Geolocation** | geocoder, geopy |

---

## Requirements

- Python 3.9 or higher
- MySQL Server
- Visual Studio Build Tools for C++ (required by spaCy)
- Internet connection (for geolocation & first-time NLTK/spaCy downloads)

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sagar-R26/AI-Resume-Analyser.git
cd "AI Resume Analyser"
```

### 2. Configure MySQL

   - Create a database named `cv`
   - Update credentials in `App.py` (search for `pymysql.connect`):
     ```python
     connection = pymysql.connect(host='localhost', user='root', password='your_password', db='cv')
     ```


### 3. Set up a virtual environment (recommended)

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux / macOS
```

### 4. Install dependencies

```bash
pip install setuptools --upgrade
pip install --only-binary :all: -r requirements.txt
python -m spacy download en_core_web_sm
```

### 5. Replace pyresparser

   Copy `pyresparser/resume_parser.py` to `venvapp\Lib\site-packages\pyresparser\` (overwrite the existing file)

### 6. Run the application

   ```bash
   streamlit run App.py
   ```

### 7. Access the app

   - Open the URL shown in terminal (default: `http://localhost:8501`)
   - Admin login: username `admin`, password `admin@resume-analyzer`

---

## Author

**Sagar R**
- GitHub: https://github.com/Sagar-R26
- Project: AI Resume Analyser
