import csv
import io
import json
import math
import re
from collections import defaultdict
from datetime import datetime
from typing import Any

from backend.models import EdgeSchema, GraphSchema

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


def _compute_pmi(
    word_rows: list[list[str]],
    min_codf: int = 1,
) -> dict[tuple[str, str], float]:
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

    pmi: dict[tuple[str, str], float] = {}
    for (w1, w2), codf_val in codf.items():
        if codf_val < min_codf:
            continue
        ratio = N * codf_val / (df[w1] * df[w2])
        pmi[(w1, w2)] = math.log(ratio) if ratio > 0 else -float("inf")

    return pmi


_UNPARSED_DATE_SENTINEL = 0.0


def parse_label(raw: Any) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    raw = str(raw).strip()
    try:
        return float(raw)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).timestamp()
        except ValueError:
            pass
    return _UNPARSED_DATE_SENTINEL


def _words_to_edges_filtered(
    words: list[str],
    label: float,
    word_set: set[str],
    edges: list,
    dates: list[str],
    pmi: dict[tuple[str, str], float],
    pmi_threshold: float = 0.0,
):
    word_set.update(words)
    dates.append(str(label))
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            key = (words[i], words[j]) if words[i] <= words[j] else (words[j], words[i])
            pair_pmi = pmi.get(key, -float("inf"))
            if pair_pmi >= pmi_threshold:
                edges.append(EdgeSchema(u=words[i], v=words[j], label=label))


def _collect_rows(rows: list[list[str]], date_idx: int, words_idx: int | None):
    collected: list[tuple[float, list[str]]] = []
    stopword_count = 0
    for row in rows:
        if words_idx is not None:
            if len(row) <= max(date_idx, words_idx):
                continue
            label_val = parse_label(row[date_idx])
            raw_words = re.split(r"[,\s]+", row[words_idx].strip())
        else:
            if len(row) < 2:
                continue
            label_val = parse_label(row[0])
            raw_words = re.split(r"[,\s]+", ",".join(row[1:]))

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered))

    return collected, stopword_count


def parse_csv(
    content: bytes, pmi_threshold: float = 0.0
) -> tuple[GraphSchema, list[str], int, int]:
    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if len(rows) < 2:
        raise ValueError("CSV must have a header row and at least one data row")

    header = [h.strip().lower() for h in rows[0]]

    if "words" in header and "date" in header:
        date_idx = header.index("date")
        words_idx = header.index("words")
        collected, stopword_count = _collect_rows(rows[1:], date_idx, words_idx)
    else:
        test_date = parse_label(rows[0][0])
        if test_date != _UNPARSED_DATE_SENTINEL:
            collected, stopword_count = _collect_rows(rows, 0, None)
        else:
            collected, stopword_count = _collect_rows(rows[1:], 0, None)

    word_only_rows = [words for _, words in collected]

    unparsed_count = sum(1 for label_val, _ in collected if label_val == _UNPARSED_DATE_SENTINEL)
    total_rows = len(collected)
    if total_rows > 0 and unparsed_count / total_rows > 0.5:
        raise ValueError(
            f"More than 50% of dates ({unparsed_count}/{total_rows}) could not be parsed. "
            "Supported formats: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, or numeric timestamps."
        )

    pmi = _compute_pmi(word_only_rows)

    word_set: set[str] = set()
    edges: list[EdgeSchema] = []
    dates: list[str] = []
    rows_parsed = 0

    for label_val, words in collected:
        _words_to_edges_filtered(
            words, label_val, word_set, edges, dates, pmi, pmi_threshold
        )
        rows_parsed += 1

    V = sorted(word_set)
    graph = GraphSchema(vertices=V, edges=edges)
    return graph, dates, rows_parsed, stopword_count


def parse_json(
    content: bytes, pmi_threshold: float = 0.0
) -> tuple[GraphSchema, list[str], int, int]:
    data = json.loads(content.decode("utf-8-sig"))

    docs = data if isinstance(data, list) else data.get("documents", data.get("data", []))

    collected: list[tuple[float, list[str]]] = []
    stopword_count = 0

    for doc in docs:
        if isinstance(doc, dict):
            date_val = (
                doc.get("date")
                or doc.get("tarih")
                or doc.get("timestamp")
                or doc.get("zaman", 0)
            )
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

        label_val = parse_label(date_val)
        if isinstance(raw_words, str):
            raw_words = re.split(r"[,\s]+", raw_words)
        if not isinstance(raw_words, list) or len(raw_words) < 1:
            continue

        filtered = [w for w in raw_words if _is_not_stopword(w)]
        stopword_count += len(raw_words) - len(filtered)
        if len(filtered) >= 2:
            collected.append((label_val, filtered))

    word_only_rows = [words for _, words in collected]

    unparsed_count = sum(1 for label_val, _ in collected if label_val == _UNPARSED_DATE_SENTINEL)
    total_rows = len(collected)
    if total_rows > 0 and unparsed_count / total_rows > 0.5:
        raise ValueError(
            f"More than 50% of dates ({unparsed_count}/{total_rows}) could not be parsed. "
            "Supported formats: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, or numeric timestamps."
        )

    pmi = _compute_pmi(word_only_rows)

    word_set: set[str] = set()
    edges: list[EdgeSchema] = []
    dates: list[str] = []
    rows_parsed = 0

    for label_val, words in collected:
        _words_to_edges_filtered(
            words, label_val, word_set, edges, dates, pmi, pmi_threshold
        )
        rows_parsed += 1

    V = sorted(word_set)
    graph = GraphSchema(vertices=V, edges=edges)
    return graph, dates, rows_parsed, stopword_count
