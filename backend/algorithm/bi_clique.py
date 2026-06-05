from __future__ import annotations
from spanner.types import TemporalGraph, TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key


def clique_to_biclique(G: TemporalGraph) -> tuple[TemporalBiClique, dict]:
    S: list[VertexID] = []
    T: list[VertexID] = []
    lbl: dict[tuple[VertexID, VertexID], float] = {}
    proj: dict[tuple[VertexID, VertexID], tuple[VertexID, VertexID]] = {}

    for v in G.V:
        vs = f"{v}_S"
        vt = f"{v}_T"
        S.append(vs)
        T.append(vt)
        lbl[_edge_key(vs, vt)] = 0.0

    for v in G.V:
        vs = f"{v}_S"
        for u in G.V:
            if u == v:
                continue
            ut = f"{u}_T"
            k = _edge_key(vs, ut)
            lbl[k] = G.label[_edge_key(v, u)]
            proj[k] = (v, u)

    return TemporalBiClique(S, T, lbl), proj
