from spanner.types import TemporalBiClique
from spanner.core import is_3_hop_k_cut_crossing, s_star_ordering


def test_no_crossing_for_k_at_n():
    S = ["a", "b"]
    T = ["x", "y"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.3, ("b", "x"): 0.2, ("b", "y"): 0.4}
    G = TemporalBiClique(S, T, lbl)
    S_ord, T_ord = s_star_ordering("a", G)
    # i=1 > k=0, check crossing
    result = is_3_hop_k_cut_crossing("b", 1, 0, "y", "a", T_ord, G)
    assert isinstance(result, bool)


def test_crossing_false_when_i_leq_k():
    S = ["a", "b", "c"]
    T = ["x", "y", "z"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.4, ("a", "z"): 0.7,
           ("b", "x"): 0.2, ("b", "y"): 0.5, ("b", "z"): 0.8,
           ("c", "x"): 0.3, ("c", "y"): 0.6, ("c", "z"): 0.9}
    G = TemporalBiClique(S, T, lbl)
    S_ord, T_ord = s_star_ordering("a", G)
    assert not is_3_hop_k_cut_crossing("a", 0, 1, "x", "a", T_ord, G)
