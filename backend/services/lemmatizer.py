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


def lemmatize_tr(word: str) -> str:
    """Best-effort Turkish lemma for `word`, falling back to the original
    word for anything the analyzer can't parse (numbers, punctuation,
    foreign words, or an unexpected internal error) -- this is a
    best-effort normalization to reduce inflectional sparsity, not a hard
    requirement, so any failure degrades to "leave the word as-is"."""
    try:
        results = _get_analyzer().lemmatize(word)
    except Exception:
        return word
    if not results:
        return word
    _, candidates = results[0]
    if not candidates:
        return word
    # Prefer a lowercase (common-noun) reading over a proper-noun one so
    # e.g. "kitaplar" and a later "Kitaplar" (sentence-initial) don't
    # fragment into separate lemma nodes.
    lowercase_candidates = [c for c in candidates if c[:1].islower()]
    return (lowercase_candidates or candidates)[0].lower()
