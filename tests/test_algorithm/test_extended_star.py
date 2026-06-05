from spanner.types import TemporalBiClique
from spanner.core import extended_star_s_star, extended_star_t_star, _emin_edges, _emax_edges


def test_extended_star_contains_emin_emax():
    S = ["a", "b"]
    T = ["x", "y"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.3, ("b", "x"): 0.2, ("b", "y"): 0.4}
    G = TemporalBiClique(S, T, lbl)
    es = extended_star_s_star("a", G)
    et = extended_star_t_star("x", G)
    emin = _emin_edges(G)
    emax = _emax_edges(G)
    for e in emin:
        assert e in es
        assert e in et
    for e in emax:
        assert e in es
        assert e in et


def test_extended_star_bounded_size():
    S = ["a", "b", "c"]
    T = ["x", "y", "z"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.4, ("a", "z"): 0.7,
           ("b", "x"): 0.2, ("b", "y"): 0.5, ("b", "z"): 0.8,
           ("c", "x"): 0.3, ("c", "y"): 0.6, ("c", "z"): 0.9}
    G = TemporalBiClique(S, T, lbl)
    es = extended_star_s_star("a", G)
    et = extended_star_t_star("x", G)
    assert len(es) <= 4 * len(S)
    assert len(et) <= 4 * len(S)
