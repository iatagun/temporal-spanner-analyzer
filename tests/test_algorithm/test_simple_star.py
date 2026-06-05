from spanner.types import TemporalBiClique
from spanner.core import simple_star, s_star_ordering, Nmin


def test_simple_star_size():
    S = ["a", "b", "c"]
    T = ["x", "y", "z"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.4, ("a", "z"): 0.7,
           ("b", "x"): 0.2, ("b", "y"): 0.5, ("b", "z"): 0.8,
           ("c", "x"): 0.3, ("c", "y"): 0.6, ("c", "z"): 0.9}
    G = TemporalBiClique(S, T, lbl)
    edges = simple_star("a", G)
    assert len(edges) == 2 * len(S) - 1  # |S| = n


def test_s_star_ordering():
    S = ["a", "b"]
    T = ["x", "y"]
    lbl = {("a", "x"): 0.2, ("a", "y"): 0.1, ("b", "x"): 0.3, ("b", "y"): 0.4}
    G = TemporalBiClique(S, T, lbl)
    S_ord, T_ord = s_star_ordering("a", G)
    assert T_ord[0] == "y"  # p_{s*}(y) = 0 < p_{s*}(x) = 1
    assert S_ord[0] == "a"  # s0 = Nmin(t0) = Nmin(y) = a
