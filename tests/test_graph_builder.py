import pytest

from backend.services.graph_builder import (
    parse_label,
    parse_corpus_rows,
    parse_json,
    compute_npmi,
    compute_association_measures,
    extract_mwe_candidates,
    bootstrap_confidence_interval,
    _is_content_word,
)


def test_parse_label_valid_dates():
    assert parse_label("2020-01-05") is not None
    assert parse_label("2020") is not None
    assert parse_label(1234.5) == 1234.5


def test_parse_label_returns_none_for_garbage():
    assert parse_label("not-a-date") is None
    assert parse_label("") is None


def test_parse_label_epoch_date_does_not_crash():
    # datetime.strptime(...).timestamp() interpreted the date in the
    # server's local timezone; on Windows with a positive UTC offset,
    # 1970-01-01 rendered as a negative local-time epoch and raised
    # OSError. Parsing must be UTC-anchored so this never happens
    # regardless of where the process runs.
    assert parse_label("1970-01-01") == 0.0


def test_corpus_rows_without_date_metadata_does_not_crash():
    # Regression test: corpus rows lacking any date metadata used to
    # route through parse_label("1970-01-01") as a fallback, which could
    # crash (see test_parse_label_epoch_date_does_not_crash). Also checks
    # that rows without dates aren't mistaken for parse failures and
    # don't trip the >50%-unparsed validation. No POS tags here (empty
    # string) so this also exercises the stopword-fallback path of
    # _is_content_word.
    rows = [
        ("", [("elma", ""), ("armut", "")], "elma armut", []),
        ("", [("armut", ""), ("muz", "")], "armut muz", []),
        ("", [("elma", ""), ("muz", "")], "elma muz", []),
    ]
    graph, dates, rows_parsed, _, _ = parse_corpus_rows(rows)
    assert rows_parsed == 3
    assert set(graph.vertices) == {"elma", "armut", "muz"}


def test_corpus_rows_flags_mostly_unparseable_dates():
    rows = [
        ("garbled-date-1", [("aa", "NOUN"), ("bb", "NOUN")], "aa bb", []),
        ("garbled-date-2", [("bb", "NOUN"), ("cc", "NOUN")], "bb cc", []),
    ]
    try:
        parse_corpus_rows(rows)
        assert False, "expected ValueError for mostly-unparseable dates"
    except ValueError:
        pass


def test_corpus_rows_pos_filter_drops_function_words():
    # Regression test for the POS-based content-word filter: a corpus row
    # with a real POS tag should drop function words (CCONJ/ADP/PRON/...)
    # and keep content words (NOUN/VERB/ADJ/PROPN), even though they're not
    # in the (Turkish-only, CSV/JSON-only) stopword list.
    rows = [
        ("2020-01-01", [("elma", "NOUN"), ("ve", "CCONJ"), ("armut", "NOUN")], "elma ve armut", []),
        ("2020-02-01", [("elma", "NOUN"), ("ve", "CCONJ"), ("armut", "NOUN")], "elma ve armut", []),
    ]
    graph, _, rows_parsed, stopword_count, _ = parse_corpus_rows(rows)
    assert rows_parsed == 2
    assert "ve" not in graph.vertices
    assert set(graph.vertices) == {"elma", "armut"}
    assert stopword_count == 2  # "ve" dropped from both rows


def _syntactic_test_rows():
    # "buyuk ev" and "iyi ev" are direct amod->NOUN dependencies; "buyuk"
    # and "iyi" are siblings (both children of "ev") -- connected only via
    # the same-sentence window, never by a direct HEAD edge. Repeated
    # twice (different dates) so every pair clears the default min_codf=2.
    from backend.services.corpus_parser import parse_conllu
    content = (
        "# date = 2020-01-01\n"
        "1\tbuyuk\tbuyuk\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "2\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "3\tiyi\tiyi\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "\n"
        "# date = 2020-02-01\n"
        "1\tbuyuk\tbuyuk\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "2\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "3\tiyi\tiyi\tADJ\t_\t_\t2\tamod\t_\t_\n"
    )
    return parse_conllu(content, filename="test.conllu")


def test_collocation_mode_window_includes_sibling_pairs():
    rows = _syntactic_test_rows()
    graph, *_ = parse_corpus_rows(rows, pmi_threshold=-1.0, collocation_mode="window")
    pairs = {(e.u, e.v) if e.u <= e.v else (e.v, e.u) for e in graph.edges}
    assert ("buyuk", "iyi") in pairs  # siblings under "ev" -- only a window pair


def test_collocation_mode_syntactic_excludes_sibling_pairs():
    rows = _syntactic_test_rows()
    graph, *_ = parse_corpus_rows(rows, pmi_threshold=-1.0, collocation_mode="syntactic")
    pairs = {(e.u, e.v) if e.u <= e.v else (e.v, e.u) for e in graph.edges}
    assert pairs == {("buyuk", "ev"), ("ev", "iyi")}
    assert ("buyuk", "iyi") not in pairs  # never a direct HEAD relation


def test_collocation_mode_syntactic_requires_dependency_info():
    # A corpus with no HEAD/DEPREL at all (e.g. routed from VRT, which
    # always returns empty deps) can't do syntactic collocation.
    rows = [("2020-01-01", [("elma", "NOUN"), ("armut", "NOUN")], "elma armut", [])]
    try:
        parse_corpus_rows(rows, collocation_mode="syntactic")
        assert False, "expected ValueError for a corpus with no dependency info"
    except ValueError:
        pass


def test_collocation_mode_syntactic_rejects_4column_conllu_with_blank_heads():
    # Regression test: a 4-column CoNLL-U (word/lemma/pos only, no HEAD --
    # e.g. this project's own shipped sample.conllu) still gives every
    # token a `deps` entry (just with a blank head_id), so a naive
    # "is deps non-empty" check would miss this and silently produce an
    # empty graph instead of a clear error.
    rows = [("2020-01-01", [("elma", "NOUN"), ("armut", "NOUN")], "elma armut", [("1", "", ""), ("2", "", "")])]
    try:
        parse_corpus_rows(rows, collocation_mode="syntactic")
        assert False, "expected ValueError for a corpus with blank head_id everywhere"
    except ValueError:
        pass


def test_collocation_mode_rejects_unknown_value():
    rows = _syntactic_test_rows()
    try:
        parse_corpus_rows(rows, collocation_mode="bogus")
        assert False, "expected ValueError for an unknown collocation mode"
    except ValueError:
        pass


def test_is_content_word_pos_vs_fallback():
    assert _is_content_word("elma", "NOUN") is True
    assert _is_content_word("ve", "CCONJ") is False
    assert _is_content_word("ve", "") is False  # falls back to stopword list
    assert _is_content_word("armut", "") is True


def test_parse_json_preserves_explicit_zero_date():
    # Regression test: `doc.get("date") or doc.get("tarih") or ...` treated
    # an explicit date=0 (epoch) as falsy and silently substituted a
    # different field's value instead.
    import json as json_mod
    content = json_mod.dumps([
        {"date": 0, "tarih": "2022-06-01", "words": ["elma", "armut"]},
        {"date": 0, "tarih": "2022-06-01", "words": ["elma", "armut"]},
    ]).encode()
    graph, dates, rows_parsed, _, _, _, _ = parse_json(content)
    assert rows_parsed == 2
    assert dates == ["0.0", "0.0"]


def test_parse_json_flags_corpus_with_no_date_fields_at_all():
    # Regression test: a JSON corpus where every document has no date/
    # tarih/timestamp/zaman field used to silently default to epoch (via
    # doc.get("zaman", 0) -> parse_label(0) -> 0.0, which is not None) and
    # never trip the same >50%-unparsed validation CSV enforces for the
    # equivalent "no real date info" case.
    import json as json_mod
    content = json_mod.dumps([
        {"words": ["elma", "armut"]},
        {"words": ["elma", "armut"]},
    ]).encode()
    try:
        parse_json(content)
        assert False, "expected ValueError for a corpus with no date info at all"
    except ValueError:
        pass


def test_compute_pmi_is_normalized_and_penalizes_hapax():
    # NPMI must stay within [-1, 1] and a pair seen only once (below
    # min_codf) must not appear at all -- this is the fix for raw PMI's
    # bias toward rare pairs.
    rows = [
        ["a", "b"], ["a", "b"], ["c", "d"], ["c", "d"],
        ["a", "b"], ["c", "d"], ["e", "f"],
    ]
    pmi = compute_npmi(rows)
    assert ("e", "f") not in pmi  # codf=1 < default min_codf=2
    for score in pmi.values():
        assert -1.0 <= score <= 1.0


def test_compute_association_measures_matches_hand_computed_values():
    # "x" appears in 5 of 6 docs, "y" in 2, both co-occur in 2 -- an
    # asymmetric case where NPMI/Dice/t-score/log-likelihood genuinely
    # differ (unlike the perfectly-correlated a-b/c-d pairs in the NPMI
    # test above, where every measure degenerates to its max). Values
    # below are hand-derived from the standard formulas (Dunning 1993 for
    # log-likelihood) and cross-checked against the implementation.
    rows = [["x", "y"], ["x", "y"], ["x"], ["x"], ["x"], ["z", "w"]]
    scores, truncated = compute_association_measures(rows)
    pair_scores = scores["x", "y"]
    assert truncated is False
    assert pair_scores["npmi"] == pytest.approx(0.16596, abs=1e-4)
    assert pair_scores["dice"] == pytest.approx(4 / 7, abs=1e-6)
    assert pair_scores["t_score"] == pytest.approx(0.23570, abs=1e-4)
    assert pair_scores["log_likelihood"] == pytest.approx(0.90805, abs=1e-4)
    # p_value: G^2's chi-square (df=1) survival function has a closed form,
    # erfc(sqrt(G^2/2)) -- 0.90805 -> 0.34063 (cross-checked against
    # math.erfc directly, not just re-deriving the same formula here).
    assert pair_scores["p_value"] == pytest.approx(0.34063, abs=1e-4)


def test_compute_association_measures_respects_min_codf_for_every_measure():
    # A pair below min_codf must be absent from the result entirely --
    # not just gated out of one measure -- since all four measures are
    # computed from the same codf/df pass.
    rows = [["a", "b"], ["a", "b"], ["c", "d"], ["c", "d"], ["a", "b"], ["c", "d"], ["e", "f"]]
    scores, _truncated = compute_association_measures(rows)
    assert ("e", "f") not in scores
    assert set(scores[("a", "b")].keys()) == {
        "npmi", "log_likelihood", "dice", "t_score", "adjacency_ratio",
        "p_value", "p_value_fdr", "p_value_bonferroni",
    }


def test_compute_association_measures_adjacency_ratio_detects_mwe_candidates():
    # "yapay" and "zeka" are ALWAYS immediate neighbors (a multi-word-
    # expression candidate like "yapay zeka") -- adjacency_ratio should be
    # 1.0. "zeka" and "veri" co-occur equally often but are never
    # adjacent (always separated by other words) -- adjacency_ratio
    # should be 0.0, even though both pairs have the same codf.
    rows = [
        ["yapay", "zeka", "buyuk", "veri"],
        ["yapay", "zeka", "kucuk", "veri"],
    ]
    scores, _truncated = compute_association_measures(rows, min_codf=2)
    assert scores[("yapay", "zeka")]["adjacency_ratio"] == pytest.approx(1.0)
    assert scores[("veri", "zeka")]["adjacency_ratio"] == pytest.approx(0.0)


def test_compute_association_measures_fdr_never_more_conservative_than_bonferroni():
    # Benjamini-Hochberg FDR is, by construction, always <= Bonferroni for
    # the same pair (less conservative) -- and both must be monotonic when
    # pairs are sorted by their raw p-value ascending (BH's defining
    # property: q(i) <= q(i+1)). A corpus with several pairs of varying
    # strength (strong/weak/noisy) gives enough spread in p-values to
    # meaningfully exercise both properties, not just a single pair.
    rows = [
        ["a", "b"], ["a", "b"], ["a", "b"], ["a", "b"],
        ["c", "d"], ["c", "d"],
        ["e", "f"], ["f", "g"], ["e", "g"], ["e", "f"], ["f", "g"],
    ]
    scores, _truncated = compute_association_measures(rows, min_codf=2)
    assert len(scores) >= 2

    for pair_scores in scores.values():
        assert pair_scores["p_value_fdr"] <= pair_scores["p_value_bonferroni"] + 1e-9

    ordered = sorted(scores.values(), key=lambda s: s["p_value"])
    fdr_values = [s["p_value_fdr"] for s in ordered]
    assert fdr_values == sorted(fdr_values)


def test_extract_mwe_candidates_penalizes_nested_bigram():
    # "yapay zeka modeli" (3 times) always contains "yapay zeka" (+2 more
    # standalone occurrences = freq 5) and "zeka modeli" (which NEVER
    # occurs on its own, freq 3 == its only longer container's freq).
    # C-value: trigram log2(3)*3=4.755; bigram "yapay zeka"
    # log2(2)*(5-3/1)=2.0; bigram "zeka modeli" log2(2)*(3-3/1)=0.0 --
    # entirely "explained away" by always riding along inside the trigram.
    word_rows = [
        ["yapay", "zeka", "modeli"],
        ["yapay", "zeka", "modeli"],
        ["yapay", "zeka", "modeli"],
        ["yapay", "zeka"],
        ["yapay", "zeka"],
    ]
    results = extract_mwe_candidates(word_rows, max_n=3, min_freq=2)
    by_text = {r["text"]: r for r in results}

    assert by_text["yapay zeka modeli"]["c_value"] == pytest.approx(4.75489, abs=1e-4)
    assert by_text["yapay zeka"]["c_value"] == pytest.approx(2.0, abs=1e-6)
    assert by_text["zeka modeli"]["c_value"] == pytest.approx(0.0, abs=1e-6)
    # Ranked descending by C-value -- the trigram is the strongest term.
    assert [r["text"] for r in results][0] == "yapay zeka modeli"


def test_extract_mwe_candidates_respects_min_freq():
    # A candidate seen only once must be dropped entirely, same rationale
    # as min_codf elsewhere in this module.
    word_rows = [["nadir", "ifade"], ["baska", "seyler", "burada"]]
    results = extract_mwe_candidates(word_rows, max_n=2, min_freq=2)
    assert results == []


def test_compute_association_measures_budget_truncates_and_reports_it():
    # A pathologically dense set of documents (many docs, tiny shared
    # vocabulary) must stop early and report truncated=True when a budget
    # is given -- matching graph_utils.maximal_cliques' same pattern.
    rows = [["a", "b", "c", "d", "e"]] * 50
    scores_unbounded, truncated_unbounded = compute_association_measures(rows, budget=None)
    scores_bounded, truncated_bounded = compute_association_measures(rows, budget=1)
    assert truncated_unbounded is False
    assert truncated_bounded is True
    assert len(scores_bounded) <= len(scores_unbounded)


def test_compute_npmi_is_a_thin_view_over_association_measures():
    rows = [["x", "y"], ["x", "y"], ["x"], ["x"], ["x"], ["z", "w"]]
    npmi_only = compute_npmi(rows)
    full, _truncated = compute_association_measures(rows)
    assert npmi_only[("x", "y")] == full[("x", "y")]["npmi"]


def test_bootstrap_confidence_interval_contains_point_estimate():
    # A basic sanity property any confidence interval must satisfy: the
    # point estimate (computed on the full, unresampled data) always
    # falls within its own bootstrap interval.
    word_rows = (
        [["yapay", "zeka", "x1"], ["yapay", "zeka", "x2"]] * 20
        + [["yapay", "other"], ["zeka", "other2"]] * 10
    )
    lower, upper, point = bootstrap_confidence_interval(
        word_rows, "yapay", "zeka", measure="npmi", n_resamples=200, seed=1
    )
    assert lower <= point + 1e-9
    assert point <= upper + 1e-9


def test_bootstrap_confidence_interval_perfectly_correlated_pair_is_degenerate():
    # A pair that co-occurs in EVERY document, with no other documents at
    # all, has zero resampling variance -- every possible resample still
    # contains only this pair, so the interval collapses to a single point.
    word_rows = [["a", "b"]] * 30
    lower, upper, point = bootstrap_confidence_interval(
        word_rows, "a", "b", measure="npmi", n_resamples=200, seed=7
    )
    assert lower == pytest.approx(1.0)
    assert upper == pytest.approx(1.0)
    assert point == pytest.approx(1.0)


def test_bootstrap_confidence_interval_stabilizes_with_more_resamples():
    # More resamples should converge toward a similar interval, not swing
    # wildly -- a weak signal that the estimator is behaving, not just
    # returning noise.
    word_rows = (
        [["a", "b", "x1"], ["a", "b", "x2"]] * 15
        + [["a", "y1"], ["b", "y2"], ["z1", "z2"]] * 15
    )
    lower_small, upper_small, _ = bootstrap_confidence_interval(
        word_rows, "a", "b", measure="npmi", n_resamples=100, seed=3
    )
    lower_large, upper_large, _ = bootstrap_confidence_interval(
        word_rows, "a", "b", measure="npmi", n_resamples=1000, seed=3
    )
    assert abs(lower_small - lower_large) < 0.3
    assert abs(upper_small - upper_large) < 0.3


def test_bootstrap_confidence_interval_handles_zero_cooccurrence_resamples_gracefully():
    # A rare pair (codf=2, right at min_codf) can easily have resamples
    # where it doesn't co-occur at all, or doesn't appear at all -- must
    # not raise (division by zero, log(0), etc.), for every measure.
    word_rows = [["a", "b"], ["a", "b"]] + [["c", "d", "e"]] * 20
    for measure in ("npmi", "log_likelihood", "dice", "t_score"):
        lower, upper, point = bootstrap_confidence_interval(
            word_rows, "a", "b", measure=measure, n_resamples=200, seed=5
        )
        assert lower <= upper + 1e-9
