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
    assert lemmatize_tr("kitaplar") == ("kitap", True)
    assert lemmatize_tr("evlerinden") == ("ev", True)


def test_lemmatize_tr_falls_back_to_original_for_unanalyzable_input():
    from backend.services.lemmatizer import lemmatize_tr
    # A nonsense token outside Zeyrek's TRmorph vocabulary (stand-in for
    # a domain-specific term or non-Turkish word) -- Zeyrek's own analyze()
    # marks this pos='Unk', which is exactly the "silent limit" this
    # function makes visible via `analyzed`, instead of just checking
    # word==lemma (a real analysis can legitimately return the input
    # unchanged too, e.g. an already-base-form noun -- see the docstring).
    lemma, analyzed = lemmatize_tr("xyzqwerty")
    assert lemma == "xyzqwerty"
    assert analyzed is False


def test_lemmatize_tr_recognizes_punctuation_as_analyzed_not_a_failure():
    from backend.services.lemmatizer import lemmatize_tr
    # Regression guard: punctuation gets a real pos='Punc' classification
    # from Zeyrek, not pos='Unk' -- must count as analyzed=True, not be
    # mistaken for an analysis failure.
    lemma, analyzed = lemmatize_tr("...")
    assert lemma == "..."
    assert analyzed is True
