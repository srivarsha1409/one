from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pdfplumber
import re
import os
from dotenv import load_dotenv
import json

# Load environment variables (for API key)
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
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.get("/")
def home():
    return {"message": "AI Resume Insight (OpenRouter) backend running ✅"}

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """Extract text from uploaded PDF and analyze it using OpenRouter AI."""
    try:
        # Step 1: Extract text from PDF
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        if not text.strip():
            return {"error": "No readable text found in PDF."}

        # Step 2: Build prompt
        prompt = f"""
You are an expert resume analysis assistant.
Extract and return structured JSON data with the following schema:

{{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": "",
  "leetcode": "",
  "languages": ["English", "Tamil"],
  "education": {{
      "degree": "",
      "university": "",
      "year": "",
      "gpa": ""
  }},
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

        # Step 3: Send to OpenRouter (GPT-4-Turbo, Claude, etc.)
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # You can change this (see note below)
            messages=[
                {"role": "system", "content": "You are an AI that returns valid JSON resume analysis only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        ai_output = response.choices[0].message.content
        ai_output = ai_output.strip().replace("```json", "").replace("```", "")
        data = json.loads(ai_output)

        # Step 4: Simple ATS scoring
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
