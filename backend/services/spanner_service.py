from __future__ import annotations

import os
from collections import deque
from spanner.types import TemporalGraph, VertexID
from spanner.core import spanner_for_clique
from spanner.verify import verify_spanner, VerificationError

from backend.models import EdgeSchema, GraphSchema, CliqueQualitySchema, MetricSchema, SpannerResponse
from backend.services.graph_utils import build_static_adj, maximal_cliques

_VERIFY = os.getenv("SPANNER_VERIFY", "").lower() in ("1", "true", "yes")


def _build_label_dict(
    graph: GraphSchema,
) -> tuple[dict[tuple[str, str], float], float]:
    lbl: dict[tuple[VertexID, VertexID], float] = {}
    max_label = 0.0
    for e in graph.edges:
        key = (e.u, e.v) if e.u <= e.v else (e.v, e.u)
        if key in lbl:
            if e.label < lbl[key]:
                lbl[key] = e.label
        else:
            lbl[key] = e.label
        if e.label > max_label:
            max_label = e.label
    return lbl, max_label


def _process_clique(
    clique: set[str],
    lbl: dict,
    all_spanner_edges: set[tuple[str, str]],
    clique_pairs: set[tuple[str, str]] | None = None,
) -> CliqueQualitySchema:
    cv_sorted = sorted(clique)
    clique_lbl: dict[tuple[str, str], float] = {}
    for i in range(len(cv_sorted)):
        for j in range(i + 1, len(cv_sorted)):
            key = (cv_sorted[i], cv_sorted[j])
            if key in lbl:
                clique_lbl[key] = lbl[key]
                if clique_pairs is not None:
                    clique_pairs.add(key)

    G = TemporalGraph(clique, clique_lbl)
    E = spanner_for_clique(G)
    before = len(all_spanner_edges)
    all_spanner_edges.update(E)
    added = len(all_spanner_edges) - before

    verified = None
    if _VERIFY:
        try:
            verify_spanner(G, E, 7 * len(clique))
            verified = True
        except VerificationError:
            verified = False

    return CliqueQualitySchema(
        size=len(clique),
        members=cv_sorted,
        spanner_edges=added,
        verified=verified,
    )


def enumerate_cliques(
    graph: GraphSchema,
    min_clique_size: int = 3,
    max_cliques: int = 0,
) -> tuple[list[set[str]], bool]:
    """Bron-Kerbosch enumeration step, split out from spanner construction
    so callers that need cliques at more than one min-size (e.g. /api/compare,
    which wants size>=2 for Jaccard *and* size>=3 for the spanner) can run
    this exponential-cost step once and filter, instead of re-enumerating.
    """
    adj = build_static_adj(graph)
    # max_cliques is deliberately NOT passed into maximal_cliques' search --
    # doing so used to stop Bron-Kerbosch as soon as it had found
    # max_cliques cliques in DFS order, which are not the largest ones, just
    # the first ones the traversal happened to reach. Sorting+slicing that
    # already-truncated set afterward gave the illusion of "top N" while
    # actually returning "first N found, ranked amongst themselves". The
    # search below is bounded only by the recursion budget (still caps
    # runtime on adversarial graphs); max_cliques is applied as a real
    # top-N-by-size selection over that full (budget-bounded) result.
    cliques, truncated = maximal_cliques(adj, min_size=min_clique_size)
    cliques = sorted(cliques, key=len, reverse=True)
    if max_cliques > 0:
        truncated = truncated or len(cliques) > max_cliques
        cliques = cliques[:max_cliques]
    return cliques, truncated


def build_spanner_from_cliques(
    graph: GraphSchema,
    cliques: list[set[str]],
) -> tuple[
    dict[tuple[str, str], float],
    float,
    set[tuple[str, str]],
    list[CliqueQualitySchema],
    set[tuple[str, str]],
]:
    """Spanner construction step: given an already-enumerated clique list,
    build the per-clique spanners and merge them. Polynomial in the size
    of `cliques` -- the expensive part is enumerate_cliques(), not this.
    """
    lbl, max_label = _build_label_dict(graph)

    all_spanner_edges: set[tuple[str, str]] = set()
    clique_pairs: set[tuple[str, str]] = set()
    clique_qualities: list[CliqueQualitySchema] = []

    for clique in cliques:
        cq = _process_clique(clique, lbl, all_spanner_edges, clique_pairs)
        clique_qualities.append(cq)

    for key in lbl:
        if key not in clique_pairs:
            all_spanner_edges.add(key)

    return lbl, max_label, all_spanner_edges, clique_qualities, clique_pairs


def compute_spanner_pipeline(
    graph: GraphSchema,
    min_clique_size: int = 3,
    max_cliques: int = 0,
) -> tuple[
    dict[tuple[str, str], float],
    float,
    list[set[str]],
    set[tuple[str, str]],
    list[CliqueQualitySchema],
    set[tuple[str, str]],
    bool,
]:
    cliques, truncated = enumerate_cliques(graph, min_clique_size, max_cliques)
    lbl, max_label, all_spanner_edges, clique_qualities, clique_pairs = (
        build_spanner_from_cliques(graph, cliques)
    )
    return lbl, max_label, cliques, all_spanner_edges, clique_qualities, clique_pairs, truncated


def _shortest_temporal_path_len(
    start: str, end: str, edges: list[tuple[str, str, float]]
) -> int | None:
    adj: dict[str, list[tuple[str, float]]] = {}
    for u, v, l in edges:
        if u == v:
            continue
        adj.setdefault(u, []).append((v, l))
        adj.setdefault(v, []).append((u, l))
    q: deque[tuple[str, float, int]] = deque()
    q.append((start, -float("inf"), 0))
    visited: set[tuple[str, float]] = {(start, -float("inf"))}
    while q:
        v, last_lbl, dist = q.popleft()
        if v == end:
            return dist
        for w, l in adj.get(v, []):
            if l >= last_lbl and (w, l) not in visited:
                visited.add((w, l))
                q.append((w, l, dist + 1))
    return None


def _compute_stretch_factor(
    lbl: dict,
    E_spanner: set[tuple[str, str]],
    clique_pairs: set[tuple[str, str]],
) -> float:
    all_edges = [
        (a, b, lbl.get((a, b) if a <= b else (b, a), 0.0))
        for a, b in E_spanner
    ]
    orig_edges = [
        (u, v, lbl[(u, v) if u <= v else (v, u)])
        for u, v in lbl
    ]

    pairs = sorted(clique_pairs)
    if len(pairs) > 50:
        pairs = pairs[:50]

    total_ratio = 0.0
    pairs_checked = 0

    for u, v in pairs:
        d_orig = _shortest_temporal_path_len(u, v, orig_edges)
        d_spanner = _shortest_temporal_path_len(u, v, all_edges)
        if d_orig and d_orig > 0:
            if d_spanner is None:
                continue
            total_ratio += d_spanner / d_orig
            pairs_checked += 1

    return round(total_ratio / max(pairs_checked, 1), 2)


def build_spanner_response(
    req_graph: GraphSchema,
    cliques: list[set[str]],
    truncated: bool,
) -> SpannerResponse:
    """Shared SpannerResponse assembly used by both /api/spanner and
    /api/compare -- previously each router hand-built this (the n<2
    short-circuit, the bound_7n coverage loop, the verified tri-state
    reduction, the spanner_edges_out comprehension, the savings/stretch
    formulas) and the two copies had already drifted (compare.py's n<2
    branch silently omitted stretch_factor).
    """
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
                stretch_factor=1.0,
            ),
        )

    lbl, max_label, all_spanner_edges, clique_qualities, clique_pairs = (
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

    # Same per-pair scores the corpus was uploaded with (see
    # graph_builder.compute_association_measures) -- carried onto the
    # spanner's own edges so SpannerView can show "NPMI/G^2/Dice/t" for a
    # kept edge, not just for edges surfaced via /api/word-cliques.
    scores_by_pair: dict[tuple[str, str], dict[str, float]] = {}
    for e in req_graph.edges:
        key = (e.u, e.v) if e.u <= e.v else (e.v, e.u)
        if e.scores:
            scores_by_pair[key] = e.scores

    spanner_edges_out = [
        EdgeSchema(
            u=a, v=b,
            label=lbl.get((a, b) if a <= b else (b, a), 0.0),
            scores=scores_by_pair.get((a, b) if a <= b else (b, a), {}),
        )
        for a, b in all_spanner_edges
    ]

    savings_base = max(uploaded_count, 1)
    savings = round((1 - spanner_count / savings_base) * 100, 1)

    stretch = (
        _compute_stretch_factor(lbl, all_spanner_edges, clique_pairs)
        if spanner_count > 0 and clique_pairs
        else 1.0
    )

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
            stretch_factor=stretch,
            cliques_processed=len(cliques),
            clique_qualities=clique_qualities,
            truncated=truncated,
        ),
    )
