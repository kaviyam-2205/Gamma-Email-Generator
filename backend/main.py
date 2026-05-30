# ============================================================
# main.py
# Gamma Email Generator — FastAPI Backend
# ============================================================
# ROUTES:
#   POST /api/email/generate  → Generate + Auto Save to DB
#   GET  /health              → Health check
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
import os
from agents import run_email_crew

# ─────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────
load_dotenv()

app = FastAPI(title="Gamma Email Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ─────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────
class EmailRequest(BaseModel):
    input_mail: str
    category: str
    sub_category: str = ""

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "message": "Gamma Email API is running!"}


@app.post("/api/email/generate")
def generate_email(req: EmailRequest):

    # Step 1 — Fetch training examples from DB
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT input_mail, output_mail FROM training_data WHERE category=%s LIMIT 5",
        (req.category,)
    )
    examples = cursor.fetchall()

    # Step 2 — Run 5 agents pipeline
    result = run_email_crew(
        input_mail=req.input_mail,
        category=req.category,
        sub_category=req.sub_category,
        training_examples=examples
    )

    # Step 3 — Auto save to DB
    cursor2 = db.cursor()
    cursor2.execute(
        """INSERT INTO training_data 
        (category, sub_category, input_mail, output_mail) 
        VALUES (%s, %s, %s, %s)""",
        (req.category, req.sub_category,
         req.input_mail, result)
    )
    db.commit()
    db.close()

    return {"output_mail": result}