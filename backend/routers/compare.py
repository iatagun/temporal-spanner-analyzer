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
from backend.services.graph_utils import build_static_adj, maximal_cliques
from backend.services.spanner_service import compute_spanner_pipeline

router = APIRouter()


def _maximal_cliques_from_graph(g: GraphSchema) -> list[set[str]]:
    adj = build_static_adj(g)
    return maximal_cliques(adj, min_size=2)


def _clique_jaccard(a: list[set[str]], b: list[set[str]]) -> float:
    if not a and not b:
        return 1.0
    a_sigs = {frozenset(c) for c in a}
    b_sigs = {frozenset(c) for c in b}
    inter = a_sigs & b_sigs
    union = a_sigs | b_sigs
    return round(len(inter) / len(union), 3) if union else 1.0


def _compute_spanner_response(req_graph: GraphSchema) -> SpannerResponse:
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

    lbl, max_label, cliques, all_spanner_edges, clique_qualities, edges_covered, _ = (
        compute_spanner_pipeline(req_graph)
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

    all_verified = (
        all(cq.verified for cq in clique_qualities) if clique_qualities else True
    )

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
        ),
    )


@router.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest):
    s1 = _compute_spanner_response(req.graph1)
    s2 = _compute_spanner_response(req.graph2)

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

    c1 = _maximal_cliques_from_graph(req.graph1)
    c2 = _maximal_cliques_from_graph(req.graph2)
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
        ),
    )
