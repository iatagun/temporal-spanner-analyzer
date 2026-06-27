import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import spanner, trends, compare, explore

app = FastAPI(title="Temporal Spanner API", version="0.1.0")

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3004,http://127.0.0.1:3004").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spanner.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(explore.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "algo": "Baligács 2026"}
