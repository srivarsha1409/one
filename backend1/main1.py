from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import spacy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    text = text.replace("https://https://", "https://")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    with pdfplumber.open(file.file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    text = clean_text(text)
    doc = nlp(text)

    # --- Basic Details ---
    name = ""
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            break

    if not name:
        m = re.search(r'^[A-Z][A-Za-z\s]{2,25}$', text)
        if m:
            name = m.group(0)

    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phones = re.findall(r'\b\d{10}\b', text)

    github = re.search(r'(https?://(?:www\.)?github\.com/[^\s]+)', text)
    linkedin = re.search(r'(https?://(?:www\.)?linkedin\.com/[^\s]+)', text)
    leetcode = re.search(r'(https?://(?:www\.)?leetcode\.com/[^\s]+)', text)

    # --- Education Section ---
    edu_section = re.search(r'EDUCATION(.*?)(PROJECT|INTERNSHIP|EXPERIENCE|DECLARATION|$)', text, re.IGNORECASE | re.DOTALL)
    education_text = edu_section.group(1).strip() if edu_section else ""

    degree_match = re.search(r'(B\.?E\.?|BTech|Bachelor).*?(Engineering|Technology).*', education_text, re.IGNORECASE)
    degree = degree_match.group(0).strip() if degree_match else "Not Found"

    uni_match = re.search(r'(Institute|College|University).*?(Technology|Engineering|Science).*', education_text)
    university = uni_match.group(0).strip() if uni_match else "Not Found"

    gpa_match = re.search(r'GPA[:\s]*([0-9.]+)', education_text)
    gpa = gpa_match.group(1) if gpa_match else "Not Found"

    year_match = re.search(r'(\b20\d{2}\b)', education_text)
    grad_year = year_match.group(1) if year_match else "Not Found"

    # --- Internship / Project Section ---
    proj_section = re.search(r'(PROJECT|INTERNSHIP).*?(EDUCATION|DECLARATION|$)', text, re.IGNORECASE | re.DOTALL)
    project_text = proj_section.group(0) if proj_section else ""

    # Try to extract project/company names
    projects = re.findall(r'([A-Z][A-Za-z\s]{3,})\s*(?:This project|Project|uses|predicts|developed|created)', project_text)

    # Technologies used
    tech_keywords = ["Python", "Machine Learning", "Deep Learning", "CNN", "Random Forest", "XGBoost", "Data Science"]
    used_tech = [t for t in tech_keywords if re.search(rf'\b{t}\b', project_text, re.IGNORECASE)]

    internships = [{
        "company": projects[0] if projects else "Not Found",
        "position": "Student Project / Intern",
        "duration": "Detected automatically",
        "technologies": ", ".join(used_tech) if used_tech else "Detected automatically"
    }]

    # --- Skills ---
    skills_section = re.search(r'SKILLS(.*?)(PROJECT|EDUCATION|LANGUAGES|$)', text, re.IGNORECASE | re.DOTALL)
    skills_text = skills_section.group(1) if skills_section else ""
    keywords = ["Python", "Java", "C", "C++", "Machine Learning", "Deep Learning",
                "Data Science", "Git", "Flask", "HTML", "CSS", "React"]
    tech_skills = [k for k in keywords if re.search(rf'\b{k}\b', skills_text, re.IGNORECASE)]

    # --- Languages ---
    lang_section = re.search(r'LANGUAGES(.*?)(AREA|PROJECT|EDUCATION|$)', text, re.IGNORECASE | re.DOTALL)
    languages = []
    if lang_section:
        langs = lang_section.group(1)
        languages = re.findall(r'(English|Tamil|Hindi|French)', langs, re.IGNORECASE)
    languages = list(set(languages)) or ["English"]

    # --- ATS Score ---
    ats_score = min(100, len(tech_skills) * 10 + 20)

    # --- Summary ---
    summary = " ".join(text.split()[:80]) + "..."

    return {
        "data": {
            "name": name or "Not Found",
            "email": emails[0] if emails else "Not Found",
            "phone": phones[0] if phones else "Not Found",
            "linkedin": linkedin.group(1) if linkedin else "Not Found",
            "github": github.group(1) if github else "Not Found",
            "leetcode": leetcode.group(1) if leetcode else "Not Found",
            "education": {
                "degree": degree,
                "university": university,
                "gpa": gpa,
                "year": grad_year
            },
            "internships": internships,
            "skills": {
                "technical": tech_skills,
                "soft": ["Communication", "Teamwork", "Problem Solving"]
            },
            "languages": languages,
            "ats_score": ats_score,
            "summary": summary,
            "word_count": len(text.split()),
            "role_match": "Data Scientist / ML Engineer"
        }
    }
