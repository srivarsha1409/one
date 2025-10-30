# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    github = Column(String, nullable=True)
    leetcode = Column(String, nullable=True)
    codechef = Column(String, nullable=True)
    codeforces = Column(String, nullable=True)
    hackerrank = Column(String, nullable=True)
    skills_tech = Column(Text, nullable=True)   # JSON string
    skills_soft = Column(Text, nullable=True)   # JSON string
    skills_area_of_interest = Column(Text, nullable=True)  # JSON string
    ats_score = Column(Integer, nullable=True)
    role_match = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
