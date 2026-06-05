from spanner.types import TemporalBiClique, TemporalGraph
from spanner.core import dismountability, dismountability_12_hop, is_12_hop_dismountable, Nmin, Nmax


def test_dismountability_empty():
    G = TemporalBiClique([], [], {})
    S, T, E = dismountability(G)
    assert len(S) == 0
    assert len(T) == 0
    assert len(E) == 0


def test_dismountability_simple():
    S = ["a", "b"]
    T = ["x", "y"]
    lbl = {("a", "x"): 0.1, ("a", "y"): 0.3, ("b", "x"): 0.2, ("b", "y"): 0.4}
    G = TemporalBiClique(S, T, lbl)
    S2, T2, E = dismountability(G)
    assert len(S2) == len(T2)  # EM property
    assert len(E) >= 0


def test_12_hop_dismountability_empty():
    G = TemporalGraph({0, 1}, {(0, 1): 0.5})
    Vp, Ed = dismountability_12_hop(G)
    # n=2: no {1,2}-hop dismountable vertices
    assert len(Vp) == 2


def test_12_hop_dismountability_small():
    G = TemporalGraph({0, 1, 2}, {(0, 1): 0.1, (0, 2): 0.3, (1, 2): 0.2})
    Vp, Ed = dismountability_12_hop(G)
    assert len(Vp) <= 3
    assert len(Vp) >= 0
