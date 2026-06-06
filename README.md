# Gamma AI Email Generator — POC

AI-powered email generation using CrewAI + Ollama + FastAPI + React + MySQL

## Setup Instructions

### Prerequisites
- Python 3.12
- Node.js (LTS)
- MySQL Server
- Ollama

### Backend Setup
cd backend
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install -r requirements.txt
python load_training.py
uvicorn main:app --reload --port 8000

### Frontend Setup
cd frontend
npm install
npm start

### Database Setup
- Create database: gamma_email
- Update .env with your MySQL credentials

### Ollama Setup
ollama pull llama3.2
