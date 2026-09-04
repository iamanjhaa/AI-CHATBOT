from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

from app.routes.chat import router as chat_router


app = FastAPI(
    title="SIH26043 Problem Solving Chatbot API",
    description="Phase 1 MVP backend for household and local societal problem guidance.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ai-chatbot-8bde.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "SIH26043 chatbot backend is running"}
