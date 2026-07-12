from fastapi import APIRouter, HTTPException
from pydantic import Field
from typing import List, Optional

from backend.models import GraphSchema, BaseModel
from backend.services.trend_analyzer import compute_trends


class WordCliqueRequest(BaseModel):
    graph: GraphSchema
    word: str
    windows: int = Field(10, ge=1, le=200)


class WordCliqueSnapshotResponse(BaseModel):
    window: int
    window_start: float
    window_end: float
    members: List[str]
    size: int


class WordCliqueItemResponse(BaseModel):
    label: str
    members: List[str]
    description: Optional[str] = None
    snapshots: List[WordCliqueSnapshotResponse]


class WordCliqueResponse(BaseModel):
    word: str
    cliques: List[WordCliqueItemResponse]
    total_snapshots: int


class CheckCliqueRequest(BaseModel):
    graph: GraphSchema
    words: List[str]


class CheckCliqueResponse(BaseModel):
    is_clique: bool
    word_count: int
    edge_count: int
    expected_edges: int
    missing_edges: Optional[List[List[str]]] = None


router = APIRouter()


@router.post("/word-cliques", response_model=WordCliqueResponse)
def word_cliques(req: WordCliqueRequest):
    if not req.word:
        raise HTTPException(400, "word is required")
    trend = compute_trends(req.graph, windows=req.windows)

    cliques_map: dict[str, dict] = {}
    total_snapshots = 0

    for tl in trend.timelines:
        clique_snapshots = []
        for snap in tl.snapshots:
            if req.word in snap.members:
                clique_snapshots.append(WordCliqueSnapshotResponse(
                    window=snap.window,
                    window_start=snap.window_start,
                    window_end=snap.window_end,
                    members=snap.members,
                    size=snap.size,
                ))
                total_snapshots += 1

        if clique_snapshots:
            cliques_map[tl.id] = WordCliqueItemResponse(
                label=tl.label,
                members=sorted({m for s in clique_snapshots for m in s.members}),
                snapshots=clique_snapshots,
            )

    return WordCliqueResponse(
        word=req.word,
        cliques=list(cliques_map.values()),
        total_snapshots=total_snapshots,
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

    missing: list[list[str]] = []
    edge_count = 0
    word_list = sorted(words_set)
    for i in range(len(word_list)):
        for j in range(i + 1, len(word_list)):
            key = (word_list[i], word_list[j])
            if key in edge_map:
                edge_count += 1
            else:
                missing.append([word_list[i], word_list[j]])

    total_pairs = len(word_list) * (len(word_list) - 1) // 2
    return CheckCliqueResponse(
        is_clique=len(missing) == 0,
        word_count=len(word_list),
        edge_count=edge_count,
        expected_edges=total_pairs,
        missing_edges=missing if missing else None,
    )
