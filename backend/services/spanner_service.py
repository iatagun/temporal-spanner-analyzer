from __future__ import annotations

import os
from spanner.types import TemporalGraph, VertexID
from spanner.core import spanner_for_clique
from spanner.verify import verify_spanner, VerificationError

from backend.models import GraphSchema, CliqueQualitySchema
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
    # max_cliques bounds the Bron-Kerbosch search itself (not just a
    # post-hoc slice), so a dense upload can't force unbounded enumeration
    # before we ever get to trim the result.
    cliques, truncated = maximal_cliques(
        adj, min_size=min_clique_size, max_cliques=max_cliques
    )
    cliques = sorted(cliques, key=len, reverse=True)
    if max_cliques > 0:
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
    set[tuple[str, str]],
    bool,
]:
    cliques, truncated = enumerate_cliques(graph, min_clique_size, max_cliques)
    lbl, max_label, all_spanner_edges, clique_qualities, clique_pairs = (
        build_spanner_from_cliques(graph, cliques)
    )
    return lbl, max_label, cliques, all_spanner_edges, clique_qualities, clique_pairs, truncated
