from __future__ import annotations
from spanner.types import TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key, pos, Nmax


def is_3_hop_k_cut_crossing(
    s_i: VertexID, i: int, k: int,
    t_i: VertexID,
    s_star: VertexID,
    T_ord: list[VertexID],
    G: TemporalBiClique,
) -> bool:
    if i <= k:
        return False
    for t in G.T:
        v = Nmax(t, G)
        if not (pos(t_i, s_i, G) <= pos(t_i, v, G)):
            continue
        for j_idx in range(k + 1):
            t_j = T_ord[j_idx]
            if not (pos(v, t_i, G) <= pos(v, t_j, G)):
                continue
            if not (pos(t_j, v, G) <= pos(t_j, s_star, G)):
                continue
            return True
    return False


def find_3_hop_crossing_path(
    s_i: VertexID, _i: int, k: int,
    t_i: VertexID,
    s_star: VertexID,
    T_ord: list[VertexID],
    G: TemporalBiClique,
) -> list[tuple[VertexID, VertexID]]:
    for t in G.T:
        v = Nmax(t, G)
        if not (pos(t_i, s_i, G) <= pos(t_i, v, G)):
            continue
        for j_idx in range(k + 1):
            t_j = T_ord[j_idx]
            if not (pos(v, t_i, G) <= pos(v, t_j, G)):
                continue
            if not (pos(t_j, v, G) <= pos(t_j, s_star, G)):
                continue
            return [_edge_key(s_i, t_i), _edge_key(t_i, v), _edge_key(v, t_j)]
    raise RuntimeError("Lemma 16 guarantees path exists but not found")


def lemma16_check(
    i: int, k: int,
    s_star: VertexID,
    S_ord: list[VertexID], T_ord: list[VertexID],
    G: TemporalBiClique,
) -> tuple[str, int | None]:
    if i <= k:
        return ("extended", i)
    s_i = S_ord[i]
    t_i = T_ord[i]
    if is_3_hop_k_cut_crossing(s_i, i, k, t_i, s_star, T_ord, G):
        return ("crossing", None)
    return ("extended", i)
