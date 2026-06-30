"""
main.py — ATS Resume Checker FastAPI backend
"""

import os
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.gemini import extract_keywords, analyse_resume
from src.reader import extract_resume_text

app = FastAPI(title="ATS Resume Checker", version="3.0.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyse")
async def analyse(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(""),
    job_description: str = Form(""),
):
    # ── 1. Get resume text ──────────────────────────────────────────
    if resume_file and resume_file.filename:
        raw = await resume_file.read()
        try:
            resume_text = extract_resume_text(resume_file.filename, raw)
        except ValueError as e:
            raise HTTPException(400, str(e))

    if not resume_text.strip():
        raise HTTPException(400, "Resume required — upload a PDF/DOCX or paste text.")

    # ── 2. Extract keywords from JD (only if provided) ──────────────
    keywords = []
    keyword_data = {}
    if job_description.strip():
        keyword_data = extract_keywords(job_description)
        keywords = keyword_data.get("keywords", [])

    # ── 3. Analyse ──────────────────────────────────────────────────
    try:
        result = analyse_resume(resume_text, job_description, keywords)
    except RuntimeError as e:
        msg = str(e)
        raise HTTPException(429 if "quota" in msg.lower() else 502, msg)

    # ── 4. Return report ────────────────────────────────────────────
    return JSONResponse({
        "target_role":             result.get("target_role", keyword_data.get("target_role", "")),
        "mode":                    result.get("mode", "general"),
        "ats_score":               int(result.get("ats_score", 0)),
        "matched_keywords":        result.get("matched_keywords", []),
        "missing_keywords":        result.get("missing_keywords", []),
        "suggested_keywords":      result.get("suggested_keywords", []),
        "section_feedback":        result.get("section_feedback", {}),
        "bullet_quality":          result.get("bullet_quality", ""),
        "legacy_formatting_flags": result.get("legacy_formatting_flags", []),
        "universal_flags":         result.get("universal_flags", []),
        "suggestions":             result.get("suggestions", []),
    })