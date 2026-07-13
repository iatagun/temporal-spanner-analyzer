import sys


def test_lemmatizer_module_does_not_import_zeyrek_at_module_load():
    # Regression test for the lazy-loading design: importing
    # backend.services.lemmatizer (which graph_builder.py does
    # unconditionally) must not itself trigger the ~2-3s zeyrek/TRmorph
    # analyzer load -- that cost should only be paid by requests that
    # actually ask for lemmatize=True.
    sys.modules.pop("zeyrek", None)
    sys.modules.pop("backend.services.lemmatizer", None)
    import backend.services.lemmatizer  # noqa: F401
    assert "zeyrek" not in sys.modules


def test_lemmatize_tr_collapses_known_inflections():
    from backend.services.lemmatizer import lemmatize_tr
    assert lemmatize_tr("kitaplar") == "kitap"
    assert lemmatize_tr("evlerinden") == "ev"


def test_lemmatize_tr_falls_back_to_original_for_unanalyzable_input():
    from backend.services.lemmatizer import lemmatize_tr
    # Punctuation-only / empty-ish input the analyzer can't parse at all.
    assert lemmatize_tr("...") == "..."
