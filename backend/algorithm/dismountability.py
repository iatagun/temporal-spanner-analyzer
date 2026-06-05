from __future__ import annotations
from spanner.types import TemporalGraph, TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import (
    _edge_key, Nmin, Nmax, pos, is_temporal_path,
    induced_subgraph, induced_subgraph_clique,
)


def dismountability(G: TemporalBiClique) -> tuple[set[VertexID], set[VertexID], set[tuple[VertexID, VertexID]]]:
    S_cur = set(G.S)
    T_cur = set(G.T)
    E_add: set[tuple[VertexID, VertexID]] = set()

    Gc = lambda: induced_subgraph(G, S_cur, T_cur)

    changed = True
    while changed:
        changed = False
        for s in list(S_cur):
            Gi = Gc()
            t = Nmin(s, Gi)
            for s2 in list(S_cur):
                if s2 == s:
                    continue
                if pos(t, s2, Gi) < pos(t, s, Gi):
                    S_cur.remove(s2)
                    E_add.add(_edge_key(s, t))
                    E_add.add(_edge_key(s2, t))
                    changed = True
                    break
            if changed:
                break
        if changed:
            continue
        for t in list(T_cur):
            Gi = Gc()
            s = Nmax(t, Gi)
            for t2 in list(T_cur):
                if t2 == t:
                    continue
                if pos(s, t2, Gi) > pos(s, t, Gi):
                    T_cur.remove(t2)
                    E_add.add(_edge_key(s, t))
                    E_add.add(_edge_key(s, t2))
                    changed = True
                    break
            if changed:
                break

    return S_cur, T_cur, E_add


def is_12_hop_dismountable(v: VertexID, G: TemporalGraph) -> tuple[bool, VertexID | None, VertexID | None]:
    for u in G.V:
        if u == v:
            continue
        try:
            nmin_u = Nmin(u, G)
        except ValueError:
            continue
        if nmin_u == v:
            continue
        if is_temporal_path([v, nmin_u, u], G):
            for w in G.V:
                if w in (v, u):
                    continue
                try:
                    nmax_w = Nmax(w, G)
                except ValueError:
                    continue
                if nmax_w in (v, w):
                    continue
                if is_temporal_path([w, nmax_w, v], G):
                    return True, u, w
    return False, None, None


def dismountability_12_hop(G: TemporalGraph) -> tuple[set[VertexID], set[tuple[VertexID, VertexID]]]:
    V_cur: set[VertexID] = set(G.V)
    E_add: set[tuple[VertexID, VertexID]] = set()
    changed = True
    while changed:
        changed = False
        for v in list(V_cur):
            Gi = induced_subgraph_clique(G, V_cur)
            ok, u, w = is_12_hop_dismountable(v, Gi)
            if ok:
                V_cur.remove(v)
                E_add.add(_edge_key(v, Nmin(u, Gi)))
                E_add.add(_edge_key(Nmin(u, Gi), u))
                E_add.add(_edge_key(w, Nmax(w, Gi)))
                E_add.add(_edge_key(Nmax(w, Gi), v))
                changed = True
                break
    return V_cur, E_add
