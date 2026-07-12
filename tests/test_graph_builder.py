from backend.services.graph_builder import (
    parse_label,
    parse_corpus_rows,
    _compute_pmi,
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
        ("", [("elma", ""), ("armut", "")]),
        ("", [("armut", ""), ("muz", "")]),
        ("", [("elma", ""), ("muz", "")]),
    ]
    graph, dates, rows_parsed, _ = parse_corpus_rows(rows)
    assert rows_parsed == 3
    assert set(graph.vertices) == {"elma", "armut", "muz"}


def test_corpus_rows_flags_mostly_unparseable_dates():
    rows = [
        ("garbled-date-1", [("aa", "NOUN"), ("bb", "NOUN")]),
        ("garbled-date-2", [("bb", "NOUN"), ("cc", "NOUN")]),
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
        ("2020-01-01", [("elma", "NOUN"), ("ve", "CCONJ"), ("armut", "NOUN")]),
        ("2020-02-01", [("elma", "NOUN"), ("ve", "CCONJ"), ("armut", "NOUN")]),
    ]
    graph, _, rows_parsed, stopword_count = parse_corpus_rows(rows)
    assert rows_parsed == 2
    assert "ve" not in graph.vertices
    assert set(graph.vertices) == {"elma", "armut"}
    assert stopword_count == 2  # "ve" dropped from both rows


def test_is_content_word_pos_vs_fallback():
    assert _is_content_word("elma", "NOUN") is True
    assert _is_content_word("ve", "CCONJ") is False
    assert _is_content_word("ve", "") is False  # falls back to stopword list
    assert _is_content_word("armut", "") is True


def test_compute_pmi_is_normalized_and_penalizes_hapax():
    # NPMI must stay within [-1, 1] and a pair seen only once (below
    # min_codf) must not appear at all -- this is the fix for raw PMI's
    # bias toward rare pairs.
    rows = [
        ["a", "b"], ["a", "b"], ["c", "d"], ["c", "d"],
        ["a", "b"], ["c", "d"], ["e", "f"],
    ]
    pmi = _compute_pmi(rows)
    assert ("e", "f") not in pmi  # codf=1 < default min_codf=2
    for score in pmi.values():
        assert -1.0 <= score <= 1.0
