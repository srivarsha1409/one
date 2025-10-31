from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pdfplumber
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize OpenAI client (OpenRouter)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ✅ Normalize languages
def normalize_languages(languages):
    standard_langs = {
        "english": "English", "tamil": "Tamil", "hindi": "Hindi",
        "telugu": "Telugu", "malayalam": "Malayalam", "kannada": "Kannada",
        "french": "French", "german": "German", "spanish": "Spanish",
        "bengali": "Bengali", "marathi": "Marathi", "punjabi": "Punjabi",
        "gujarati": "Gujarati", "urdu": "Urdu", "oriya": "Oriya",
        "nepali": "Nepali"
    }
    normalized = []
    for lang in languages:
        key = lang.strip().lower()
        if key in standard_langs and standard_langs[key] not in normalized:
            normalized.append(standard_langs[key])
    return normalized


@app.get("/")
def home():
    return {"message": "AI Resume Insight backend running ✅"}


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # ✅ Read PDF text
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        if not text.strip():
            return {"error": "No readable text found in PDF."}

        # ✅ Resume parsing prompt
        prompt = f"""
Extract structured resume info and return VALID JSON ONLY:

{{
  "name":"",
  "email":"",
  "phone":"",
  "linkedin":"",
  "github":"",
  "leetcode":"",
  "codechef":"",
  "hackerrank":"",
  "languages": [],
  "education": {{
      "degree":"",
      "university":"",
      "year":"",
      "gpa":"",
      "school_name":"",
      "sslc_percentage":"",
      "hsc_percentage":""
  }},
  "internships":[{{"company":"","position":"","duration":"","technologies":""}}],
  "skills":{{"technical":[],"soft":[]}},
  "certificates":[],
  "role_match":"",
  "summary":""
}}

Resume text:
{text}
"""

        # ✅ Try paid model first
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            ai_output = response.choices[0].message.content

        except Exception:
            print("⚠️ No credits — switching to free Gemma model")
            try:
                # ✅ First free fallback
                response = client.chat.completions.create(
                    model="google/gemma-2-9b-it",
                    messages=[
                        {"role": "system", "content": "Return ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                ai_output = response.choices[0].message.content

            except Exception:
                print("⚠️ Gemma failed — switching to free Mistral model")
                # ✅ Backup model
                response = client.chat.completions.create(
                    model="mistralai/mistral-7b-instruct",
                    messages=[
                        {"role": "system", "content": "Return ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )
                ai_output = response.choices[0].message.content

        # ✅ Clean JSON text
        ai_output = ai_output.strip().replace("```json", "").replace("```", "")

        # ✅ Parse JSON safely
        data = json.loads(ai_output)

        # ✅ Defaults
        data.setdefault("languages", [])
        data.setdefault("skills", {"technical": [], "soft": []})
        data.setdefault("education", {"degree": "", "university": "", "year": "", "gpa": "", "school_name": "", "sslc_percentage": "", "hsc_percentage": ""})
        data.setdefault("internships", [])
        data.setdefault("certificates", [])
        data.setdefault("role_match", "")
        data.setdefault("summary", "")

        # ✅ Normalize languages
        langs = data.get("languages", [])
        langs = [l.strip() for l in langs if l.strip()] if isinstance(langs, list) else []
        normalized = normalize_languages(langs)

        if not normalized:
            common_langs = ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "French"]
            normalized = [lang for lang in common_langs if lang.lower() in text.lower()]
        if not normalized:
            normalized = ["English"]

        data["languages"] = normalized

        # ✅ ATS Score
        tech_count = len(data.get("skills", {}).get("technical", []))
        ats_score = min(100, tech_count * 10 + 30)

        return {
            "data": {
                **data,
                "ats_score": ats_score,
                "word_count": len(text.split())
            }
        }

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return {"error": str(e)}

