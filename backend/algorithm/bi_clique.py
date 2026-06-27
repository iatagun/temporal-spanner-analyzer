from __future__ import annotations
from spanner.types import TemporalGraph, TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key


def clique_to_biclique(G: TemporalGraph) -> tuple[TemporalBiClique, dict]:
    S: list[VertexID] = []
    T: list[VertexID] = []
    lbl: dict[tuple[VertexID, VertexID], float] = {}
    proj: dict[tuple[VertexID, VertexID], tuple[VertexID, VertexID]] = {}

    s_map: dict[VertexID, str] = {}
    t_map: dict[VertexID, str] = {}
    for v in G.V:
        vs = f"{v}_S"
        vt = f"{v}_T"
        s_map[v] = vs
        t_map[v] = vt
        S.append(vs)
        T.append(vt)
        lbl[(vs, vt)] = 0.0

    for v in G.V:
        vs = s_map[v]
        for u in G.V:
            if u == v:
                continue
            ut = t_map[u]
            k = _edge_key(vs, ut)
            lbl[k] = G.label[_edge_key(v, u)]
            proj[k] = (v, u)

    return TemporalBiClique(S, T, lbl), proj
