from __future__ import annotations
import random
from spanner.types import TemporalGraph, TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key, label, Nmin, Nmax, induced_subgraph_clique
from backend.algorithm.dismountability import dismountability_12_hop
from backend.algorithm.bi_clique import clique_to_biclique
from backend.algorithm.main_algorithm import spanner_for_biclique, spanner_for_EM_biclique


def spanner_for_clique(G: TemporalGraph) -> set[tuple[VertexID, VertexID]]:
    V_prime, E_dismount = dismountability_12_hop(G)

    if len(V_prime) < 2:
        return E_dismount

    Gi = induced_subgraph_clique(G, V_prime)
    V_minus: set[VertexID] = set()
    V_plus: set[VertexID] = set()
    for v in V_prime:
        V_minus.add(Nmin(v, Gi))
        V_plus.add(Nmax(v, Gi))

    is_partition = (V_minus | V_plus == V_prime) and V_minus.isdisjoint(V_plus)

    if is_partition and len(V_minus) == len(V_plus) and len(V_minus) > 0:
        lbl: dict[tuple[VertexID, VertexID], float] = {}
        for s in V_minus:
            for t in V_plus:
                lbl[_edge_key(s, t)] = label(s, t, G)
        G_bc = TemporalBiClique(list(V_minus), list(V_plus), lbl)
        E_bc = spanner_for_EM_biclique(G_bc)
        E_total = E_dismount | {_edge_key(s, t) for s, t in E_bc}
    else:
        G_fb_lbl: dict[tuple[VertexID, VertexID], float] = {}
        for (u, v), t in G.label.items():
            if u in V_prime and v in V_prime:
                G_fb_lbl[(u, v)] = t
        G_fb = TemporalGraph(V_prime, G_fb_lbl)
        G_bc_fb, proj = clique_to_biclique(G_fb)
        E_fb = spanner_for_biclique(G_bc_fb)
        E_proj: set[tuple[VertexID, VertexID]] = set()
        for s, t in E_fb:
            if (s, t) in proj:
                E_proj.add(proj[(s, t)])
        E_total = E_dismount | E_proj

    cap = len(G.V) * (len(G.V) - 1) // 2
    if len(E_total) > cap:
        V_list = sorted(G.V)
        E_total = {(V_list[i], V_list[j]) for i in range(len(V_list)) for j in range(i + 1, len(V_list))}
    return E_total


def random_temporal_clique(n: int, seed: int | None = None) -> TemporalGraph:
    if seed is not None:
        random.seed(seed)
    V = set(range(n))
    lbl: dict[tuple[int, int], float] = {}
    for i in range(n):
        for j in range(i + 1, n):
            lbl[(i, j)] = random.random()
    return TemporalGraph(V, lbl)
