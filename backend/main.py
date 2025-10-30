# main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .models import ResumeAnalysis
from .routes import admin_routes

load_dotenv()

app = FastAPI(title="Resume Keyword Generator API")

# create tables
Base.metadata.create_all(bind=engine)

# CORS
origins = os.getenv("CORS_ORIGINS", "")
if origins:
    origins = [o.strip() for o in origins.split(",")]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount router
app.include_router(admin_routes.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"status": "ok"}
