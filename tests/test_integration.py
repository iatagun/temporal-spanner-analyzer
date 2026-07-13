import pytest
from fastapi.testclient import TestClient
import sys; sys.path.insert(0, "backend")
from backend.main import app

client = TestClient(app)


def test_upload_csv_success():
    # NPMI + min_codf=2 (see graph_builder.compute_npmi) means a pair needs
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


def test_upload_association_measure_changes_gating_and_edges_carry_all_scores():
    # Regression/wiring test: with the same numeric threshold (5.0, well
    # above NPMI's [-1,1] ceiling but below log-likelihood's for a strong
    # pair), the active association_measure must actually decide which
    # edges survive -- not silently fall back to NPMI regardless of the
    # request. "kedi,kopek" is an isolated, perfectly-correlated pair
    # (log-likelihood ~7.6); "yapay" is diluted by appearing with two
    # different partners (log-likelihood ~2.1).
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"yapay,zeka\"\n"
        b"2020-02-01,\"yapay,zeka\"\n"
        b"2020-03-12,\"yapay,ogrenme\"\n"
        b"2020-04-01,\"yapay,ogrenme\"\n"
        b"2020-05-01,\"kedi,kopek\"\n"
        b"2020-06-01,\"kedi,kopek\"\n"
    )
    r_npmi = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "5.0", "association_measure": "npmi"},
    )
    r_ll = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "5.0", "association_measure": "log_likelihood"},
    )
    assert r_npmi.status_code == 200 and r_ll.status_code == 200
    assert r_npmi.json()["graph"]["edges"] == []  # every NPMI score is <= 1.0 < 5.0
    assert r_npmi.json()["association_measure"] == "npmi"

    ll_edges = r_ll.json()["graph"]["edges"]
    # One edge instance per document occurrence (2 "kedi,kopek" rows) --
    # same pair, same scores, different labels. Only the FIRST occurrence
    # carries `scores` (see graph_builder._words_to_edges_filtered) -- a
    # 27MB synthetic corpus with pairs repeating ~22x on average showed
    # this duplication alone bloating the upload response from ~80MB to
    # 200MB+, for data every consumer already dedups by pair anyway.
    assert len(ll_edges) == 2
    pairs = {(e["u"], e["v"]) if e["u"] <= e["v"] else (e["v"], e["u"]) for e in ll_edges}
    assert pairs == {("kedi", "kopek")}
    assert set(ll_edges[0]["scores"].keys()) == {
        "npmi", "log_likelihood", "dice", "t_score", "adjacency_ratio",
        "p_value", "p_value_fdr", "p_value_bonferroni",
    }
    assert ll_edges[0]["scores"]["log_likelihood"] > 5.0
    assert ll_edges[1]["scores"] == {}
    assert r_ll.json()["association_measure"] == "log_likelihood"


def test_upload_rejects_unknown_association_measure():
    csv_content = b"date,words\n2020-01-05,\"a,b\"\n2020-02-01,\"a,b\"\n"
    r = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"association_measure": "bogus"},
    )
    assert r.status_code == 422


def test_upload_lemmatize_collapses_inflected_forms_into_one_node():
    # "kitaplar" (books) and "kitap" (book) are two inflections of the
    # same lemma -- without lemmatization each is a separate vertex, and
    # ("kitaplar","masa")/("kitap","masa") each only co-occur once
    # (codf=1 < min_codf=2), so NEITHER clears the threshold -- no edge
    # at all. With lemmatize=True both rows collapse onto the same
    # ("kitap","masa") pair, codf=2, and the edge appears.
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"kitaplar,masa\"\n"
        b"2020-02-01,\"kitap,masa\"\n"
    )
    r_plain = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "-1.0"},
    )
    r_lemma = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "-1.0", "lemmatize": "true"},
    )
    assert r_plain.status_code == 200 and r_lemma.status_code == 200
    assert r_plain.json()["graph"]["edges"] == []
    assert {"kitaplar", "kitap", "masa"} <= set(r_plain.json()["graph"]["vertices"])

    lemma_vertices = set(r_lemma.json()["graph"]["vertices"])
    assert lemma_vertices == {"kitap", "masa"}
    lemma_pairs = {
        (e["u"], e["v"]) if e["u"] <= e["v"] else (e["v"], e["u"])
        for e in r_lemma.json()["graph"]["edges"]
    }
    assert ("kitap", "masa") in lemma_pairs

    # lemmatize=False must not report any coverage (no attempt was made).
    assert r_plain.json()["lemmatized_count"] == 0
    assert r_plain.json()["lemmatized_total"] == 0
    # lemmatize=True: both rows have 2 words each = 4 words attempted, all
    # real Turkish nouns Zeyrek can parse -- full coverage.
    assert r_lemma.json()["lemmatized_total"] == 4
    assert r_lemma.json()["lemmatized_count"] == 4


def test_upload_lemmatize_reports_partial_coverage_for_unanalyzable_words():
    # "xyzqwerty" is outside Zeyrek's TRmorph vocabulary -- lemmatized_count
    # must reflect that it WASN'T really analyzed (falls back to itself,
    # see lemmatizer.lemmatize_tr), making Zeyrek's coverage gaps visible
    # to the user instead of silently claiming full coverage.
    csv_content = b"date,words\n2020-01-05,\"kitaplar,xyzqwerty\"\n2020-02-01,\"kitap,xyzqwerty\"\n"
    r = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"pmi_threshold": "-1.0", "lemmatize": "true"},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["lemmatized_total"] == 4
    assert d["lemmatized_count"] == 2  # only "kitaplar"/"kitap", not "xyzqwerty" x2
    assert "xyzqwerty" in d["graph"]["vertices"]  # left as-is, still usable


def test_mwe_candidates_ranks_nested_terms_correctly():
    # Uses upload's raw_documents directly (like word-cliques does) to rank
    # multi-word-expression candidates by C-value -- see
    # graph_builder.extract_mwe_candidates for the hand-verified formula.
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"yapay,zeka,modeli\"\n"
        b"2020-02-01,\"yapay,zeka,modeli\"\n"
        b"2020-03-01,\"yapay,zeka,modeli\"\n"
        b"2020-04-01,\"yapay,zeka\"\n"
        b"2020-05-01,\"yapay,zeka\"\n"
    )
    r_upload = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert r_upload.status_code == 200
    raw_documents = r_upload.json()["raw_documents"]

    r = client.post("/api/mwe-candidates", json={"raw_documents": raw_documents, "max_n": 3, "min_freq": 2})
    assert r.status_code == 200
    candidates = r.json()["candidates"]
    texts = [c["text"] for c in candidates]
    assert "yapay zeka modeli" in texts
    # Ranked descending by C-value -- the un-diluted trigram wins.
    assert texts[0] == "yapay zeka modeli"


def test_mwe_candidates_requires_raw_documents():
    r = client.post("/api/mwe-candidates", json={"raw_documents": []})
    assert r.status_code == 400


def test_pair_confidence_uses_upload_raw_documents():
    # Uses upload's raw_documents directly (same "raw_documents, not
    # graph" pattern as mwe-candidates/word-cliques). A pair that
    # co-occurs in every document has zero resampling variance, so its
    # interval collapses to a single point -- a strong, easily-checked
    # end-to-end signal that the real endpoint (not just the unit-tested
    # function) is wired correctly.
    csv_content = b"date,words\n2020-01-05,\"yapay,zeka\"\n2020-02-01,\"yapay,zeka\"\n2020-03-01,\"yapay,zeka\"\n"
    r_upload = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert r_upload.status_code == 200
    raw_documents = r_upload.json()["raw_documents"]

    r = client.post("/api/pair-confidence", json={
        "raw_documents": raw_documents, "word1": "yapay", "word2": "zeka", "n_resamples": 100,
    })
    assert r.status_code == 200
    d = r.json()
    assert d["lower"] == pytest.approx(1.0)
    assert d["upper"] == pytest.approx(1.0)
    assert d["point_estimate"] == pytest.approx(1.0)


def test_pair_confidence_requires_raw_documents_and_words():
    r_no_docs = client.post("/api/pair-confidence", json={"raw_documents": [], "word1": "a", "word2": "b"})
    assert r_no_docs.status_code == 400

    r_no_word = client.post("/api/pair-confidence", json={
        "raw_documents": [{"label": 0.0, "words": ["a", "b"], "text": "a b"}],
        "word1": "", "word2": "b",
    })
    assert r_no_word.status_code == 400


def test_upload_conllu_syntactic_collocation_excludes_sibling_pairs():
    # "buyuk"/"iyi" are both amod children of "ev" (siblings, not directly
    # connected) -- collocation_mode=syntactic must exclude that pair,
    # while the default "window" mode includes it (see
    # test_collocation_mode_syntactic_excludes_sibling_pairs for the unit
    # version). Repeated twice so every pair clears min_codf=2.
    conllu_content = (
        "# date = 2020-01-01\n"
        "1\tbuyuk\tbuyuk\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "2\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "3\tiyi\tiyi\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "\n"
        "# date = 2020-02-01\n"
        "1\tbuyuk\tbuyuk\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "2\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "3\tiyi\tiyi\tADJ\t_\t_\t2\tamod\t_\t_\n"
    ).encode()
    r = client.post(
        "/api/upload",
        files={"file": ("test.conllu", conllu_content, "text/plain")},
        data={"pmi_threshold": "-1.0", "collocation_mode": "syntactic"},
    )
    assert r.status_code == 200
    pairs = {(e["u"], e["v"]) if e["u"] <= e["v"] else (e["v"], e["u"]) for e in r.json()["graph"]["edges"]}
    assert pairs == {("buyuk", "ev"), ("ev", "iyi")}


def test_upload_sample_conllu_supports_syntactic_collocation():
    # Regression test: the shipped demo file used to have no HEAD/DEPREL
    # at all (4-column CoNLL-U), so a first-time user trying "Sözdizimsel"
    # on "Örnek Veri ile Dene" would just hit a 400. It was hand-annotated
    # with compound-noun-phrase dependencies (see the file's own header
    # comment) -- must now work and produce recognizable pairs like
    # "yapay"-"zeka", which repeats across many dates in the file.
    import os
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "frontend", "public", "sample.conllu"
    )
    with open(sample_path, "rb") as f:
        sample_content = f.read()
    r = client.post(
        "/api/upload",
        files={"file": ("sample.conllu", sample_content, "text/plain")},
        data={"collocation_mode": "syntactic"},
    )
    assert r.status_code == 200
    pairs = {(e["u"], e["v"]) if e["u"] <= e["v"] else (e["v"], e["u"]) for e in r.json()["graph"]["edges"]}
    assert ("yapay", "zeka") in pairs


def test_upload_rejects_syntactic_collocation_for_non_conllu():
    # Only CoNLL-U carries HEAD/DEPREL -- VRT/CSV/JSON must be rejected
    # upfront rather than silently falling back to window mode.
    csv_content = b"date,words\n2020-01-05,\"yapay,zeka\"\n2020-02-01,\"yapay,zeka\"\n"
    r = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"collocation_mode": "syntactic"},
    )
    assert r.status_code == 400


def test_upload_tei_word_level_success():
    xml_content = (
        b'<?xml version="1.0"?>\n'
        b'<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
        b'<teiHeader><date when="2020-01-15"/></teiHeader>\n'
        b'<text><body><div>\n'
        b'<s><w lemma="yapay" pos="ADJ">yapay</w><w lemma="zeka" pos="NOUN">zeka</w></s>\n'
        b'<s><w lemma="yapay" pos="ADJ">yapay</w><w lemma="zeka" pos="NOUN">zeka</w></s>\n'
        b'</div></body></text>\n'
        b'</TEI>\n'
    )
    r = client.post("/api/upload", files={"file": ("test.xml", xml_content, "application/xml")})
    assert r.status_code == 200
    d = r.json()
    assert "yapay" in d["graph"]["vertices"]
    assert "zeka" in d["graph"]["vertices"]


def test_upload_tei_plain_text_fallback_success():
    xml_content = (
        b'<TEI><teiHeader><date when="2021-06-01"/></teiHeader>\n'
        b'<text><body>\n'
        b'<p>yapay zeka konusu burada anlatiliyor bugun</p>\n'
        b'<p>yapay zeka tekrar burada gecen konu bugun</p>\n'
        b'</body></text></TEI>\n'
    )
    r = client.post("/api/upload", files={"file": ("test.xml", xml_content, "application/xml")})
    assert r.status_code == 200
    d = r.json()
    assert "yapay" in d["graph"]["vertices"]


def test_upload_rejects_malformed_xml_with_400_not_500():
    r = client.post(
        "/api/upload",
        files={"file": ("bad.xml", b"<TEI><unclosed>", "application/xml")},
    )
    assert r.status_code == 400


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


def test_trends_windows_zero_is_422_not_crash():
    # Regression test: windows=0 used to reach compute_trends and raise an
    # unhandled ZeroDivisionError (step = range / windows) -> bare 500.
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/trends", json={"graph": g, "windows": 0})
    assert r.status_code == 422


def test_trends_windows_out_of_bounds_is_422():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/trends", json={"graph": g, "windows": 100_000})
    assert r.status_code == 422


def test_word_cliques_windows_zero_is_422():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/word-cliques", json={"graph": g, "word": "a", "windows": 0})
    assert r.status_code == 422


def test_spanner_min_clique_size_out_of_bounds_is_422():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/spanner", json={"graph": g, "min_clique_size": 1})
    assert r.status_code == 422


def test_spanner_max_cliques_out_of_bounds_is_422():
    g = {"vertices": ["a", "b"], "edges": [{"u": "a", "v": "b", "label": 1.0}]}
    r = client.post("/api/spanner", json={"graph": g, "max_cliques": -1})
    assert r.status_code == 422


def test_upload_response_has_no_dead_session_id_field():
    csv_content = b"date,words\n2020-01-05,\"a,b\"\n2020-02-01,\"a,b\"\n"
    r = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert "session_id" not in r.json()


def test_upload_returns_raw_documents_for_windowed_trends():
    # /api/trends recomputes NPMI per time window from these raw
    # (label, words) rows instead of only slicing the corpus-global edge
    # set -- see trend_analyzer.compute_trends. The backend stays
    # stateless: the client re-sends what upload returned here, there is
    # no server-side session (see test_upload_response_has_no_dead_session_id_field).
    # A triangle (3 mutually co-occurring words) so it survives the
    # single-snapshot noise filter (see trend_analyzer.compute_trends)
    # even though both rows land in the same (windows=1) window.
    csv_content = (
        b"date,words\n"
        b"2020-01-05,\"kedi,kopek,kus\"\n"
        b"2020-02-01,\"kedi,kopek,kus\"\n"
    )
    r = client.post("/api/upload", files={"file": ("test.csv", csv_content, "text/csv")})
    assert r.status_code == 200
    d = r.json()
    assert len(d["raw_documents"]) == 2
    assert {tuple(sorted(doc["words"])) for doc in d["raw_documents"]} == {("kedi", "kopek", "kus")}

    r2 = client.post("/api/trends", json={
        "graph": d["graph"],
        "windows": 1,
        "raw_documents": d["raw_documents"],
        "pmi_threshold": d["pmi_threshold"],
    })
    assert r2.status_code == 200
    tr = r2.json()
    member_sets = {tuple(sorted(m for s in tl["snapshots"] for m in s["members"])) for tl in tr["timelines"]}
    assert ("kedi", "kopek", "kus") in member_sets


def test_spanner_empty_graph():
    g = {"vertices": ["a"], "edges": []}
    r = client.post("/api/spanner", json={"graph": g})
    assert r.status_code == 200
    d = r.json()
    assert d["metrics"]["spanner_edges"] == 0
    assert "pmi_threshold" not in d["metrics"]


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
