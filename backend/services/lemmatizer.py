"""Lazy-loaded Turkish lemmatizer (Zeyrek/TRmorph) for CSV/JSON uploads,
which otherwise have no morphological analysis at all -- CoNLL-U/VRT
already prefer a LEMMA column when the corpus supplies one (see
corpus_parser.py), so this only matters for the two formats that don't.

Loading the FST analyzer costs ~2-3s one-time (measured); importing it
eagerly at module load would make EVERY cold start (Render's free plan
sleeps after 15min idle) pay that cost even for corpora that never
request lemmatization, so it's deferred to first actual use.
"""
import logging

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        import zeyrek
        # Zeyrek logs a `logger.warning(...)` per morphological analysis
        # path it considers -- harmless but floods production logs on
        # every lemmatize() call otherwise (measured: dozens of lines per
        # word).
        logging.getLogger("zeyrek.rulebasedanalyzer").setLevel(logging.ERROR)
        _analyzer = zeyrek.MorphAnalyzer()
    return _analyzer


def lemmatize_tr(word: str) -> tuple[str, bool]:
    """Best-effort Turkish lemma for `word`. Returns (lemma, analyzed) --
    `analyzed=False` means Zeyrek found NO real morphological parse
    (numbers, foreign/domain words outside its TRmorph vocabulary, or an
    unexpected internal error).

    Deliberately uses `analyze()`, not the higher-level `lemmatize()`:
    `lemmatize()` silently falls back to echoing the input word back as
    its own "lemma" for a word it couldn't parse at all, which made
    `analyzed` always True except for an empty string -- useless as a
    coverage signal. `analyze()` instead exposes Zeyrek's own internal
    marker for this, `Parse(pos='Unk', lemma='Unk', ...)`, which is what
    `analyzed` actually checks below. (Note: a real parse can still
    legitimately return pos='Punc' for punctuation, or a lemma identical
    to the input for an already-base-form word -- neither is a failure.)
    """
    try:
        result = _get_analyzer().analyze(word)
    except Exception:
        return word, False
    if not result or not result[0]:
        return word, False
    parses = [p for p in result[0] if p.pos != "Unk"]
    if not parses:
        return word, False
    # Prefer a lowercase (common-noun) reading over a proper-noun one so
    # e.g. "kitaplar" and a later "Kitaplar" (sentence-initial) don't
    # fragment into separate lemma nodes.
    lowercase = [p.lemma for p in parses if p.lemma[:1].islower()]
    lemma = (lowercase or [p.lemma for p in parses])[0]
    return lemma.lower(), True
