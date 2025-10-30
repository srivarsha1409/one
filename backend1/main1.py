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

# ✅ Initialize OpenAI client for OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ✅ Normalize languages
def normalize_languages(languages):
    """Normalize language names like tamil/TAMIL/English/ENGLISH."""
    standard_langs = {
        "english": "English", "tamil": "Tamil", "hindi": "Hindi", "telugu": "Telugu",
        "malayalam": "Malayalam", "kannada": "Kannada", "french": "French",
        "german": "German", "spanish": "Spanish", "bengali": "Bengali",
        "marathi": "Marathi", "punjabi": "Punjabi", "gujarati": "Gujarati",
        "urdu": "Urdu", "oriya": "Oriya", "nepali": "Nepali",
    }

    normalized = []
    for lang in languages:
        key = lang.strip().lower()
        if key in standard_langs:
            proper = standard_langs[key]
            if proper not in normalized:
                normalized.append(proper)
    return normalized


@app.get("/")
def home():
    return {"message": "AI Resume Insight (OpenRouter) backend running ✅"}


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """Extract text from uploaded PDF and analyze using OpenRouter AI."""
    try:
        # Step 1: Extract text from PDF
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        if not text.strip():
            return {"error": "No readable text found in PDF."}

        # Step 2: AI Prompt
        prompt = f"""
You are an expert resume analysis assistant.
Return strictly valid JSON only in this format:

{{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": "",
  "leetcode": "",
  "languages": [],
  "education": {{
      "degree": "",
      "university": "",
      "year": "",
      "gpa": ""
  }},
  "codechef":"",
  "hackerrank":"",
  "internships": [
      {{
          "company": "",
          "position": "",
          "duration": "",
          "technologies": ""
      }}
  ],
  "skills": {{
      "technical": [],
      "soft": []
  }},
  "certificates": [],
  "role_match": "",
  "summary": ""
}}

Resume text:
{text}
        """

        # Step 3: Call OpenRouter
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that returns only valid JSON resume analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        ai_output = response.choices[0].message.content
        ai_output = ai_output.strip().replace("```json", "").replace("```", "")

        # Step 4: Parse JSON safely
        try:
            data = json.loads(ai_output)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON from AI:\n", ai_output)
            return {"error": "AI response was invalid. Please try again."}

        # ✅ Step 5: Ensure all expected fields exist
        data.setdefault("role_match", "General")
        data.setdefault("languages", [])
        data.setdefault("skills", {"technical": [], "soft": []})
        data.setdefault("education", {"degree": "", "university": "", "year": "", "gpa": ""})
        data.setdefault("internships", [])
        data.setdefault("certificates", [])
        data.setdefault("summary", "")
        data.setdefault("codechef", "")
        data.setdefault("hackerrank", "")

        # ✅ Step 6: Normalize and fix languages
        langs = data.get("languages", [])
        if isinstance(langs, list):
            # Filter out empty strings and whitespace
            langs = [l.strip() for l in langs if l and l.strip()]
            normalized = normalize_languages(langs)
        else:
            normalized = []

        # Fallback: detect from resume text if still empty
        if not normalized:
            common_langs = ["English", "Tamil", "Hindi", "Kannada", "Telugu", "Malayalam", "French"]
            normalized = [lang for lang in common_langs if lang.lower() in text.lower()]

        # Final fallback if none found
        if not normalized:
            normalized = ["English"]  # Default assumption

        data["languages"] = normalized



        # Step 7: Simple ATS scoring
        tech_skills = data.get("skills", {}).get("technical", [])
        ats_score = min(100, len(tech_skills) * 10 + 20)

        return {
            "data": {
                **data,
                "ats_score": ats_score,
                "word_count": len(text.split()),
            }
        }

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return {"error": str(e)}
