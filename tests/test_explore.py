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
    assert d["total_pairs"] == 1
    assert len(d["missing_pairs"]) == 0


def test_check_clique_false():
    g = {
        "vertices": ["a", "b", "c"],
        "edges": [{"u": "a", "v": "b", "label": 1}],
    }
    r = client.post("/api/check-clique", json={"graph": g, "words": ["a", "c"]})
    assert r.status_code == 200
    d = r.json()
    assert d["is_clique"] is False
    assert len(d["missing_pairs"]) == 1
    assert d["missing_pairs"][0] == ["a", "c"]


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
    assert "snapshots" in d
