"""
ATS Resume Analyzer — Prompts v2

Key changes from v1:
1. Keyword matching is now DETERMINISTIC (done in Python, not the LLM) — the LLM
   was being asked to count overlaps and do arithmetic, which is unreliable and
   unreproducible. The LLM now only judges things that actually require judgment.
2. Score is assembled in Python from a fixed base + LLM-provided qualitative
   flags, not asked of the LLM as a single "calculate the exact number" output.
3. "mode" is returned explicitly so general-mode and JD-mode scores are never
   silently compared on the same scale.
4. Formatting flags are split into "legacy_ats_risk" vs "universal_risk" since
   modern ATS (Workday, Greenhouse) parse single-column tables fine, but older
   systems (Taleo-era) don't — the tool should say which kind of risk it is
   instead of asserting one universal truth.
5. One few-shot example added to the analyse prompt to stabilize output format
   and feedback specificity.
"""

# ─────────────────────────────────────────────
# 1. Keyword extraction (unchanged structure, soft_skills now actually used)
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# 2. Deterministic keyword matching — DO THIS IN PYTHON, NOT THE LLM
# ─────────────────────────────────────────────

def match_keywords(resume_text: str, keywords: list[str]) -> dict:
    """
    Reproducible keyword overlap check. Case-insensitive substring match,
    with light normalization (e.g. "Node.js" vs "NodeJS").
    Replace with fuzzy matching (e.g. rapidfuzz) if you want tolerance for
    typos or word-order variation.
    """
    import re

    def normalize(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower())

    resume_norm = normalize(resume_text)
    matched, missing = [], []
    for kw in keywords:
        if normalize(kw) in resume_norm:
            matched.append(kw)
        else:
            missing.append(kw)
    return {"matched_keywords": matched, "missing_keywords": missing}


def compute_ats_score(
    matched_keywords: list[str],
    missing_keywords: list[str],
    has_quantified_achievements: bool,
    summary_quality: str,        # "strong" | "weak" | "missing"
    bullets_use_action_verbs: bool,
    missing_sections: list[str],
    legacy_formatting_flags: list[str],
    minor_issues: list[str],
    mode: str,                   # "jd" | "general"
) -> int:
    """
    Deterministic score assembly. The LLM supplies the qualitative inputs
    (summary_quality, bullets_use_action_verbs, etc.) via the analyse prompt;
    this function does the actual arithmetic so it's reproducible.

    Score starts at 95, not 100 — a perfect 100 should be reserved for
    near-flawless resumes with full keyword alignment, since real-world
    strong resumes (even very good ones) typically land in the 75-90 range,
    not the high 90s.
    """
    score = 95

    if mode == "jd":
        total_kw = len(matched_keywords) + len(missing_keywords)
        if total_kw > 0:
            score -= min(32, 4 * len(missing_keywords))

    if not has_quantified_achievements:
        score -= 14
    if summary_quality == "missing":
        score -= 9
    elif summary_quality == "weak":
        score -= 5
    if legacy_formatting_flags:
        score -= 6
    if not bullets_use_action_verbs:
        score -= 3
    if missing_sections:
        score -= 4
    score -= 2 * len(minor_issues)

    return max(10, min(100, score))


# ─────────────────────────────────────────────
# 3. Analysis prompt — LLM only judges what requires judgment
# ─────────────────────────────────────────────

ANALYSE_PROMPT = """You are an expert ATS resume analyst. Return a JSON object only. No prose, no markdown.

Your job is to ANALYSE the resume and return structured qualitative judgments.
Do NOT calculate a numeric score yourself — the score is computed separately
from the fields you return. Do not rewrite or edit the resume.

---

MODE:
{mode_instruction}

---

WHAT TO JUDGE:

- has_quantified_achievements: true only if at least one bullet contains a real
  number, percentage, or measurable outcome (not "many users" or "various
  improvements" — those are not quantified).
- summary_quality: "strong" (specific to the role, names real skills/domain),
  "weak" (generic / vague / could apply to any candidate), or "missing".
- bullets_use_action_verbs: true only if the large majority of bullets open
  with a strong verb (Built, Reduced, Led, Architected, etc.) — not "Responsible
  for" or "Worked on".
- missing_sections: list any of [Skills, Experience, Projects, Education] that
  are absent. Note: for students/new grads, Projects can substitute for
  Experience — only flag Experience as missing if there is also no Projects
  section.
- legacy_formatting_flags: formatting that breaks OLDER ATS parsers specifically
  (e.g. Taleo-era) — multi-column layout, text in headers/footers, graphics
  replacing text, special unicode bullets/symbols. Do NOT flag simple tables or
  single-column layouts; modern ATS (Workday, Greenhouse) handle those fine.
- universal_flags: issues that hurt regardless of ATS version — missing contact
  info, missing LinkedIn/GitHub if relevant to the role, broken section headers.
- minor_issues: list specific small problems (inconsistent date formatting,
  weak word choice in 1-2 spots, missing metrics in otherwise-good bullets).
  Each entry must reference something real and specific — not generic advice.

SECTION FEEDBACK:
- One specific, actionable sentence per present section. Be direct, not vague
  praise. If a section is missing, say so plainly instead of guessing content.

SUGGESTIONS:
- 3 to 5 suggestions, each referencing a specific bullet, section, or phrase
  actually in the resume. No generic advice like "add more keywords."

---

EXAMPLE (for format reference only — do not reuse this content):

Input resume excerpt: "Built internal dashboard used by support team."
Bad suggestion: "Add more detail."
Good suggestion: "The dashboard bullet has no scale — note how many support
agents used it or what manual process it replaced (e.g. 'used daily by a
12-person support team, replacing a manual spreadsheet workflow')."

---

Return exactly this JSON:
{{
  "target_role": "string",
  "mode": "{mode_value}",
  "has_quantified_achievements": true,
  "summary_quality": "strong | weak | missing",
  "bullets_use_action_verbs": true,
  "missing_sections": ["string"],
  "legacy_formatting_flags": ["string"],
  "universal_flags": ["string"],
  "minor_issues": ["string"],
  "section_feedback": {{
    "summary": "string",
    "skills": "string",
    "experience": "string",
    "projects": "string",
    "education": "string"
  }},
  "bullet_quality": "string",
  "suggested_keywords": ["string"],
  "suggestions": ["string"]
}}

---

{jd_block}

Resume:
{resume_text}"""


# ─────────────────────────────────────────────
# 4. Mode instruction builders
# ─────────────────────────────────────────────

def build_analyse_prompt(resume_text: str, job_description: str = "", keywords: list = None) -> tuple[str, str]:
    """
    Returns (prompt, mode) — mode is needed later for compute_ats_score().
    """
    keywords = keywords or []
    if job_description.strip():
        mode = "jd"
        mode_instruction = (
            "JD MODE: A job description is provided. Judge the resume's fit "
            "and quality relative to this specific role. suggested_keywords "
            "should list role-relevant terms not already in the resume, beyond "
            "the keyword list already being matched separately."
        )
        jd_block = f"Job Description:\n{job_description.strip()}"
    else:
        mode = "general"
        mode_instruction = (
            "GENERAL MODE: No job description provided. Infer the target role "
            "from the resume content. Analyse for general ATS quality, "
            "completeness, and impact. suggested_keywords should list skills/"
            "tools relevant to the inferred role that are plausibly missing."
        )
        jd_block = "(No job description provided — general ATS quality analysis only)"

    prompt = ANALYSE_PROMPT.format(
        mode_instruction=mode_instruction,
        mode_value=mode,
        jd_block=jd_block,
        resume_text=resume_text.strip(),
    )
    return prompt, mode