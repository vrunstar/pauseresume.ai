# ```pauseresumeplay.ai```

An ATS resume checker built with FastAPI + React. Upload your resume, optionally paste a job description, and get an instant report card — ATS score, keyword gaps, section feedback, and actionable suggestions.

🔗 **Live:** [pauseresume.vercel.app](https://pauseresume.vercel.app) · **API:** [ats-check-hcdg.onrender.com](https://ats-check-hcdg.onrender.com/docs)

## What it does

**With a job description:**
- Extracts keywords from the JD
- Shows matched, missing, and suggested keywords
- Scores your resume against the role

**Without a job description:**
- Infers your target role from the resume
- Analyses general ATS quality
- Suggests skills relevant to your inferred role

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Vite, React Router |
| Backend | FastAPI, Python 3.11+ |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Resume parsing | pdfplumber (PDF), python-docx (DOCX) |
| Deployment | Vercel (frontend) + Render (backend) |

## Project structure

```
ats_resume_optimizer/
├── backend/
│   ├── main.py               # FastAPI app — /analyse endpoint
│   ├── requirements.txt
│   └── src/
│       ├── config.py         # env config
│       ├── gemini.py         # Groq client, extract_keywords, analyse_resume
│       ├── parser.py         # JSON extraction + resume section splitting
│       ├── formatter.py      # text normalisation
│       ├── prompt.py         # KEYWORD_PROMPT + ANALYSE_PROMPT
│       └── reader.py         # PDF/DOCX text extraction
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── api.js            # axios calls to FastAPI
│       ├── main.jsx
│       ├── components/
│       │   ├── KeywordBadge.jsx
│       │   └── ScoreRing.jsx
│       └── pages/
│           ├── Home.jsx
│           └── Results.jsx
└── render.yaml               # Render deployment config
```

## Local setup

### 1. Clone

```bash
git clone https://github.com/vrunstar/ats_resume_optimizer.git
cd ats_resume_optimizer
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
```

Start the server:
```bash
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Deployment

### Backend → Render

1. Push repo to GitHub
2. Render dashboard → New → Web Service → connect repo
3. Render auto-detects `render.yaml`
4. Set environment variables in the Render dashboard:
   - `GROQ_API_KEY` — your Groq API key
   - `ALLOWED_ORIGINS` — your Vercel frontend URL
5. Deploy

### Frontend → Vercel

1. Vercel dashboard → New Project → connect repo
2. Set root directory to `frontend`
3. Add environment variable:
   - `VITE_API_URL` — your Render backend URL (e.g. `https://pauseresumeplay-api.onrender.com`)
4. Deploy

## API

### `POST /analyse`

| Field | Type | Required |
|---|---|---|
| `resume_file` | File (PDF/DOCX) | No* |
| `resume_text` | string | No* |
| `job_description` | string | No |

*One of `resume_file` or `resume_text` is required.

**Response:**
```json
{
  "target_role": "string",
  "ats_score": 0,
  "matched_keywords": [],
  "missing_keywords": [],
  "suggested_keywords": [],
  "section_feedback": {
    "summary": "string",
    "skills": "string",
    "experience": "string",
    "projects": "string",
    "education": "string"
  },
  "bullet_quality": "string",
  "formatting_flags": [],
  "suggestions": []
}
```

## Environment variables

| Variable | Where | Description |
|---|---|---|
| `GROQ_API_KEY` | backend `.env` | Groq API key |
| `ALLOWED_ORIGINS` | backend `.env` | Comma-separated allowed CORS origins |
| `VITE_API_URL` | frontend `.env` | Backend URL (empty = use Vite proxy locally) |

## Roadmap

- **Optimised resume builder** — generate a rewritten, ATS-friendly version of the resume with the suggested improvements applied, with a PDF download
- **Multi-JD comparison** — check one resume against multiple job descriptions at once
- **Resume history** — save and compare past analyses
- **Cover letter generator** — generate a tailored cover letter based on the resume and JD

## License

MIT
