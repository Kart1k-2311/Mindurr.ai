# Mindurr.ai
Resume show marks, not mastery. We profile true potential to bridge the fap between student talent and hiring industries.

---

## Problem Statement
The existing process of assessing students' performance depends solely on the CGPA, marks, and certificates of the concerned individuals, which might fail to provide a clear picture about their true abilities, interests, and skills. Factors like socio-economic status of individuals, peer pressure, parental pressure, addiction to social media, insufficient basic knowledge, and varied learning skills might impact the performance of the students in their academics. Consequently, it is possible that many capable students do not get suitable job opportunities to showcase their true potential, whereas some industries might find it difficult to hire suitable candidates for certain positions. The purpose of this project is to design an intelligent system that assesses the skills and potential abilities of the students and makes a skill profile accordingly. Finally, the system recommends suitable candidates according to the needs of the industries.

---

## Live Demo & Preview



---

## Target Audience
### Core Learning Objectives
1. **Algorithmic Thinking:** Master foundational programming structures through bite-sized interactive challenges.
2. **Project Application:** Complete real-world capstone projects with immediate automated code validation.
3. **Collaborative Problem Solving:** Engage in moderated peer discussions and collaborative code-review forums.

---

## Key Features
### 👨‍🎓 For Students & Learners
- **Interactive Code Sandboxes:** In-browser execution engine for Python, JavaScript, and SQL.
- **Micro-Learning Units:** Bite-sized lessons combining video, interactive diagrams, and MDX-rendered theory.
- **Automated Grading & Quizzes:** Instant validation for multiple-choice questions, fill-in-the-blanks, and code challenges.
- **Verifiable Certificates:** Cryptographically verifiable PDF completion certificates upon curriculum mastery.
- **Personal Learning Dashboard:** Visual progression tracking, streak counters, and skill mastery trees.

---
## Tech Stack
The platform is engineered using a modular, lightweight core built on foundational web technologies, paired with modern micro-frontend components, serverless backend infrastructure, and AI-driven skill-profiling engines.

| Layer | Technology | Purpose & Implementation |
| :--- | :--- | :--- |
| **Frontend Core** | **HTML5, Modern CSS3, Vanilla JS (ES6+)** | High-performance, lightweight UI foundation ensuring fast load times, accessible page layouts, and cross-device responsiveness. |
| **Component Layer** | **React & React DOM** | Used for rich, interactive frontend modules (e.g., dynamic skill radar charts, interactive assessment sandboxes, and candidate matching filters). |
| **AI & Assessment Engine** | **Gemini 3.5 API** | Powers natural language skill extraction, semantic evaluation of projects, qualitative interview analysis, and automated candidate-to-role matching. |
| **Backend & Database** | **Supabase** | Managed PostgreSQL database, built-in row-level security (RLS), real-time subscriptions, and secure JWT-based authentication. |
| **Edge & Cloud Services** | **Cloudflare** | DNS routing, CDN caching, DDoS mitigation, and Cloudflare Workers for edge proxying and securing backend API keys. |
| **Storage & Media** | **Supabase Storage** | Secure object storage for student resumes, project media, and verification assets with signed URL access. |



---
## Getting started

### 1. Prerequisites
- Python 3.13+
- Supabase project (URL, anon key, service role key)
- Google Gemini API key

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the Supabase credentials and Gemini API key.

Run the SQL migrations in the **Supabase Dashboard → SQL Editor** (in order):
- `sql/001_profiles.sql`
- `sql/002_skill_profiles.sql`
- `sql/003_recruiter_profiles.sql`
- `sql/004_job_descriptions.sql`
- `sql/005_candidate_matches.sql`
- `sql/006_add_ai_insights.sql`

Start the API server:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend
The frontend is a static site (HTML/JS + Supabase JS SDK via CDN). Serve it on a port allowed by the backend CORS config (e.g. 8080):
```bash
cd frontend
python -m http.server 8080
```
Open `http://localhost:8080`.

Landing → `user_selection.html` → `login_register.html` (role-based) → `assessment.html` → `profile.html` (student) or
`recruiter_dashboard.html` → `candidate_profile.html` (recruiter).
## Course Content Architecture & Curriculum Management

---

## Contributing Guidelines
1. Clone the repo
2. Initialise the Git
3. Pull the origin or create a branch
4. Make changes on your local machine
5. Add a commit message and commit the changes
6. Push it to origin or the branch

---
## License & Acknowledgments
This project is lisenced under the InfoSnatcher.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
