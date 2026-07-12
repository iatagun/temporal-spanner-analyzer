from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app

client = TestClient(app)


def test_upload_csv_success():
    # NPMI + min_codf=2 (see graph_builder._compute_pmi) means a pair needs
    # to co-occur more than once, and not in literally every row, to score
    # as an edge -- "kedi,kopek" is included as a second, unrelated pair so
    # "yapay" isn't in 100% of rows (which would make it uninformative and
    # zero out its own pairs' NPMI).
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"yapay,zeka\"\n"
        b"2020-02-01,\"yapay,zeka\"\n"
        b"2020-03-12,\"yapay,ogrenme\"\n"
        b"2020-04-01,\"yapay,ogrenme\"\n"
        b"2020-05-01,\"kedi,kopek\"\n"
        b"2020-06-01,\"kedi,kopek\"\n"
    )
    r = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert r.status_code == 200
    d = r.json()
    assert d["rows_parsed"] == 6
    assert set(d["graph"]["vertices"]) == {"yapay", "zeka", "ogrenme", "kedi", "kopek"}
    edge_pairs = {(e["u"], e["v"]) if e["u"] <= e["v"] else (e["v"], e["u"]) for e in d["graph"]["edges"]}
    assert edge_pairs == {("yapay", "zeka"), ("ogrenme", "yapay"), ("kedi", "kopek")}


def test_upload_pmi_threshold_form_field_is_applied():
    # Regression test: SpannerRequest.pmi_threshold used to be accepted by
    # the schema but never read by any endpoint, while /api/upload always
    # used a hardcoded module constant regardless of what was sent. The
    # threshold must now actually change which edges survive.
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"yapay,zeka\"\n"
        b"2020-02-01,\"yapay,zeka\"\n"
        b"2020-03-12,\"yapay,ogrenme\"\n"
        b"2020-04-01,\"yapay,ogrenme\"\n"
        b"2020-05-01,\"kedi,kopek\"\n"
        b"2020-06-01,\"kedi,kopek\"\n"
    )
    r_loose = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "-1.0"},
    )
    r_strict = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "0.99"},
    )
    assert r_loose.status_code == 200 and r_strict.status_code == 200
    loose_edges = len(r_loose.json()["graph"]["edges"])
    strict_edges = len(r_strict.json()["graph"]["edges"])
    assert loose_edges > strict_edges
    assert r_strict.json()["pmi_threshold"] == 0.99


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


def test_upload_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr("backend.routers.spanner.MAX_UPLOAD_BYTES", 10)
    r = client.post("/api/upload", files={"file": ("test.csv", b"date,words\n" + b"a" * 100, "text/csv")})
    assert r.status_code == 413


def test_upload_oversized_csv_field_is_400_not_500():
    # A single CSV field wider than Python's csv module default limit
    # (131072 bytes) used to raise an uncaught csv.Error -> 500.
    huge_field = b"date,words\n2020-01-01," + b"a " * 100_000
    r = client.post("/api/upload", files={"file": ("huge.csv", huge_field, "text/csv")})
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


def test_export_graphml_escapes_special_chars():
    g = {"vertices": ["a&b", 'c<d>"e'], "edges": [{"u": "a&b", "v": 'c<d>"e', "label": 1.0}]}
    r = client.post("/api/export?fmt=graphml", json={"graph": g})
    assert r.status_code == 200
    assert "a&amp;b" in r.text
    assert "c&lt;d&gt;&quot;e" in r.text
    assert "<d>" not in r.text


def test_export_csv_quotes_commas():
    g = {"vertices": ["x,y", "z"], "edges": [{"u": "x,y", "v": "z", "label": 1.0}]}
    r = client.post("/api/export?fmt=csv", json={"graph": g})
    assert r.status_code == 200
    assert '"x,y"' in r.text


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
