from __future__ import annotations
from spanner.types import TemporalBiClique, VertexID
from backend.algorithm.temporal_graph import _edge_key, Nmax
from backend.algorithm.simple_star import s_star_ordering, simple_star
from backend.algorithm.extended_star import extended_star_s_star, extended_star_t_star
from backend.algorithm.cut_crossing import lemma16_check, find_3_hop_crossing_path
from backend.algorithm.dismountability import dismountability, induced_subgraph


def lemma17_find_cover(
    G: TemporalBiClique,
) -> tuple[set[tuple[VertexID, VertexID]], str, set[VertexID], set[VertexID]]:
    n = len(G.S)
    if n < 3:
        E_star: set[tuple[VertexID, VertexID]] = set()
        for s in G.S:
            for t in G.T:
                k = _edge_key(s, t)
                if k in G.label:
                    E_star.add(k)
        return E_star, "trivial", set(G.S), set(G.T)
    k = n // 2
    s_star = G.S[0]
    S_ord, T_ord = s_star_ordering(s_star, G)

    all_crossing = True
    for i in range(k + 1, n):
        cas, _ = lemma16_check(i, k, s_star, S_ord, T_ord, G)
        if cas != "crossing":
            all_crossing = False
            break

    if all_crossing:
        E_star = simple_star(s_star, G)
        for i in range(k + 1, n):
            s_i = S_ord[i]
            t_i = T_ord[i]
            for e in find_3_hop_crossing_path(s_i, i, k, t_i, s_star, T_ord, G):
                E_star.add(e)
        for s in G.S:
            E_star.add(_edge_key(s, Nmax(s, G)))
        for t in G.T:
            E_star.add(_edge_key(t, Nmax(t, G)))
        S_rem: set[VertexID] = set(G.S)
        T_rem: set[VertexID] = set(T_ord[:k])
        return E_star, "S_Tprime", S_rem, T_rem
    else:
        for i in range(k + 1, n):
            cas, _ = lemma16_check(i, k, s_star, S_ord, T_ord, G)
            if cas == "extended":
                t_i = T_ord[i]
                E_star = extended_star_s_star(s_star, G) | extended_star_t_star(t_i, G)
                S_rem = set(S_ord[k + 1:])
                T_rem: set[VertexID] = set(G.T)
                return E_star, "Sprime_T", S_rem, T_rem

    raise RuntimeError("Lemma 17 violated - unreachable")


def spanner_for_EM_biclique(G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    n = len(G.S)
    if n <= 1:
        if n == 1:
            return {_edge_key(G.S[0], G.T[0])}
        return set()

    E_star, casus, S_rem, T_rem = lemma17_find_cover(G)

    if casus == "trivial":
        return E_star
    if casus == "S_Tprime":
        G_sub = induced_subgraph(G, set(G.S), T_rem)
        S_sub, T_sub, E_dismount = dismountability(G_sub)
        G_em = induced_subgraph(G, S_sub, T_sub)
        E_rec = spanner_for_EM_biclique(G_em)
        return E_star | E_dismount | E_rec
    else:
        G_sub = induced_subgraph(G, S_rem, set(G.T))
        S_sub, T_sub, E_dismount = dismountability(G_sub)
        G_em = induced_subgraph(G, S_sub, T_sub)
        E_rec = spanner_for_EM_biclique(G_em)
        return E_star | E_dismount | E_rec


def spanner_for_biclique(G: TemporalBiClique) -> set[tuple[VertexID, VertexID]]:
    S_p, T_p, E_dismount = dismountability(G)
    G_em = induced_subgraph(G, S_p, T_p)
    E_em = spanner_for_EM_biclique(G_em)
    return E_dismount | E_em
