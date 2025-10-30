# ai_resume_parser.py
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-70b-instruct")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in .env")

PROMPT_TEMPLATE = """
You are a precise resume parsing assistant. Given resume text return ONLY a JSON with the exact fields:
{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": "",
  "leetcode": "",
  "codechef": "",
  "codeforces": "",
  "hackerrank": "",
  "skills": {
      "technical": [],
      "soft": [],
      "area_of_interest": []
  },
  "summary": "",
  "ats_score": 0,
  "role_match": 0,
  "word_count": 0
}

Rules:
- Output MUST be valid JSON only (no commentary).
- Combine skills found under headings like "Skills", "Technical Skills", "Programming Languages", "Languages", "Frameworks", "Tools & Technologies", etc. into "technical".
- Combine "Soft Skills", "Interpersonal Skills", "Communication", "Strengths" into "soft".
- If a heading "Area of Interest", "Interests" or similar exists, place items under "area_of_interest".
- For ats_score and role_match return integer 0-100 (estimates).
- word_count = number of words in resume_text.
- summary: a short (1-3 sentences) summary extracted or generated.

Resume:
-----
{resume_text}
"""

def call_openrouter(resume_text: str) -> dict:
    prompt_text = PROMPT_TEMPLATE.replace("{resume_text}", resume_text[:40000])
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.0,
        "max_tokens": 1500
    }
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"OpenRouter unexpected response: {e} - {data}")
    # ensure valid JSON (some model outputs can include stray text)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # attempt to find JSON block in content
        import re
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            parsed = json.loads(match.group(0))
        else:
            raise RuntimeError(f"Model output not JSON:\n{content}")
    return parsed
