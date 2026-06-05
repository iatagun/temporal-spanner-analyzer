from __future__ import annotations
from spanner.types import TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key, Nmin, Nmax, pos
from backend.algorithm.simple_star import s_star_ordering, t_star_ordering


def _emin_edges(G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    e: set[tuple[VertexID, VertexID]] = set()
    for s in G.S:
        e.add(_edge_key(s, Nmin(s, G)))
    for t in G.T:
        e.add(_edge_key(t, Nmin(t, G)))
    return e


def _emax_edges(G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    e: set[tuple[VertexID, VertexID]] = set()
    for s in G.S:
        e.add(_edge_key(s, Nmax(s, G)))
    for t in G.T:
        e.add(_edge_key(t, Nmax(t, G)))
    return e


def extend_index_s_star(
    s: VertexID, s_star: VertexID,
    _S_ord: list[VertexID], T_ord: list[VertexID],
    G: TemporalBiClique,
) -> int | None:
    max_l: int | None = None
    for l in range(len(T_ord)):
        t_l = T_ord[l]
        if pos(t_l, s, G) > pos(t_l, s_star, G):
            max_l = l
    return max_l


def extended_star_s_star(s_star: VertexID, G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    edges = _emin_edges(G) | _emax_edges(G)
    for t in G.T:
        edges.add(_edge_key(s_star, t))
    S_ord, T_ord = s_star_ordering(s_star, G)
    for s in G.S:
        if s == s_star:
            continue
        idx = extend_index_s_star(s, s_star, S_ord, T_ord, G)
        if idx is not None:
            edges.add(_edge_key(s, T_ord[idx]))
    return edges


def extend_index_t_star(
    t: VertexID, t_star: VertexID,
    S_ord: list[VertexID], _T_ord: list[VertexID],
    G: TemporalBiClique,
) -> int | None:
    max_l: int | None = None
    for l in range(len(S_ord)):
        s_l = S_ord[l]
        if pos(s_l, t, G) < pos(s_l, t_star, G):
            max_l = l
    return max_l


def extended_star_t_star(t_star: VertexID, G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    edges = _emin_edges(G) | _emax_edges(G)
    for s in G.S:
        edges.add(_edge_key(s, t_star))
    S_ord, T_ord = t_star_ordering(t_star, G)
    for t in G.T:
        if t == t_star:
            continue
        idx = extend_index_t_star(t, t_star, S_ord, T_ord, G)
        if idx is not None:
            edges.add(_edge_key(S_ord[idx], t))
    return edges
