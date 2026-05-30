# ============================================================
# load_training.py
# Gamma Email Generator — EML Training Data Loader
# ============================================================
# FLOW:
#   1. Reads .eml files from training_data/ folder
#   2. Extracts category from folder name
#   3. Extracts sub_category from file name
#   4. Extracts plain text from .eml
#      (falls back to HTML → text if no plain text found)
#   5. Saves to MySQL training_data table
# ============================================================

import os
import re
import email
from email import policy
from dotenv import load_dotenv
import mysql.connector

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────
load_dotenv()

TRAINING_FOLDER = os.path.join(os.path.dirname(__file__), "training_data")

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
# EXTRACT PLAIN TEXT FROM HTML
# ─────────────────────────────────────────
def html_to_text(html: str) -> str:
    # Remove style blocks
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # Remove script blocks
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    # Replace <br> and <p> with newlines
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<p[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
    html = re.sub(r'<h[1-6][^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</h[1-6]>', '\n', html, flags=re.IGNORECASE)
    # Remove all remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&#39;', "'")
    # Clean up extra whitespace
    html = re.sub(r'\n\s*\n', '\n\n', html)
    html = re.sub(r' +', ' ', html)
    return html.strip()

# ─────────────────────────────────────────
# EXTRACT BODY FROM .EML FILE
# ─────────────────────────────────────────
def extract_body(eml_path: str) -> str:
    with open(eml_path, "r", encoding="utf-8", errors="ignore") as f:
        msg = email.message_from_file(f, policy=policy.default)

    body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get_content_disposition())

            # Skip attachments
            if "attachment" in disposition:
                continue

            # Prefer plain text
            if content_type == "text/plain" and not body:
                body = part.get_content()

            # Fallback to HTML
            elif content_type == "text/html" and not html_body:
                html_body = part.get_content()

    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body = msg.get_content()
        elif content_type == "text/html":
            html_body = msg.get_content()

    # If no plain text — extract from HTML
    if not body and html_body:
        body = html_to_text(html_body)

    return body.strip()

# ─────────────────────────────────────────
# FORMAT SUB CATEGORY FROM FILE NAME
# ─────────────────────────────────────────
def format_sub_category(filename: str) -> str:
    name = filename.replace(".eml", "")
    name = name.replace("_", " ")
    return name.title()

# ─────────────────────────────────────────
# MAIN LOADER
# ─────────────────────────────────────────
def load_training_data():
    db = get_db()
    cursor = db.cursor()

    total = 0
    skipped = 0

    print("\n📂 Starting EML Training Data Loader...\n")

    # Loop through category folders
    for category in os.listdir(TRAINING_FOLDER):
        category_path = os.path.join(TRAINING_FOLDER, category)

        if not os.path.isdir(category_path):
            continue

        print(f"📁 Category: {category}")

        # Loop through .eml files
        for filename in os.listdir(category_path):
            if not filename.endswith(".eml"):
                continue

            eml_path = os.path.join(category_path, filename)
            sub_category = format_sub_category(filename)

            # Extract body
            body = extract_body(eml_path)

            if not body:
                print(f"   ⚠️  Skipped (empty body): {filename}")
                skipped += 1
                continue

            # Save to DB
            cursor.execute(
                """INSERT INTO training_data 
                (category, sub_category, input_mail, output_mail) 
                VALUES (%s, %s, %s, %s)""",
                (category, sub_category, body, body)
            )
            db.commit()
            total += 1
            print(f"   ✅ Loaded: {filename} → {sub_category}")

    db.close()

    print(f"\n🎉 Done! {total} files loaded, {skipped} skipped.\n")

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    load_training_data()