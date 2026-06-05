from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app

client = TestClient(app)


def test_upload_csv_success():
    csv_content = b"date,words\n2020-01-05,\"yapay,zeka\"\n2020-03-12,\"yapay,ogrenme\"\n"
    r = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert r.status_code == 200
    d = r.json()
    assert d["rows_parsed"] == 2
    assert len(d["graph"]["vertices"]) == 3
    assert len(d["graph"]["edges"]) == 2


def test_upload_json_success():
    json_content = b'[{"date": "2020-01-05", "words": ["yapay", "zeka"]}, {"date": "2020-03-12", "words": ["yapay", "ogrenme"]}]'
    r = client.post("/api/upload", files={"file": ("test.json", json_content, "application/json")})
    assert r.status_code == 200
    d = r.json()
    assert d["rows_parsed"] == 2
    assert len(d["graph"]["vertices"]) == 3


def test_upload_json_wrapper():
    json_content = b'{"documents": [{"date": "2020-01-05", "words": ["elma", "armut"]}, {"date": "2020-06-01", "words": ["armut", "muz"]}]}'
    r = client.post("/api/upload", files={"file": ("data.json", json_content, "application/json")})
    assert r.status_code == 200
    d = r.json()
    assert d["rows_parsed"] == 2
    assert "armut" in d["graph"]["vertices"]


def test_upload_invalid_extension():
    r = client.post("/api/upload", files={"file": ("data.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_upload_empty_csv():
    r = client.post("/api/upload", files={"file": ("empty.csv", b"date,words", "text/csv")})
    assert r.status_code == 400


def test_spanner_empty_graph():
    g = {"vertices": ["a"], "edges": []}
    r = client.post("/api/spanner", json={"graph": g})
    assert r.status_code == 200
    d = r.json()
    assert d["metrics"]["spanner_edges"] == 0


def test_export_json():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/export?fmt=json", json={"graph": g})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"


def test_export_csv():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/export?fmt=csv", json={"graph": g})
    assert r.status_code == 200
    assert "source,target,label" in r.text


def test_export_graphml():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/export?fmt=graphml", json={"graph": g})
    assert r.status_code == 200
    assert "<graphml" in r.text


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
