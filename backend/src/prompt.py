KEYWORD_PROMPT = """You are an ATS keyword extractor. Return a JSON object only. No prose, no markdown.

Extract from the job description and return exactly this structure:
{{
  "target_role": "string",
  "keywords": ["string"],
  "skills": ["string"],
  "tools": ["string"],
  "soft_skills": ["string"]
}}

Rules:
- Keep keywords concise and exact — prefer wording directly from the job description
- No duplicates across lists
- No explanation text, no markdown fences — raw JSON only

Job Description:
{job_description}"""


ANALYSE_PROMPT = """You are an expert ATS resume analyst. Return a JSON object only. No prose, no markdown.

Your job is to ANALYSE the resume and return a structured report card. Do not rewrite or edit the resume.

---

MODE:
{mode_instruction}

---

ANALYSIS RULES:

ATS SCORE (0-100):
- Start at 100
- Deduct exactly 4 points per missing JD keyword found in resume (max -32) — only if JD is provided
- Deduct 7 if resume has no quantified achievements (numbers, percentages, metrics)
- Deduct 9 if summary/objective is missing or weak (generic, vague)
- Deduct 6 if any ATS formatting red flags are found (tables, columns, graphics, special symbols)
- Deduct 3 if bullet points do not start with strong action verbs
- Deduct 4 if key sections are missing (Skills, Experience or Projects, Education)
- Deduct 2 for each minor issue: inconsistent formatting, weak word choice, missing metrics in 1-2 bullets
- Add back 1-3 points for exceptional strengths (strong quantified impact, perfect keyword alignment, clean structure)
- Calculate the exact final number — do not round to the nearest 5 or 10
- The final score must reflect the precise sum of all deductions and additions above, not an estimate
- Minimum score: 10

SECTION FEEDBACK:
- For each section present in the resume, give one specific, actionable sentence
- If a section is missing, say so clearly
- Do not praise vaguely — be direct and specific

BULLET QUALITY:
- Check if bullets start with strong action verbs (Built, Developed, Reduced, Led, etc.)
- Check if any bullets contain quantified results (numbers, %, time saved, users impacted)
- Return one honest assessment sentence

FORMATTING FLAGS:
- Flag: tables, multi-column layouts, headers/footers, graphics, special unicode symbols, missing contact info, missing LinkedIn/GitHub
- Return as a list of short flag strings — empty list if none found

SUGGESTIONS:
- 3 to 5 specific, actionable suggestions
- Each suggestion must reference something real from the resume
- No generic advice like "add more keywords" — be precise

---

Return exactly this JSON:
{{
  "target_role": "string",
  "ats_score": 0,
  "matched_keywords": ["string"],
  "missing_keywords": ["string"],
  "suggested_keywords": ["string"],
  "section_feedback": {{
    "summary": "string",
    "skills": "string",
    "experience": "string",
    "projects": "string",
    "education": "string"
  }},
  "bullet_quality": "string",
  "formatting_flags": ["string"],
  "suggestions": ["string"]
}}

---

{jd_block}

Resume:
{resume_text}"""


# ─────────────────────────────────────────────
# Mode instruction builders
# ─────────────────────────────────────────────

def build_analyse_prompt(resume_text: str, job_description: str = "", keywords: list = []) -> str:
    if job_description.strip():
        mode_instruction = (
            "JD MODE: A job description is provided. "
            "Compare the resume against the JD. "
            "Extract matched and missing keywords. "
            "Score and analyse relative to this specific role."
        )
        jd_block = (
            f"Job Description:\n{job_description.strip()}\n\n"
            f"Keywords to check against resume:\n{', '.join(keywords) if keywords else '(none)'}"
        )
    else:
        mode_instruction = (
            "GENERAL MODE: No job description provided. "
            "Infer the target role from the resume content. "
            "Analyse the resume for general ATS quality, completeness, and impact. "
            "matched_keywords and missing_keywords should be empty lists. "
            "suggested_keywords should list skills/tools relevant to the inferred role that are missing."
        )
        jd_block = "(No job description provided — general ATS quality analysis only)"

    return ANALYSE_PROMPT.format(
        mode_instruction=mode_instruction,
        jd_block=jd_block,
        resume_text=resume_text.strip(),
    )
