from spanner.core import (
    spanner_for_clique, spanner_for_biclique, spanner_for_EM_biclique,
    clique_to_biclique, dismountability, random_temporal_clique,
    exists_temporal_path_in_subgraph,
)
from spanner.types import TemporalGraph, TemporalBiClique
from spanner.verify import verify_spanner


def test_spanner_for_clique_small():
    G = random_temporal_clique(4, seed=0)
    E = spanner_for_clique(G)
    assert verify_spanner(G, E, 7 * 4)
    assert len(E) <= 7 * 4


def test_spanner_for_clique_medium():
    G = random_temporal_clique(10, seed=42)
    E = spanner_for_clique(G)
    assert verify_spanner(G, E, 7 * 10)
    assert len(E) <= 7 * 10


def test_spanner_for_clique_all_pairs():
    n = 6
    G = random_temporal_clique(n, seed=7)
    E = spanner_for_clique(G)
    for u in G.V:
        for v in G.V:
            if u == v:
                continue
            assert exists_temporal_path_in_subgraph(u, v, E, G), \
                f"No temporal path between {u} and {v}"


def test_spanner_for_biclique_small():
    S = [0, 1]
    T = [2, 3]
    lbl = {(0, 2): 0.1, (0, 3): 0.4, (1, 2): 0.2, (1, 3): 0.3}
    G = TemporalBiClique(S, T, lbl)
    E = spanner_for_biclique(G)
    for s in S:
        for t in T:
            assert exists_temporal_path_in_subgraph(s, t, E, G)


def test_spanner_for_EM_biclique_small():
    S = [0, 1]
    T = [2, 3]
    lbl = {(0, 2): 0.1, (0, 3): 0.4, (1, 2): 0.2, (1, 3): 0.3}
    G = TemporalBiClique(S, T, lbl)
    S2, T2, _ = dismountability(G)
    S2_list = sorted(S2)
    T2_list = sorted(T2)
    G_em = TemporalBiClique(S2_list, T2_list, {})
    for s in S2_list:
        for t in T2_list:
            k = (s, t) if s <= t else (t, s)
            G_em.label[k] = lbl.get(k, 0.5)
    if len(S2_list) > 0:
        E = spanner_for_EM_biclique(G_em)
        assert len(E) <= 14 * len(S2_list) or len(E) == 0


def test_multiple_seeds():
    for n in [4, 6, 8]:
        for seed in [0, 1, 2]:
            G = random_temporal_clique(n, seed=seed)
            E = spanner_for_clique(G)
            assert verify_spanner(G, E, 7 * n), f"Failed n={n} seed={seed}"
