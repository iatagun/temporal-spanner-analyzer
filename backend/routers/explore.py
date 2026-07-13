from fastapi import APIRouter, HTTPException
from pydantic import Field
from typing import List, Optional

from backend.models import GraphSchema, BaseModel, RawDocumentSchema, AssociationMeasure
from backend.services.trend_analyzer import compute_trends
from backend.services.graph_builder import extract_mwe_candidates, bootstrap_confidence_interval


class WordCliqueRequest(BaseModel):
    graph: GraphSchema
    word: str
    windows: int = Field(10, ge=1, le=200)
    raw_documents: List[RawDocumentSchema] = []
    pmi_threshold: float = Field(0.15, ge=-1000.0, le=1000.0)
    association_measure: AssociationMeasure = "npmi"


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
    truncated: bool = False


class MWECandidateRequest(BaseModel):
    raw_documents: List[RawDocumentSchema]
    max_n: int = Field(4, ge=2, le=8)
    min_freq: int = Field(2, ge=1, le=1000)
    top_n: int = Field(50, ge=1, le=500)


class MWECandidateItem(BaseModel):
    ngram: List[str]
    text: str
    frequency: int
    c_value: float


class MWECandidateResponse(BaseModel):
    candidates: List[MWECandidateItem]


class PairConfidenceRequest(BaseModel):
    raw_documents: List[RawDocumentSchema]
    word1: str
    word2: str
    association_measure: AssociationMeasure = "npmi"
    n_resamples: int = Field(500, ge=50, le=2000)


class PairConfidenceResponse(BaseModel):
    lower: float
    upper: float
    point_estimate: float


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
    raw_documents = [(d.label, d.words) for d in req.raw_documents] if req.raw_documents else None
    trend = compute_trends(
        req.graph,
        windows=req.windows,
        raw_documents=raw_documents,
        pmi_threshold=req.pmi_threshold,
        measure=req.association_measure,
    )

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
        truncated=trend.truncated,
    )


@router.post("/mwe-candidates", response_model=MWECandidateResponse)
def mwe_candidates(req: MWECandidateRequest):
    # Needs the raw per-document word lists (not graph.edges, which only
    # carries pairs) to build contiguous n-grams -- same "raw_documents,
    # not graph" pattern as trend_analyzer's windowed recompute.
    if not req.raw_documents:
        raise HTTPException(400, "raw_documents is required")
    word_rows = [d.words for d in req.raw_documents]
    candidates = extract_mwe_candidates(
        word_rows, max_n=req.max_n, min_freq=req.min_freq, top_n=req.top_n
    )
    return MWECandidateResponse(candidates=[MWECandidateItem(**c) for c in candidates])


@router.post("/pair-confidence", response_model=PairConfidenceResponse)
def pair_confidence(req: PairConfidenceRequest):
    # Opt-in, single-pair, on-demand -- see
    # graph_builder.bootstrap_confidence_interval's docstring for why this
    # is never computed automatically for every pair in a corpus.
    if not req.raw_documents:
        raise HTTPException(400, "raw_documents is required")
    if not req.word1 or not req.word2:
        raise HTTPException(400, "word1 and word2 are required")
    word_rows = [d.words for d in req.raw_documents]
    lower, upper, point = bootstrap_confidence_interval(
        word_rows, req.word1, req.word2,
        measure=req.association_measure, n_resamples=req.n_resamples,
    )
    return PairConfidenceResponse(lower=lower, upper=upper, point_estimate=point)


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
