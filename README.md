# HireLoop

HireLoop is a full-stack AI resume-to-job matching platform. It analyzes a candidate resume against a job description, researches the target company, scores the match, explains evidence for matched skills, and generates resume improvement suggestions through a multi-agent backend workflow.

## Live Demo

- Frontend: https://hireloop-930cv82n0-neha-damani-s-projects.vercel.app/
- Backend: https://hireloop-7j0q.onrender.com/
- Repository: https://github.com/nehadamani0909/HIRELOOP

The backend is hosted on Render's free tier, so the first request after inactivity can take 50 seconds or more while the service wakes up.

## Features

- PDF resume upload and text extraction.
- Job description parsing for required skills, preferred skills, responsibilities, and experience requirements.
- AI resume extraction for skills, projects, experience, education, and skill evidence.
- Semantic JD-to-resume matching with match score, matched skills, missing skills, and reasoning summary.
- Evidence generation for each matched skill.
- Resume improvement suggestions tailored to the job description.
- Company research using Tavily search.
- Results page for reviewing the complete analysis.

## Tech Stack

Frontend:
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Vercel

Backend:
- FastAPI
- Uvicorn
- Groq API
- Tavily API
- LangGraph-style multi-agent workflow
- Pydantic
- pypdf
- Render

## Project Structure

```text
HIRELOOP/
├── backend/
│   ├── agents/
│   │   ├── resume_agent.py
│   │   ├── jd_agent.py
│   │   ├── matching_agent.py
│   │   ├── evidence_agent.py
│   │   ├── resume_suggestion_agent.py
│   │   └── workflow.py
│   ├── main.py
│   ├── schemas.py
│   ├── utils.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── results/page.tsx
│   ├── package.json
│   ├── next.config.ts
│   └── .env.example
└── README.md
```

## Environment Variables

Backend `.env`:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

For production on Vercel:

```env
NEXT_PUBLIC_API_BASE_URL=https://hireloop-7j0q.onrender.com
```

Never commit real `.env` files. This repo only includes `.env.example` files.

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nehadamani0909/HIRELOOP.git
cd HIRELOOP
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your real API keys to `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Start the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test it:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"HireLoop backend running"}
```

### 3. Set Up the Frontend

Open a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
```

Add the local backend URL to `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/analyze` | Basic keyword-based resume analysis |
| `POST` | `/analyze-ai` | Resume extraction only |
| `POST` | `/analyze-full-ai` | Resume and JD extraction |
| `POST` | `/analyze-match-ai` | Resume, JD, and matching analysis |
| `POST` | `/analyze-evidence-ai` | Adds evidence generation |
| `POST` | `/analyze-suggestion-ai` | Adds resume suggestions |
| `POST` | `/analyze-langgraph` | Full multi-agent workflow used by the frontend |

The frontend sends a `multipart/form-data` request to `/analyze-langgraph` with:

```text
resume: PDF file
job_description: string
company_name: string
```

## Deployment

### Backend on Render

Create a Render Web Service connected to this repository.

Settings:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Current backend deployment:

```text
https://hireloop-7j0q.onrender.com
```

### Frontend on Vercel

Import the same GitHub repository into Vercel.

Settings:

```text
Root Directory: frontend
Framework Preset: Next.js
Build Command: npm run build
Install Command: npm install
```

Environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://hireloop-7j0q.onrender.com
```

Current frontend deployment:

```text
https://hireloop-930cv82n0-neha-damani-s-projects.vercel.app/
```

## Notes

- Render free instances spin down after inactivity. A cold request can take 50 seconds or more.
- The backend lazy-loads AI agents so the Render service can start within the free tier memory limit.
- Local semantic embedding dependencies are disabled in production by default to keep memory usage low.
- Real secrets are ignored through `.gitignore`; use `.env.example` files as templates only.

## Author

Built by Neha Damani.
