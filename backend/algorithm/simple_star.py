from __future__ import annotations
from spanner.types import TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key, Nmin, Nmax, pos


def s_star_ordering(s_star: VertexID, G: TemporalBiClique) -> tuple[list[VertexID], list[VertexID]]:
    T_ord = sorted(G.T, key=lambda t: pos(s_star, t, G))
    S_ord = [Nmin(t, G) for t in T_ord]
    return S_ord, T_ord


def t_star_ordering(t_star: VertexID, G: TemporalBiClique) -> tuple[list[VertexID], list[VertexID]]:
    S_ord = sorted(G.S, key=lambda s: pos(t_star, s, G), reverse=True)
    T_ord = [Nmax(s, G) for s in S_ord]
    return S_ord, T_ord


def simple_star(s_star: VertexID, G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    edges: set[tuple[VertexID, VertexID]] = set()
    for s in G.S:
        edges.add(_edge_key(s, Nmin(s, G)))
    for t in G.T:
        edges.add(_edge_key(s_star, t))
    return edges
