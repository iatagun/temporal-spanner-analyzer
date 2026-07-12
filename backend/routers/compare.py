from fastapi import APIRouter

from backend.models import (
    CompareRequest,
    CompareResponse,
    CompareMetricSchema,
    GraphSchema,
)
from backend.services.spanner_service import build_spanner_response, enumerate_cliques

router = APIRouter()

SPANNER_MIN_CLIQUE_SIZE = 3


def _enumerate_once(graph: GraphSchema) -> tuple[list[set[str]], list[set[str]], bool]:
    """Bron-Kerbosch is the expensive step here, so it runs exactly once
    per graph at the loosest size (>=2, needed for the Jaccard/clique-count
    comparison). The size>=3 subset used for the spanner is then a cheap
    filter over already-enumerated maximal cliques, not a second search --
    maximality doesn't depend on the min-size threshold, so this is exactly
    the set enumerate_cliques(graph, min_clique_size=3) would have found.
    """
    all_cliques, truncated = enumerate_cliques(graph, min_clique_size=2)
    spanner_cliques = [c for c in all_cliques if len(c) >= SPANNER_MIN_CLIQUE_SIZE]
    return all_cliques, spanner_cliques, truncated


def _clique_jaccard(a: list[set[str]], b: list[set[str]]) -> float:
    if not a and not b:
        return 1.0
    a_sigs = {frozenset(c) for c in a}
    b_sigs = {frozenset(c) for c in b}
    inter = a_sigs & b_sigs
    union = a_sigs | b_sigs
    return round(len(inter) / len(union), 3) if union else 1.0


@router.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest):
    c1, spanner_cliques1, c1_truncated = _enumerate_once(req.graph1)
    c2, spanner_cliques2, c2_truncated = _enumerate_once(req.graph2)

    s1 = build_spanner_response(req.graph1, spanner_cliques1, c1_truncated)
    s2 = build_spanner_response(req.graph2, spanner_cliques2, c2_truncated)

    v1 = set(req.graph1.vertices)
    v2 = set(req.graph2.vertices)
    e1 = {(e.u, e.v) for e in req.graph1.edges}
    e2 = {(e.u, e.v) for e in req.graph2.edges}

    v_union = len(v1 | v2)
    v_intersection = len(v1 & v2)
    v_overlap = round(v_intersection / v_union * 100, 1) if v_union else 0.0

    e_union = len(e1 | e2)
    e_intersection = len(e1 & e2)
    e_overlap = round(e_intersection / e_union * 100, 1) if e_union else 0.0

    savings_diff = round(s1.metrics.savings_pct - s2.metrics.savings_pct, 1)
    if savings_diff > 0:
        savings_compare = f"{req.label1} wins by {savings_diff}%"
    elif savings_diff < 0:
        savings_compare = f"{req.label2} wins by {abs(savings_diff)}%"
    else:
        savings_compare = "Equal"

    clique_jaccard = _clique_jaccard(c1, c2)

    return CompareResponse(
        spanner1=s1,
        spanner2=s2,
        comparison=CompareMetricSchema(
            vertex_union=v_union,
            vertex_intersection=v_intersection,
            vertex_overlap_pct=v_overlap,
            edge_union=e_union,
            edge_intersection=e_intersection,
            edge_overlap_pct=e_overlap,
            savings_compare=savings_compare,
            clique_count_1=len(c1),
            clique_count_2=len(c2),
            clique_jaccard=clique_jaccard,
            cliques_processed_1=s1.metrics.cliques_processed,
            cliques_processed_2=s2.metrics.cliques_processed,
            truncated=c1_truncated or c2_truncated,
        ),
    )
