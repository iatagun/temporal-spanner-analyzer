from spanner.types import TemporalGraph, TemporalBiClique
from spanner.core import clique_to_biclique


def test_clique_to_biclique_basic():
    G = TemporalGraph({0, 1, 2}, {(0, 1): 0.5, (0, 2): 0.3, (1, 2): 0.7})
    bc, proj = clique_to_biclique(G)
    assert len(bc.S) == 3
    assert len(bc.T) == 3
    for v in range(3):
        assert f"{v}_S" in bc.S
        assert f"{v}_T" in bc.T
    assert bc.label[("0_S", "0_T")] == 0.0
    assert bc.label[("0_S", "1_T")] == 0.5
    assert bc.label[("1_S", "2_T")] == 0.7
    assert proj[("0_S", "1_T")] == ("0", "1")


def test_clique_to_biclique_projection():
    G = TemporalGraph({"a", "b"}, {("a", "b"): 1.0})
    bc, proj = clique_to_biclique(G)
    for (s, t), (u, v) in proj.items():
        s_src = s.replace("_S", "").replace("_T", "")
        t_src = t.replace("_S", "").replace("_T", "")
        assert {s_src, t_src} == {u, v}
        assert u != v
