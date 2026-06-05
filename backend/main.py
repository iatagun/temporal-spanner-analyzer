from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import spanner, trends, compare, explore

app = FastAPI(title="Temporal Spanner API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
