from fastapi import APIRouter, HTTPException
from typing import List

from backend.models import GraphSchema, BaseModel
from backend.services.trend_analyzer import compute_trends


class WordCliqueRequest(BaseModel):
    graph: GraphSchema
    word: str
    windows: int = 10


class WordCliqueSnapshot(BaseModel):
    window: int
    window_start: float
    window_end: float
    clique_id: str
    clique_label: str
    members: List[str]
    size: int


class WordCliqueResponse(BaseModel):
    word: str
    time_range: List[float]
    snapshots: List[WordCliqueSnapshot]
    timeline_count: int


class CheckCliqueRequest(BaseModel):
    graph: GraphSchema
    words: List[str]


class CheckCliqueResponse(BaseModel):
    is_clique: bool
    total_pairs: int
    missing_pairs: List[tuple[str, str]]
    edge_count: int


router = APIRouter()


@router.post("/word-cliques", response_model=WordCliqueResponse)
def word_cliques(req: WordCliqueRequest):
    if not req.word:
        raise HTTPException(400, "word is required")
    trend = compute_trends(req.graph, windows=req.windows)

    snapshots: list[WordCliqueSnapshot] = []
    for tl in trend.timelines:
        for snap in tl.snapshots:
            if req.word in snap.members:
                snapshots.append(WordCliqueSnapshot(
                    window=snap.window,
                    window_start=snap.window_start,
                    window_end=snap.window_end,
                    clique_id=tl.id,
                    clique_label=tl.label,
                    members=snap.members[:],
                    size=snap.size,
                ))

    return WordCliqueResponse(
        word=req.word,
        time_range=trend.time_range,
        snapshots=snapshots,
        timeline_count=len({s.clique_id for s in snapshots}),
    )


@router.post("/check-clique", response_model=CheckCliqueResponse)
def check_clique(req: CheckCliqueRequest):
    if len(req.words) < 2:
        raise HTTPException(400, "At least 2 words required")

    words_set = set(req.words)
    edge_map: dict[tuple[str, str], float] = {}
    for e in req.graph.edges:
        a, b = (e.u, e.v) if e.u <= e.v else (e.v, e.u)
        edge_map[(a, b)] = e.label

    missing: list[tuple[str, str]] = []
    edge_count = 0
    word_list = sorted(words_set)
    for i in range(len(word_list)):
        for j in range(i + 1, len(word_list)):
            key = (word_list[i], word_list[j])
            if key in edge_map:
                edge_count += 1
            else:
                missing.append(key)

    total_pairs = len(word_list) * (len(word_list) - 1) // 2
    return CheckCliqueResponse(
        is_clique=len(missing) == 0,
        total_pairs=total_pairs,
        missing_pairs=missing,
        edge_count=edge_count,
    )
