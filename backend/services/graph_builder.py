import csv
import io
import json
import math
import random
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
    budget: int | None = None,
) -> tuple[dict[tuple[str, str], dict[str, float]], bool]:
    """Computes four standard corpus-linguistics association measures for
    every content-word pair from one shared pass over df/codf/N -- corpus
    linguists routinely want to see (or report) more than just NPMI, and a
    tool that only ever offers one measure invites "why this one" scrutiny.
    Also tracks adjacency (for multi-word-expression detection, see
    `adjacency_ratio` below).

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
    - adjacency_ratio: fraction of this pair's co-occurrences where the two
      words were IMMEDIATE neighbors (not just anywhere in the same
      document) -- a necessary condition for a multi-word expression like
      "yapay zeka". Not a gating measure (never in ASSOCIATION_MEASURES,
      can't be selected as the upload threshold), purely informational.

    min_codf drops pairs seen fewer than min_codf times before any measure
    is computed -- a pair seen once is coincidence regardless of which
    measure reads it.

    `budget` caps the number of distinct pairs tracked (len(codf)),
    checked once per document (cheap) -- same budget+truncated pattern as
    graph_utils.maximal_cliques's Bron-Kerbosch search. A narrow,
    densely-repeating vocabulary spread across many documents can make
    `codf` approach the full C(V,2) pair space (measured: 13.5s at just
    11MB in that pathological case, see CLAUDE.md's "Büyük Derlem" note).
    None (default) is unbounded -- /api/upload's one-shot corpus-global
    call uses that (already measured fast even at 27MB); trend_analyzer's
    per-window recompute passes a real budget since it repeats this
    computation once per window.
    """
    N = len(word_rows)
    if N < 2:
        return {}, False

    df: dict[str, int] = defaultdict(int)
    codf: dict[tuple[str, str], int] = defaultdict(int)
    adjacency_count: dict[tuple[str, str], int] = defaultdict(int)
    truncated = False

    for words in word_rows:
        if budget is not None and len(codf) >= budget:
            truncated = True
            break
        unique = set(words)
        for w in unique:
            df[w] += 1
        sorted_unique = sorted(unique)
        for i in range(len(sorted_unique)):
            for j in range(i + 1, len(sorted_unique)):
                key = (sorted_unique[i], sorted_unique[j])
                codf[key] += 1
        # Adjacency needs the ORIGINAL word order -- sorted_unique above
        # (used for codf) is alphabetical, not positional.
        for i in range(len(words) - 1):
            a, b = words[i], words[i + 1]
            if a == b:
                continue
            key = (a, b) if a <= b else (b, a)
            adjacency_count[key] += 1

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

        # p_value: G^2 asymptotically follows a chi-square distribution
        # with df=1 under the null (independence) hypothesis. Its survival
        # function has a closed form for df=1 -- P(chi2_1 > x) =
        # erfc(sqrt(x/2)) -- avoiding a scipy dependency just for this.
        # Verified against the standard critical values: erfc(sqrt(3.841/2))
        # = 0.05000, erfc(sqrt(6.635/2)) = 0.01000, erfc(sqrt(10.828/2)) = 0.00100.
        # g2 is mathematically always >= 0, but a tiny negative float
        # artifact (rounding) is possible right at 0 -- guard sqrt() with
        # max() rather than a bare `g2 > 0` check.
        p_value = math.erfc(math.sqrt(max(g2, 0.0) / 2))

        measures[(w1, w2)] = {
            "npmi": npmi,
            "log_likelihood": g2,
            "dice": dice,
            "t_score": t_score,
            "adjacency_ratio": adjacency_count.get((w1, w2), 0) / codf_val,
            "p_value": p_value,
        }

    # Multiple-comparison correction: with potentially thousands of pairs
    # tested at once, an uncorrected p<0.05 on log_likelihood produces
    # ~5% * n_pairs false positives by chance alone. These are purely
    # informational (like adjacency_ratio) -- gating still uses the raw
    # measure the caller selected, for backward compatibility.
    n_pairs = len(measures)
    if n_pairs > 0:
        sorted_by_p = sorted(measures.items(), key=lambda kv: kv[1]["p_value"])
        running_min = 1.0
        for rank in range(n_pairs, 0, -1):
            _key, scores = sorted_by_p[rank - 1]
            raw_p = scores["p_value"]
            # Benjamini-Hochberg step-up: q(i) = min_{k>=i} p(k)*n/k,
            # enforced here by scanning from the largest rank down and
            # keeping a running minimum so q is monotonically non-decreasing
            # as rank increases (required for BH to be valid).
            running_min = min(running_min, raw_p * n_pairs / rank)
            scores["p_value_fdr"] = min(1.0, running_min)
            scores["p_value_bonferroni"] = min(1.0, raw_p * n_pairs)

    return measures, truncated


def _is_contiguous_subsequence(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    ls, ll = len(short), len(long)
    if ls >= ll:
        return False
    return any(long[i:i + ls] == short for i in range(ll - ls + 1))


def extract_mwe_candidates(
    word_rows: list[list[str]],
    max_n: int = 4,
    min_freq: int = 2,
    top_n: int = 50,
) -> list[dict]:
    """Ranks multi-word-expression candidates (contiguous word n-grams,
    n=2..max_n) by C-value (Frantzi & Ananiadou 1996) -- generalizes
    compute_association_measures' adjacency_ratio (a coarse bigram-only
    yes/no signal) into a real term-extraction ranking that accounts for
    NESTING: "yapay zeka" scores lower if it almost always occurs inside
    the longer "yapay zeka modeli", since that's evidence it isn't really
    an independent unit on its own.

    C-value(a) = log2(|a|) * f(a) if `a` is never nested in a longer
    candidate; otherwise log2(|a|) * (f(a) - mean(f(b) for b in
    longer-candidates-containing-a)) -- the classic formula.

    n-grams are extracted from the same filtered, order-preserved word
    list already used for compute_association_measures -- so, like
    adjacency_ratio, "contiguous" means contiguous in the CONTENT-WORD
    sequence (stopwords already removed), not the raw original sentence.
    `min_freq` drops candidates below it entirely, same rationale as
    `min_codf` elsewhere: a term seen once is coincidence, not a pattern.
    """
    freq: dict[tuple[str, ...], int] = defaultdict(int)
    for words in word_rows:
        for n in range(2, max_n + 1):
            for i in range(len(words) - n + 1):
                freq[tuple(words[i:i + n])] += 1

    candidates = {ngram: f for ngram, f in freq.items() if f >= min_freq}
    if not candidates:
        return []

    by_length: dict[int, list[tuple[str, ...]]] = defaultdict(list)
    for ngram in candidates:
        by_length[len(ngram)].append(ngram)

    results: list[dict] = []
    for ngram, f in candidates.items():
        length = len(ngram)
        nested_in_freqs = [
            candidates[longer]
            for longer_len in range(length + 1, max_n + 1)
            for longer in by_length.get(longer_len, ())
            if _is_contiguous_subsequence(ngram, longer)
        ]
        if nested_in_freqs:
            c_value = math.log2(length) * (f - sum(nested_in_freqs) / len(nested_in_freqs))
        else:
            c_value = math.log2(length) * f
        results.append({
            "ngram": list(ngram),
            "text": " ".join(ngram),
            "frequency": f,
            "c_value": c_value,
        })

    results.sort(key=lambda r: r["c_value"], reverse=True)
    return results[:top_n] if top_n else results


def _bootstrap_pair_score(codf_val: int, df_w1: int, df_w2: int, N: int, measure: str) -> float:
    """Same formulas as compute_association_measures' per-pair math, but
    tolerant of codf_val==0 (a real possibility when bootstrap resampling
    happens to drop every document containing the pair) -- the batch
    version never needs this, since it only ever processes pairs already
    confirmed to have codf_val >= min_codf > 0."""
    if N == 0:
        return 0.0
    p_x = df_w1 / N
    p_y = df_w2 / N
    p_xy = codf_val / N

    if measure == "dice":
        denom = df_w1 + df_w2
        return (2 * codf_val / denom) if denom > 0 else 0.0

    if measure == "t_score":
        if codf_val == 0:
            return 0.0
        expected = N * p_x * p_y
        return (codf_val - expected) / math.sqrt(codf_val)

    if measure == "log_likelihood":
        a, b = codf_val, df_w1 - codf_val
        c, d = df_w2 - codf_val, N - df_w1 - df_w2 + codf_val
        row1, row2 = a + b, c + d
        col1, col2 = a + c, b + d
        g2 = 0.0
        for observed, expected_cell in (
            (a, row1 * col1 / N), (b, row1 * col2 / N),
            (c, row2 * col1 / N), (d, row2 * col2 / N),
        ):
            if observed > 0 and expected_cell > 0:
                g2 += observed * math.log(observed / expected_cell)
        return g2 * 2

    # npmi (default)
    if p_xy <= 0 or p_x <= 0 or p_y <= 0:
        return -1.0  # no co-occurrence at all -- NPMI's minimal value
    pmi = math.log(p_xy / (p_x * p_y))
    if p_xy >= 1.0:
        return 1.0
    return pmi / -math.log(p_xy)


def bootstrap_confidence_interval(
    word_rows: list[list[str]],
    w1: str,
    w2: str,
    measure: str = "npmi",
    n_resamples: int = 500,
    seed: int | None = None,
) -> tuple[float, float, float]:
    """Bootstrap confidence interval for a SINGLE pair's association
    score. Resamples documents WITH REPLACEMENT n_resamples times,
    recomputes just this one pair's score in each resample, and returns
    the (2.5th percentile, 97.5th percentile, point estimate on the full
    data).

    Deliberately per-pair and opt-in (see /api/pair-confidence), NOT run
    automatically for every pair a corpus produces: doing this for
    potentially tens of thousands of pairs (see
    compute_association_measures) would multiply the whole corpus's
    computation cost by n_resamples, undoing the Faz A performance work
    on /api/trends. Presence/absence of each word is precomputed ONCE per
    document (O(N) total) so each resample only re-sums booleans by
    index (O(N) per resample) rather than re-scanning word lists --
    n_resamples=500 stays well under a second even for large corpora.
    """
    N = len(word_rows)
    if N < 2:
        return (0.0, 0.0, 0.0)

    has_w1 = [w1 in set(row) for row in word_rows]
    has_w2 = [w2 in set(row) for row in word_rows]

    def _counts(indices: list[int]) -> tuple[int, int, int]:
        df_w1 = sum(1 for i in indices if has_w1[i])
        df_w2 = sum(1 for i in indices if has_w2[i])
        codf = sum(1 for i in indices if has_w1[i] and has_w2[i])
        return codf, df_w1, df_w2

    codf, df_w1, df_w2 = _counts(list(range(N)))
    point_estimate = _bootstrap_pair_score(codf, df_w1, df_w2, N, measure)

    rng = random.Random(seed)
    resampled_scores: list[float] = []
    for _ in range(n_resamples):
        indices = [rng.randrange(N) for _ in range(N)]
        rc, rw1, rw2 = _counts(indices)
        resampled_scores.append(_bootstrap_pair_score(rc, rw1, rw2, N, measure))

    resampled_scores.sort()
    lower_idx = int(0.025 * n_resamples)
    upper_idx = min(n_resamples - 1, int(0.975 * n_resamples))
    return resampled_scores[lower_idx], resampled_scores[upper_idx], point_estimate


def compute_npmi(
    word_rows: list[list[str]],
    min_codf: int = 2,
) -> dict[tuple[str, str], float]:
    """NPMI-only view over compute_association_measures, kept for call
    sites that only need the one score."""
    measures, _truncated = compute_association_measures(word_rows, min_codf)
    return {pair: scores["npmi"] for pair, scores in measures.items()}


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
    # budget=None (unbounded) -- this one-shot corpus-global computation is
    # already measured fast even at 27MB (see CLAUDE.md); only the
    # per-window recompute in trend_analyzer needs a real budget.
    scores, _truncated = compute_association_measures(word_only_rows)

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
    lemmatized_count = 0
    lemmatized_total = 0
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
            new_words = []
            for w in raw_words:
                lemma, analyzed = lemmatize_tr(w)
                new_words.append(lemma)
                lemmatized_total += 1
                if analyzed:
                    lemmatized_count += 1
            raw_words = new_words

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered, raw_text))

    return collected, stopword_count, lemmatized_count, lemmatized_total


def parse_csv(
    content: bytes, pmi_threshold: float = 0.0, measure: str = "npmi", lemmatize: bool = False
) -> tuple[GraphSchema, list[str], int, int, list[tuple[float, list[str]]], int, int]:
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
        collected, stopword_count, lemmatized_count, lemmatized_total = _collect_rows(
            rows[1:], date_idx, words_idx, lemmatize
        )
    else:
        test_date = parse_label(rows[0][0])
        if test_date is not None:
            collected, stopword_count, lemmatized_count, lemmatized_total = _collect_rows(
                rows, 0, None, lemmatize
            )
        else:
            collected, stopword_count, lemmatized_count, lemmatized_total = _collect_rows(
                rows[1:], 0, None, lemmatize
            )

    graph, dates, rows_parsed, documents = _build_graph(
        collected, pmi_threshold, validate_dates=True, measure=measure
    )
    return graph, dates, rows_parsed, stopword_count, documents, lemmatized_count, lemmatized_total


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
) -> tuple[GraphSchema, list[str], int, int, list[tuple[float, list[str], str]], int, int]:
    data = json.loads(content.decode("utf-8-sig"))

    docs = data if isinstance(data, list) else data.get("documents", data.get("data", []))

    collected: list[tuple[float | None, list[str], str]] = []
    stopword_count = 0
    lemmatized_count = 0
    lemmatized_total = 0

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
            new_words = []
            for w in raw_words:
                lemma, analyzed = lemmatize_tr(str(w))
                new_words.append(lemma)
                lemmatized_total += 1
                if analyzed:
                    lemmatized_count += 1
            raw_words = new_words

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered, raw_text))

    graph, dates, rows_parsed, documents = _build_graph(
        collected, pmi_threshold, validate_dates=True, measure=measure
    )
    return graph, dates, rows_parsed, stopword_count, documents, lemmatized_count, lemmatized_total
