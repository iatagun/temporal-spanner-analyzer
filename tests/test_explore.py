from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app

client = TestClient(app)


def test_check_clique_true():
    g = {
        "vertices": ["a", "b", "c"],
        "edges": [
            {"u": "a", "v": "b", "label": 1},
            {"u": "a", "v": "c", "label": 2},
            {"u": "b", "v": "c", "label": 3},
        ],
    }
    r = client.post("/api/check-clique", json={"graph": g, "words": ["a", "b"]})
    assert r.status_code == 200
    d = r.json()
    assert d["is_clique"] is True
    assert d["expected_edges"] == 1
    assert d["missing_edges"] is None


def test_check_clique_false():
    g = {
        "vertices": ["a", "b", "c"],
        "edges": [{"u": "a", "v": "b", "label": 1}],
    }
    r = client.post("/api/check-clique", json={"graph": g, "words": ["a", "c"]})
    assert r.status_code == 200
    d = r.json()
    assert d["is_clique"] is False
    assert len(d["missing_edges"]) == 1
    assert d["missing_edges"][0] == ["a", "c"]


def test_word_cliques():
    g = {
        "vertices": ["a", "b", "c"],
        "edges": [
            {"u": "a", "v": "b", "label": 1},
            {"u": "a", "v": "c", "label": 2},
            {"u": "b", "v": "c", "label": 3},
        ],
    }
    r = client.post("/api/word-cliques", json={"graph": g, "word": "a", "windows": 2})
    assert r.status_code == 200
    d = r.json()
    assert d["word"] == "a"
    assert "cliques" in d
    assert d["total_snapshots"] > 0
