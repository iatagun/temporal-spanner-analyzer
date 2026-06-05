from __future__ import annotations
from collections import deque
from spanner.types import TemporalGraph, TemporalBiClique, VertexID


def _edge_key(u: VertexID, v: VertexID) -> tuple[VertexID, VertexID]:
    a, b = str(u), str(v)
    return (a, b) if a <= b else (b, a)


def label(v: VertexID, u: VertexID, G: TemporalGraph | TemporalBiClique) -> float:
    return G.label[_edge_key(v, u)]


def Nmin(v: VertexID, G: TemporalGraph | TemporalBiClique) -> VertexID:
    if isinstance(G, TemporalBiClique):
        candidates = [
            w for w in (G.T if v in G.S else G.S)
            if _edge_key(v, w) in G.label
        ]
    else:
        candidates = [w for w in G.V if w != v and _edge_key(v, w) in G.label]
    if not candidates:
        raise ValueError(f"{v} has no neighbours")
    return min(candidates, key=lambda w: label(v, w, G))


def Nmax(v: VertexID, G: TemporalGraph | TemporalBiClique) -> VertexID:
    if isinstance(G, TemporalBiClique):
        candidates = [
            w for w in (G.T if v in G.S else G.S)
            if _edge_key(v, w) in G.label
        ]
    else:
        candidates = [w for w in G.V if w != v and _edge_key(v, w) in G.label]
    if not candidates:
        raise ValueError(f"{v} has no neighbours")
    return max(candidates, key=lambda w: label(v, w, G))


def pos(v: VertexID, u: VertexID, G: TemporalGraph | TemporalBiClique) -> int:
    if isinstance(G, TemporalBiClique):
        neighbors = [
            w for w in (G.T if v in G.S else G.S)
            if _edge_key(v, w) in G.label
        ]
    else:
        neighbors = [w for w in G.V if w != v and _edge_key(v, w) in G.label]
    neighbors.sort(key=lambda w: label(v, w, G))
    try:
        return neighbors.index(u)
    except ValueError:
        return -1


def is_temporal_path(vertices: list[VertexID], G: TemporalGraph | TemporalBiClique) -> bool:
    last = -float("inf")
    for i in range(len(vertices) - 1):
        l = label(vertices[i], vertices[i + 1], G)
        if l < last:
            return False
        last = l
    return True


def induced_subgraph(G: TemporalBiClique, S_sub: set[VertexID], T_sub: set[VertexID]) -> TemporalBiClique:
    sub_lbl = {}
    for s in S_sub:
        for t in T_sub:
            k = _edge_key(s, t)
            if k in G.label:
                sub_lbl[k] = G.label[k]
    return TemporalBiClique(list(S_sub), list(T_sub), sub_lbl)


def induced_subgraph_clique(G: TemporalGraph, V_sub: set[VertexID]) -> TemporalGraph:
    sub_lbl = {}
    for (u, v), t in G.label.items():
        if u in V_sub and v in V_sub:
            sub_lbl[(u, v)] = t
    return TemporalGraph(set(V_sub), sub_lbl)


def exists_temporal_path_in_subgraph(
    start: VertexID, end: VertexID,
    allowed: set[tuple[VertexID, VertexID]],
    G: TemporalGraph | TemporalBiClique,
) -> bool:
    start_s, end_s = str(start), str(end)
    adj: dict[str, list[str]] = {}
    for a, b in allowed:
        sa, sb = str(a), str(b)
        adj.setdefault(sa, []).append(sb)
        adj.setdefault(sb, []).append(sa)
    q: deque[tuple[str, float]] = deque()
    q.append((start_s, -float("inf")))
    visited: set[tuple[str, float]] = {(start_s, -float("inf"))}
    while q:
        v, last_lbl = q.popleft()
        if v == end_s:
            return True
        for w in adj.get(v, []):
            l = label(v, w, G)
            if l >= last_lbl and (w, l) not in visited:
                visited.add((w, l))
                q.append((w, l))
    return False
