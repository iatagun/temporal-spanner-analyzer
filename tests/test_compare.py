from unittest.mock import patch

from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app
from backend.services import graph_utils

client = TestClient(app)


def test_compare_two_graphs():
    g1 = {
        "vertices": ["a", "b", "c"],
        "edges": [
            {"u": "a", "v": "b", "label": 1},
            {"u": "a", "v": "c", "label": 2},
            {"u": "b", "v": "c", "label": 3},
        ],
    }
    g2 = {
        "vertices": ["b", "c", "d"],
        "edges": [
            {"u": "b", "v": "c", "label": 1},
            {"u": "b", "v": "d", "label": 2},
            {"u": "c", "v": "d", "label": 3},
        ],
    }

    r = client.post("/api/compare", json={"graph1": g1, "graph2": g2})
    assert r.status_code == 200
    d = r.json()
    assert "spanner1" in d
    assert "spanner2" in d
    assert "comparison" in d
    assert d["comparison"]["vertex_overlap_pct"] == 50.0
    assert d["comparison"]["vertex_intersection"] == 2


def test_compare_identical_graphs():
    g = {
        "vertices": ["x", "y"],
        "edges": [{"u": "x", "v": "y", "label": 0.5}],
    }
    r = client.post("/api/compare", json={"graph1": g, "graph2": g})
    assert r.status_code == 200
    d = r.json()
    assert d["comparison"]["vertex_overlap_pct"] == 100.0
    assert d["comparison"]["edge_overlap_pct"] == 100.0
    assert d["comparison"]["savings_compare"] == "Equal"


def test_compare_stretch_factor_matches_spanner_endpoint():
    # Regression test: compare.py used to hand-roll its own SpannerResponse
    # assembly, and its n<2 branch silently omitted stretch_factor (always
    # None) while /api/spanner's equivalent branch returned 1.0 -- the two
    # endpoints disagreed on the same conceptual case. Both now share
    # spanner_service.build_spanner_response.
    g = {"vertices": ["a"], "edges": []}
    r_spanner = client.post("/api/spanner", json={"graph": g})
    r_compare = client.post("/api/compare", json={"graph1": g, "graph2": g})
    assert r_spanner.json()["metrics"]["stretch_factor"] == 1.0
    assert r_compare.json()["spanner1"]["metrics"]["stretch_factor"] == 1.0
    assert r_compare.json()["spanner2"]["metrics"]["stretch_factor"] == 1.0


def test_compare_enumerates_cliques_once_per_graph():
    # Bron-Kerbosch is the expensive step in /api/compare; it used to run
    # twice per graph (once for the spanner at min_size=3, once for the
    # Jaccard/clique-count comparison at min_size=2). Regression test: it
    # must run exactly once per graph now.
    g1 = {
        "vertices": ["a", "b", "c"],
        "edges": [
            {"u": "a", "v": "b", "label": 1},
            {"u": "a", "v": "c", "label": 2},
            {"u": "b", "v": "c", "label": 3},
        ],
    }
    g2 = {
        "vertices": ["b", "c", "d"],
        "edges": [
            {"u": "b", "v": "c", "label": 1},
            {"u": "b", "v": "d", "label": 2},
            {"u": "c", "v": "d", "label": 3},
        ],
    }

    with patch(
        "backend.services.spanner_service.maximal_cliques",
        wraps=graph_utils.maximal_cliques,
    ) as spy:
        r = client.post("/api/compare", json={"graph1": g1, "graph2": g2})
        assert r.status_code == 200
        assert spy.call_count == 2
