# llama_service.py
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
You are a resume analysis assistant. Given the resume text, produce a valid JSON object (nothing else) with the exact keys:
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
  "skills": { "technical": [], "soft": [] },
  "summary": "",
  "ats_score": 0,
  "role_match": 0,
  "word_count": 0
}
Rules:
- Output ONLY JSON.
- technical skills should be short strings (e.g., "Python", "React", "Docker").
- soft skills should be short strings (e.g., "communication", "teamwork").
- ats_score: integer 0-100 (estimate).
- role_match: integer 0-100 (estimated match to a role inferred from skills).
Now analyze the resume text below and return the JSON.
Resume:
-----
{resume_text}
"""

def call_openrouter(resume_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.replace("{resume_text}", resume_text[:40000])  # limit size
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1500
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # get content
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError("Unexpected response from OpenRouter: %s" % e)
    # parse JSON from content
    parsed = json.loads(content)
    return parsed
