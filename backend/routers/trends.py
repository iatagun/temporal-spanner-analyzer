from fastapi import APIRouter, HTTPException

from backend.models import TrendRequest, TrendResponse
from backend.services.trend_analyzer import compute_trends

router = APIRouter()


@router.post("/trends", response_model=TrendResponse)
def get_trends(req: TrendRequest):
    if not req.graph or not req.graph.edges:
        raise HTTPException(400, "Graph must have at least one edge")
    raw_documents = [(d.label, d.words) for d in req.raw_documents] if req.raw_documents else None
    return compute_trends(
        req.graph,
        windows=req.windows,
        raw_documents=raw_documents,
        pmi_threshold=req.pmi_threshold,
        measure=req.association_measure,
    )
