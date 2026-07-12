from backend.services.graph_builder import parse_label, parse_corpus_rows


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
    # don't trip the >50%-unparsed validation.
    rows = [("", ["elma", "armut"]), ("", ["armut", "muz"]), ("", ["elma", "muz"])]
    graph, dates, rows_parsed, _ = parse_corpus_rows(rows)
    assert rows_parsed == 3
    assert set(graph.vertices) == {"elma", "armut", "muz"}


def test_corpus_rows_flags_mostly_unparseable_dates():
    rows = [("garbled-date-1", ["a", "b"]), ("garbled-date-2", ["b", "c"])]
    try:
        parse_corpus_rows(rows)
        assert False, "expected ValueError for mostly-unparseable dates"
    except ValueError:
        pass
