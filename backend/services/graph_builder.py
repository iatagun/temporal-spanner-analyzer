import csv
import io
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from backend.models import EdgeSchema, GraphSchema
from backend.services.lemmatizer import lemmatize_tr

TURKISH_STOPWORDS: set[str] = {
    "acaba", "altı", "altmış", "ama", "ancak", "arada", "artık",
    "asıl", "aslında", "az", "bana", "bazı", "belki", "ben", "benden",
    "beni", "benim", "beri", "beş", "bile", "bin", "bir", "birçok",
    "biri", "birkaç", "birkez", "biz", "bizden", "bizi", "bizim",
    "bu", "buna", "bunda", "bundan", "bunlar", "bunları", "bunların",
    "bunu", "bunun", "da", "daha", "dahi", "dair", "de", "defa",
    "değil", "diğer", "diye", "doksan", "dokuz", "dolayı", "dört",
    "dünya", "elli", "en", "eğer", "falan", "fazla", "filan",
    "gerek", "gibi", "göre", "gün", "hala", "halen", "hangi",
    "hani", "hatta", "hem", "henüz", "hep", "hepsi", "her",
    "herhangi", "herkes", "hiç", "hiçbir", "için", "içinde", "iki",
    "ile", "ilgili", "ise", "işte", "itibaren", "iyi", "kadar",
    "karşın", "kaç", "kendi", "kendine", "kendini", "kendisi",
    "kere", "kez", "kim", "kimden", "kime", "kimi", "kimse",
    "kırk", "ki", "lakin", "madem", "meğer", "milyon",
    "mu", "mı", "mi", "mü",
    "nasıl", "ne", "neden", "nedenle", "nerde", "nerede", "nereden",
    "nereli", "nereye", "niye", "niçin",
    "o", "olan", "olarak", "oldu", "olduğu", "olduğunu",
    "olmadı", "olmak", "olması", "olmayan", "olmaz", "olsa",
    "olsun", "olup", "olur", "olursa", "oluyor",
    "ona", "onca", "onda", "ondan", "onlar", "onlardan", "onları",
    "onların", "onu", "onun", "otuz", "oysa",
    "pek", "rağmen", "sadece", "sanki", "sana", "sekiz", "seksen",
    "sen", "senden", "seni", "senin", "siz", "sizden", "sizi", "sizin",
    "sonra", "sonuçta",
    "şey", "şeyden", "şeyi", "şeyler",
    "tarafından", "tüm",
    "üç",
    "var", "ve", "veya", "veyahut",
    "ya", "yani", "yapacak", "yapılan", "yapıyor", "yaptı",
    "yaptığı", "yaptığını", "yaptıkları",
    "yedi", "yeni", "yerine", "yetmiş", "yine", "yok", "yoksa",
    "yüz", "yüzünden", "zaten", "zira",
}


def _is_not_stopword(w: str) -> bool:
    return w not in TURKISH_STOPWORDS and len(w) > 1


# Universal-POS content-word categories. Used to filter function words
# (conjunctions, particles, pronouns, ...) out of the co-occurrence graph
# when a corpus format supplies POS tags (CoNLL-U/VRT); this is
# language-agnostic, unlike TURKISH_STOPWORDS below.
CONTENT_POS: set[str] = {"NOUN", "PROPN", "VERB", "ADJ"}


def _is_content_word(word: str, pos: str = "") -> bool:
    """POS-based content-word filter when a POS tag is available (CoNLL-U/
    VRT); falls back to the Turkish stopword list when it isn't (CSV/JSON
    have no POS info)."""
    if pos:
        return pos.upper() in CONTENT_POS and len(word) > 1
    return _is_not_stopword(word)


COLLOCATION_MODES: set[str] = {"window", "syntactic"}


def _dependency_pairs(
    word_pos_pairs: list[tuple[str, str]],
    deps: list[tuple[str, str, str]],
) -> list[tuple[str, str]]:
    """Direct HEAD-dependent word pairs between two content words (e.g.
    adjective-noun, subject-verb) -- a different notion of "co-occurring"
    than same-sentence window: syntactic proximity in the dependency tree,
    not just appearing anywhere in the same sentence. Only DIRECT parent-
    child edges count (not indirect paths through an intervening function
    word); both ends must independently pass the content-word filter."""
    if not deps or len(deps) != len(word_pos_pairs):
        return []

    id_to_word: dict[str, str] = {}
    for (word, pos), (token_id, _head_id, _deprel) in zip(word_pos_pairs, deps):
        if _is_content_word(word, pos):
            id_to_word[token_id] = word

    pairs: list[tuple[str, str]] = []
    for (word, pos), (_token_id, head_id, _deprel) in zip(word_pos_pairs, deps):
        if not _is_content_word(word, pos):
            continue
        head_word = id_to_word.get(head_id)
        if head_word and head_word != word:
            pairs.append((word, head_word))
    return pairs


# The four association measures computed for every pair -- and the only
# names valid in the `measure` parameter threaded through parse_csv/
# parse_json/parse_corpus_rows and trend_analyzer's windowed recompute.
ASSOCIATION_MEASURES: set[str] = {"npmi", "log_likelihood", "dice", "t_score"}


def compute_association_measures(
    word_rows: list[list[str]],
    min_codf: int = 2,
) -> dict[tuple[str, str], dict[str, float]]:
    """Computes four standard corpus-linguistics association measures for
    every content-word pair from one shared pass over df/codf/N -- corpus
    linguists routinely want to see (or report) more than just NPMI, and a
    tool that only ever offers one measure invites "why this one" scrutiny.

    - npmi: normalized PMI, bounded [-1, 1]. Plain PMI over-weights rare
      pairs (seen twice out of two docs can outscore seen 500/1000); NPMI
      divides that out.
    - log_likelihood: G^2 (Dunning 1993) over the word1-present/absent x
      word2-present/absent 2x2 contingency table -- the classic
      significance-of-collocation statistic, unbounded, compared against
      chi-square critical values (e.g. 3.84 for p<0.05).
    - dice: 2*codf / (df[w1]+df[w2]), bounded [0, 1].
    - t_score: (observed - expected) / sqrt(observed) -- classic collocation
      t-test, conventionally significant around 1.96-2.0.

    min_codf drops pairs seen fewer than min_codf times before any measure
    is computed -- a pair seen once is coincidence regardless of which
    measure reads it.
    """
    N = len(word_rows)
    if N < 2:
        return {}

    df: dict[str, int] = defaultdict(int)
    codf: dict[tuple[str, str], int] = defaultdict(int)

    for words in word_rows:
        unique = set(words)
        for w in unique:
            df[w] += 1
        sorted_unique = sorted(unique)
        for i in range(len(sorted_unique)):
            for j in range(i + 1, len(sorted_unique)):
                key = (sorted_unique[i], sorted_unique[j])
                codf[key] += 1

    measures: dict[tuple[str, str], dict[str, float]] = {}
    for (w1, w2), codf_val in codf.items():
        if codf_val < min_codf:
            continue
        p_xy = codf_val / N
        p_x = df[w1] / N
        p_y = df[w2] / N

        pmi = math.log(p_xy / (p_x * p_y))
        if p_xy >= 1.0:
            # Co-occurs in every row -- the -log(p_xy) normalizer is 0/0.
            # Convention: maximal (positive) association is 1.0.
            npmi = 1.0
        else:
            npmi = pmi / -math.log(p_xy)

        dice = 2 * codf_val / (df[w1] + df[w2])

        expected = N * p_x * p_y
        t_score = (codf_val - expected) / math.sqrt(codf_val)

        # G^2: a/b/c/d is the 2x2 table of (w1 present/absent) x (w2
        # present/absent) counts; d>=0 always since df[w1]+df[w2]-codf_val
        # (docs containing w1 or w2) can never exceed N.
        a = codf_val
        b = df[w1] - codf_val
        c = df[w2] - codf_val
        d = N - df[w1] - df[w2] + codf_val
        row1, row2 = a + b, c + d
        col1, col2 = a + c, b + d
        g2 = 0.0
        for observed, expected_cell in (
            (a, row1 * col1 / N),
            (b, row1 * col2 / N),
            (c, row2 * col1 / N),
            (d, row2 * col2 / N),
        ):
            if observed > 0 and expected_cell > 0:
                g2 += observed * math.log(observed / expected_cell)
        g2 *= 2

        measures[(w1, w2)] = {
            "npmi": npmi,
            "log_likelihood": g2,
            "dice": dice,
            "t_score": t_score,
        }

    return measures


def compute_npmi(
    word_rows: list[list[str]],
    min_codf: int = 2,
) -> dict[tuple[str, str], float]:
    """NPMI-only view over compute_association_measures, kept for call
    sites that only need the one score."""
    return {
        pair: scores["npmi"]
        for pair, scores in compute_association_measures(word_rows, min_codf).items()
    }


# Fallback numeric label for rows whose date could not be parsed (or was
# never provided). Kept distinct from the *detection* of an unparsed date:
# detection uses `parse_label(...) is None`, never a float comparison, so a
# genuinely valid epoch-adjacent timestamp can never be mistaken for a
# parse failure.
_UNRESOLVED_LABEL_FALLBACK = 0.0


def parse_label(raw: Any) -> float | None:
    """Parse a date/timestamp-like value into a float label. Returns None
    if `raw` could not be interpreted at all. All calendar dates are
    parsed as UTC -- interpreting them in the server's local timezone
    would make the resulting timestamps depend on where the process
    happens to run, and would raise OSError on some platforms for
    dates at/before the epoch in positive-UTC-offset locales.
    """
    if isinstance(raw, (int, float)):
        return float(raw)
    raw = str(raw).strip()
    if not raw:
        return None

    if raw.isdigit() and len(raw) == 4:
        try:
            return datetime.strptime(raw, "%Y").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass

    try:
        return float(raw)
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    return None


def _words_to_edges_filtered(
    words: list[str],
    label: float,
    word_set: set[str],
    edges: list,
    dates: list[str],
    scores: dict[tuple[str, str], dict[str, float]],
    measure: str,
    threshold: float,
    scored_pairs_seen: set[tuple[str, str]],
):
    # A pair that co-occurs across many documents gets one EdgeSchema per
    # occurrence (that's how trend/spanner windowing finds "when" a pair
    # was seen) but its `scores` are the same fixed dict every time --
    # attaching it to every occurrence measurably bloated upload responses
    # (a 27MB corpus with pairs repeating ~22x on average produced a 200MB+
    # response, ~130MB of it being duplicate scores). Every consumer
    # (frontend edgeScoreMap, spanner_service's scores_by_pair) already
    # dedups by pair anyway, so only the first occurrence needs it.
    word_set.update(words)
    dates.append(str(label))
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            key = (words[i], words[j]) if words[i] <= words[j] else (words[j], words[i])
            pair_scores = scores.get(key)
            gate_value = pair_scores[measure] if pair_scores else -float("inf")
            if gate_value >= threshold:
                include_scores = pair_scores and key not in scored_pairs_seen
                if include_scores:
                    scored_pairs_seen.add(key)
                edges.append(EdgeSchema(
                    u=words[i], v=words[j], label=label,
                    scores=pair_scores if include_scores else {},
                ))


def _validate_date_coverage(collected: list[tuple[float | None, list[str], str]]) -> None:
    total_rows = len(collected)
    unparsed_count = sum(1 for label_val, _, _ in collected if label_val is None)
    if total_rows > 0 and unparsed_count / total_rows > 0.5:
        raise ValueError(
            f"More than 50% of dates ({unparsed_count}/{total_rows}) could not be parsed. "
            "Supported formats: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, or numeric timestamps."
        )


def _build_graph(
    collected: list[tuple[float | None, list[str], str]],
    pmi_threshold: float,
    validate_dates: bool,
    measure: str = "npmi",
) -> tuple[GraphSchema, list[str], int, list[tuple[float, list[str], str]]]:
    """Shared final stage for parse_csv/parse_json/parse_corpus_rows:
    association measure computation + edge/vertex assembly. `collected`
    triples a resolved label (or None if unresolved), its already
    stopword-filtered word list, and the original raw text (for
    concordance/KWIC display). `measure` picks which of
    compute_association_measures' four scores gates edge inclusion
    against pmi_threshold -- all four are still attached to every
    surviving edge (EdgeSchema.scores) for display/comparison.

    Also returns the resolved (label, words, text) documents themselves --
    trend_analyzer needs (label, words) to recompute association scores
    per time window rather than only ever slicing the one corpus-global
    edge set; the frontend needs `text` for KWIC/concordance display.
    """
    if measure not in ASSOCIATION_MEASURES:
        raise ValueError(f"Unknown association measure: {measure}")
    if validate_dates:
        _validate_date_coverage(collected)

    word_only_rows = [words for _, words, _ in collected]
    scores = compute_association_measures(word_only_rows)

    word_set: set[str] = set()
    edges: list[EdgeSchema] = []
    dates: list[str] = []
    documents: list[tuple[float, list[str], str]] = []
    scored_pairs_seen: set[tuple[str, str]] = set()
    rows_parsed = 0

    for label_val, words, text in collected:
        label = label_val if label_val is not None else _UNRESOLVED_LABEL_FALLBACK
        _words_to_edges_filtered(
            words, label, word_set, edges, dates, scores, measure, pmi_threshold, scored_pairs_seen
        )
        documents.append((label, words, text))
        rows_parsed += 1

    graph = GraphSchema(vertices=sorted(word_set), edges=edges)
    return graph, dates, rows_parsed, documents


def _collect_rows(rows: list[list[str]], date_idx: int, words_idx: int | None, lemmatize: bool = False):
    collected: list[tuple[float | None, list[str], str]] = []
    stopword_count = 0
    for row in rows:
        if words_idx is not None:
            if len(row) <= max(date_idx, words_idx):
                continue
            label_val = parse_label(row[date_idx])
            raw_text = row[words_idx].strip()
            raw_words = re.split(r"[,\s]+", raw_text)
        else:
            if len(row) < 2:
                continue
            label_val = parse_label(row[0])
            raw_text = ",".join(row[1:])
            raw_words = re.split(r"[,\s]+", raw_text)

        # Lemmatize before the stopword filter (not after) so an
        # inflected content word collapses to its dictionary form BEFORE
        # we decide whether it's a stopword -- and so raw_text (kept for
        # KWIC/concordance display) stays the real, unlemmatized sentence.
        if lemmatize:
            raw_words = [lemmatize_tr(w) for w in raw_words]

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered, raw_text))

    return collected, stopword_count


def parse_csv(
    content: bytes, pmi_threshold: float = 0.0, measure: str = "npmi", lemmatize: bool = False
) -> tuple[GraphSchema, list[str], int, int, list[tuple[float, list[str]]]]:
    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        rows = list(reader)
    except csv.Error as e:
        raise ValueError(f"Could not parse CSV: {e}")

    if len(rows) < 2:
        raise ValueError("CSV must have a header row and at least one data row")

    header = [h.strip().lower() for h in rows[0]]

    if "words" in header and "date" in header:
        date_idx = header.index("date")
        words_idx = header.index("words")
        collected, stopword_count = _collect_rows(rows[1:], date_idx, words_idx, lemmatize)
    else:
        test_date = parse_label(rows[0][0])
        if test_date is not None:
            collected, stopword_count = _collect_rows(rows, 0, None, lemmatize)
        else:
            collected, stopword_count = _collect_rows(rows[1:], 0, None, lemmatize)

    graph, dates, rows_parsed, documents = _build_graph(
        collected, pmi_threshold, validate_dates=True, measure=measure
    )
    return graph, dates, rows_parsed, stopword_count, documents


def parse_corpus_rows(
    rows: list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]],
    pmi_threshold: float = 0.0,
    measure: str = "npmi",
    collocation_mode: str = "window",
) -> tuple[GraphSchema, list[str], int, int, list[tuple[float, list[str], str]]]:
    """collocation_mode="window" (default): a document is every content
    word in the sentence, association measures see all pairs within it --
    the original "co-occurs somewhere in the same sentence" notion.
    collocation_mode="syntactic": a document is instead each direct
    HEAD-dependent content-word pair (see _dependency_pairs) -- one
    pseudo-document per dependency edge, so the SAME association-measure
    machinery (which always looks at all pairs within a "document") ends
    up scoring specific syntactic relations instead of sentence-window
    co-occurrence. Only meaningful for CoNLL-U (VRT has no HEAD/DEPREL);
    raises ValueError if no row in `rows` carries dependency info at all.
    """
    if collocation_mode not in COLLOCATION_MODES:
        raise ValueError(f"Unknown collocation mode: {collocation_mode}")

    collected: list[tuple[float | None, list[str], str]] = []
    stopword_count = 0

    if collocation_mode == "syntactic":
        # `deps` entries always exist for CoNLL-U (one per token, see
        # parse_conllu) even when the file has no HEAD column at all --
        # they just carry a blank head_id then (4-column CoNLL-U, e.g.
        # this project's own sample.conllu). Checking "any deps list is
        # non-empty" would miss that case entirely and silently produce
        # an empty graph instead of a clear error; check for at least one
        # real head reference instead.
        if not any(head_id for _, _, _, deps in rows for _, head_id, _ in deps):
            raise ValueError(
                "collocation_mode=syntactic requires CoNLL-U HEAD/DEPREL columns; "
                "this corpus (or format) doesn't carry dependency information."
            )
        for date_str, word_pos_pairs, raw_text, deps in rows:
            label = parse_label(date_str) if date_str else _UNRESOLVED_LABEL_FALLBACK
            content_count = sum(1 for w, pos in word_pos_pairs if _is_content_word(w, pos))
            stopword_count += len(word_pos_pairs) - content_count
            for child, head in _dependency_pairs(word_pos_pairs, deps):
                collected.append((label, [child, head], raw_text))
        graph, dates, rows_parsed, documents = _build_graph(
            collected, pmi_threshold, validate_dates=True, measure=measure
        )
        return graph, dates, rows_parsed, stopword_count, documents

    for date_str, word_pos_pairs, raw_text, _deps in rows:
        # An empty date_str means the corpus file carried no date metadata
        # at all (no filename pattern, no #date comment) -- that's an
        # expected condition for many corpora, not a parse failure, so it
        # gets the fallback bucket directly rather than going through
        # parse_label (which would otherwise have to special-case turning
        # "no date" into a fake date string just to parse it back out).
        label = parse_label(date_str) if date_str else _UNRESOLVED_LABEL_FALLBACK

        filtered = [w for w, pos in word_pos_pairs if _is_content_word(w, pos)]
        stopword_count += len(word_pos_pairs) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label, filtered, raw_text))

    graph, dates, rows_parsed, documents = _build_graph(
        collected, pmi_threshold, validate_dates=True, measure=measure
    )
    return graph, dates, rows_parsed, stopword_count, documents


def parse_json(
    content: bytes, pmi_threshold: float = 0.0, measure: str = "npmi", lemmatize: bool = False
) -> tuple[GraphSchema, list[str], int, int, list[tuple[float, list[str], str]]]:
    data = json.loads(content.decode("utf-8-sig"))

    docs = data if isinstance(data, list) else data.get("documents", data.get("data", []))

    collected: list[tuple[float | None, list[str], str]] = []
    stopword_count = 0

    for doc in docs:
        if isinstance(doc, dict):
            # `or`-chaining here would treat an explicit falsy date (0, the
            # epoch) as "missing" and fall through to another field. Check
            # key presence instead so a real 0 survives, and so a document
            # with no date field at all stays None (not a fabricated 0)
            # -- None is what _validate_date_coverage checks for below,
            # matching parse_csv's stricter "no date info" handling instead
            # of silently accepting a corpus with zero real date data.
            date_val = doc.get("date")
            if date_val is None:
                date_val = doc.get("tarih")
            if date_val is None:
                date_val = doc.get("timestamp")
            if date_val is None:
                date_val = doc.get("zaman")
            raw_words = (
                doc.get("words")
                or doc.get("kelimeler")
                or doc.get("tokens")
                or doc.get("sozcukler", [])
            )
        elif isinstance(doc, list) and len(doc) >= 2:
            date_val, raw_words = doc[0], doc[1]
        else:
            continue

        label_val = parse_label(date_val) if date_val is not None else None
        # Captured before the string is split into tokens (raw_text below)
        # and before a list gets normalized into one -- either way it's
        # the closest thing to "the original sentence" this format has,
        # for concordance/KWIC display.
        raw_text = raw_words if isinstance(raw_words, str) else " ".join(str(w) for w in raw_words) if isinstance(raw_words, list) else ""
        if isinstance(raw_words, str):
            raw_words = re.split(r"[,\s]+", raw_words)
        if not isinstance(raw_words, list) or len(raw_words) < 1:
            continue

        if lemmatize:
            raw_words = [lemmatize_tr(str(w)) for w in raw_words]

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered, raw_text))

    graph, dates, rows_parsed, documents = _build_graph(
        collected, pmi_threshold, validate_dates=True, measure=measure
    )
    return graph, dates, rows_parsed, stopword_count, documents
