from __future__ import annotations
import re
import os
from datetime import datetime
from pathlib import Path


def _detect_date_from_filename(filename: str) -> str | None:
    base = Path(filename).stem
    patterns = [
        (r"(\d{4}[-_]\d{2}[-_]\d{2})", "%Y-%m-%d"),
        (r"(\d{4}[-_]\d{2})", "%Y-%m"),
        (r"(\d{8})", "%Y%m%d"),
        (r"(\d{6})", "%Y%m"),
        (r"(\d{4})", "%Y"),
    ]
    for pattern, fmt in patterns:
        m = re.search(pattern, base)
        if m:
            try:
                dt = datetime.strptime(m.group(1), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


def parse_conllu(
    content: str, filename: str = ""
) -> list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]]:
    """Returns (date, [(word, upos), ...], raw_text, deps) per sentence.
    UPOS (column 4) is kept alongside the lemma so callers can filter to
    content words -- it used to be parsed and immediately discarded.
    raw_text preserves the original sentence for concordance/KWIC display:
    a `# text = ...` comment (the standard CoNLL-U way to carry it) is
    used when present, otherwise it's reconstructed by joining the FORM
    column in token order. deps is (token_id, head_id, deprel) per token,
    index-aligned with the word list -- lets callers build syntactic
    (dependency-based) collocations instead of same-sentence windows;
    always empty for VRT, which has no dependency annotation."""
    rows: list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]] = []
    current_words: list[tuple[str, str]] = []
    current_forms: list[str] = []
    current_deps: list[tuple[str, str, str]] = []
    current_text: str | None = None
    current_date: str | None = _detect_date_from_filename(filename) or ""

    def _flush():
        nonlocal current_words, current_forms, current_deps, current_text, current_date
        if current_words:
            text = current_text if current_text is not None else " ".join(current_forms)
            rows.append((current_date, current_words, text, current_deps))
        current_words = []
        current_forms = []
        current_deps = []
        current_text = None
        current_date = _detect_date_from_filename(filename) or ""

    for line in content.split("\n"):
        line = line.strip()

        if not line:
            _flush()
            continue

        if line.startswith("#"):
            date_match = re.search(
                r"date\s*[=:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})", line, re.IGNORECASE
            )
            if date_match:
                current_date = date_match.group(1).replace("/", "-")
            sent_id_match = re.search(
                r"sent_id\s*[=:]\s*(\S+)", line, re.IGNORECASE
            )
            if sent_id_match:
                sent_date = _detect_date_from_filename(sent_id_match.group(1))
                if sent_date:
                    current_date = sent_date
            text_match = re.match(r"#\s*text\s*=\s*(.+)$", line, re.IGNORECASE)
            if text_match:
                current_text = text_match.group(1).strip()
            continue

        cols = line.split("\t")
        if len(cols) < 4:
            continue

        token_id = cols[0]
        if "." in token_id or "-" in token_id:
            continue

        form = cols[1].strip()
        word = cols[2].strip() if cols[2].strip() and cols[2] != "_" else form
        upos = cols[3].strip() if cols[3].strip() != "_" else ""
        if word and word != "_":
            current_words.append((word, upos))
            head_id = cols[6].strip() if len(cols) > 6 and cols[6].strip() != "_" else ""
            deprel = cols[7].strip() if len(cols) > 7 and cols[7].strip() != "_" else ""
            current_deps.append((token_id, head_id, deprel))
        if form and form != "_":
            current_forms.append(form)

    _flush()

    return rows


def parse_vrt(
    content: str, filename: str = ""
) -> list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]]:
    """Returns (date, [(word, pos), ...], raw_text, deps) per document. VRT
    lines commonly carry word\\tlemma\\tpos; when a lemma column is present
    it's used instead of the raw form (reduces sparsity from inflection),
    and the pos column (if present) is kept for content-word filtering.
    Falls back to word-only when the file has no extra columns. raw_text
    is the surface-form tokens joined in order -- VRT has no standard
    raw-text comment the way CoNLL-U does, and this parser groups a whole
    <text>/<doc> block as one document, so it's necessarily coarser than
    CoNLL-U's per-sentence text (see CLAUDE.md granularity note). deps is
    always empty -- VRT carries no dependency annotation, so syntactic
    collocation mode isn't available for it."""
    rows: list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]] = []
    current_words: list[tuple[str, str]] = []
    current_forms: list[str] = []
    current_date: str = _detect_date_from_filename(filename) or ""
    in_document = False

    for line in content.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line.startswith("<"):
            if current_words and in_document:
                rows.append((current_date, current_words, " ".join(current_forms), []))
                current_words = []
                current_forms = []

            tag_match = re.match(r"<(\w+)", line)
            if tag_match:
                tag = tag_match.group(1).lower()
                if tag in ("text", "doc", "document", "article"):
                    in_document = True
                    current_date = _detect_date_from_filename(filename) or ""
                    date_attr = re.search(r'date\s*=\s*["\']?(\S+?)["\'>]', line)
                    if date_attr:
                        current_date = date_attr.group(1).replace("/", "-")
                elif tag in ("s", "sentence", "p", "paragraph"):
                    pass
                elif tag.startswith("/"):
                    pass
            continue

        parts = line.split("\t")
        word = parts[0].strip() if parts else ""
        if not word or word.startswith("<"):
            continue

        lemma = parts[1].strip() if len(parts) > 1 and parts[1].strip() not in ("", "_") else word
        pos = parts[2].strip() if len(parts) > 2 and parts[2].strip() != "_" else ""
        current_words.append((lemma, pos))
        current_forms.append(word)

    if current_words and in_document:
        rows.append((current_date, current_words, " ".join(current_forms), []))

    return rows


def detect_and_parse(
    content: str, filename: str = ""
) -> tuple[list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]], str, dict]:
    ext = Path(filename).suffix.lower()

    metadata = {
        "format": "csv",
        "rows_parsed": 0,
        "date_source": "filename" if _detect_date_from_filename(filename) else "none",
    }

    if ext in (".conllu", ".conll"):
        metadata["format"] = "conllu"
        rows = parse_conllu(content, filename)
    elif ext == ".vrt":
        metadata["format"] = "vrt"
        rows = parse_vrt(content, filename)
    else:
        return [], "unsupported", metadata

    metadata["rows_parsed"] = len(rows)
    return rows, "corpus", metadata
