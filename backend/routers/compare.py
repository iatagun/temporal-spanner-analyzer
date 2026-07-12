from fastapi import APIRouter

from backend.models import (
    CompareRequest,
    CompareResponse,
    CompareMetricSchema,
    SpannerResponse,
    GraphSchema,
    EdgeSchema,
    MetricSchema,
)
from backend.services.spanner_service import (
    build_spanner_from_cliques,
    enumerate_cliques,
)

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


def _compute_spanner_response(
    req_graph: GraphSchema, cliques: list[set[str]], truncated: bool
) -> SpannerResponse:
    V = set(req_graph.vertices)
    n = len(V)

    if n < 2:
        return SpannerResponse(
            original=req_graph,
            spanner=GraphSchema(vertices=sorted(V, key=str), edges=[]),
            cliques=[],
            metrics=MetricSchema(
                uploaded_edges=len(req_graph.edges),
                full_clique_edges=0,
                spanner_edges=0,
                bound_7n=0,
                ratio_per_n=0.0,
                savings_pct=0.0,
                verified=True,
            ),
        )

    lbl, max_label, all_spanner_edges, clique_qualities, _clique_pairs = (
        build_spanner_from_cliques(req_graph, cliques)
    )

    uploaded_count = len(req_graph.edges)
    spanner_count = len(all_spanner_edges)

    vertices_in_cliques: set[str] = set()
    for c in cliques:
        vertices_in_cliques.update(c)
    n_covered = len(vertices_in_cliques)
    bound = 7 * max(n_covered, 1)
    for v in V:
        if v not in vertices_in_cliques:
            bound += 1

    verified_results = [cq.verified for cq in clique_qualities] if clique_qualities else []
    if not verified_results:
        all_verified = None
    elif all(v is None for v in verified_results):
        all_verified = None
    else:
        all_verified = all(v for v in verified_results if v is not None)

    spanner_edges_out = [
        EdgeSchema(u=a, v=b, label=lbl.get((a, b) if a <= b else (b, a), 0.0))
        for a, b in all_spanner_edges
    ]

    savings_base = max(uploaded_count, 1)
    savings = round((1 - spanner_count / savings_base) * 100, 1)

    return SpannerResponse(
        original=req_graph,
        spanner=GraphSchema(vertices=sorted(V, key=str), edges=spanner_edges_out),
        cliques=[sorted(c) for c in cliques],
        metrics=MetricSchema(
            uploaded_edges=uploaded_count,
            full_clique_edges=len(lbl),
            spanner_edges=spanner_count,
            bound_7n=bound,
            ratio_per_n=round(spanner_count / max(n, 1), 2),
            savings_pct=savings,
            verified=all_verified,
            cliques_processed=len(cliques),
            clique_qualities=clique_qualities,
            truncated=truncated,
        ),
    )


@router.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest):
    c1, spanner_cliques1, c1_truncated = _enumerate_once(req.graph1)
    c2, spanner_cliques2, c2_truncated = _enumerate_once(req.graph2)

    s1 = _compute_spanner_response(req.graph1, spanner_cliques1, c1_truncated)
    s2 = _compute_spanner_response(req.graph2, spanner_cliques2, c2_truncated)

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
