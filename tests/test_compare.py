from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app

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
