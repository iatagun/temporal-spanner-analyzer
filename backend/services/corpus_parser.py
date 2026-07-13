from __future__ import annotations
import re
import os
import xml.etree.ElementTree as ET
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


# TEI POS values only get passed through to _is_content_word as a real
# tag if they look like Universal POS -- corpora tagged with some other
# scheme (Penn Treebank "NN", STTS, etc.) would otherwise have every
# single token silently misclassified as a function word (since
# _is_content_word treats any non-empty, non-matching pos as "not
# content"). Falling back to pos="" instead degrades gracefully to the
# Turkish-stopword heuristic, the same path CSV/JSON already use.
_KNOWN_UPOS: set[str] = {
    "NOUN", "PROPN", "VERB", "ADJ", "ADV", "ADP", "AUX", "CCONJ", "DET",
    "INTJ", "NUM", "PART", "PRON", "PUNCT", "SCONJ", "SYM", "X",
}


def _local_name(tag: str) -> str:
    # Strips a `{namespace-uri}` prefix ElementTree adds for elements
    # declared under a default xmlns (TEI files typically declare
    # xmlns="http://www.tei-c.org/ns/1.0") -- lets tag matching below work
    # the same whether or not the file bothers with a namespace.
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _tei_date_text(elem: ET.Element) -> str | None:
    for attr in ("when", "from", "notBefore"):
        val = elem.get(attr)
        if val:
            return val
    text = (elem.text or "").strip()
    return text or None


def _collect_tei_sentence(s_elem: ET.Element) -> tuple[list[tuple[str, str]], str]:
    words: list[tuple[str, str]] = []
    forms: list[str] = []
    for w in s_elem.iter():
        if _local_name(w.tag) != "w":
            continue
        form = (w.text or "").strip()
        lemma = w.get("lemma", "").strip() or form
        pos_raw = w.get("pos", "").strip()
        pos = pos_raw.upper() if pos_raw.upper() in _KNOWN_UPOS else ""
        if lemma:
            words.append((lemma, pos))
        if form:
            forms.append(form)
    return words, " ".join(forms)


def _walk_tei_word_level(
    elem: ET.Element,
    current_date: str,
    filename: str,
    rows: list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]],
) -> str:
    # Returns the (possibly updated) current_date so the CALLER's loop can
    # carry it forward to later siblings -- current_date is a plain str
    # (immutable), so a `current_date = new_date` reassignment inside a
    # recursive call is local to that call frame and would otherwise be
    # silently lost the moment that call returns (e.g. a <date> in
    # <teiHeader> would never reach the later <text> sibling).
    tag = _local_name(elem.tag)
    if tag == "date":
        new_date = _tei_date_text(elem)
        if new_date:
            current_date = new_date
    if tag == "s":
        words, text = _collect_tei_sentence(elem)
        if words:
            rows.append((current_date, words, text, []))
        return current_date  # <w> elements already consumed via .iter() above
    for child in elem:
        current_date = _walk_tei_word_level(child, current_date, filename, rows)
    return current_date


def parse_tei(
    content: str, filename: str = ""
) -> list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]]:
    """Best-effort TEI/XML support -- real TEI corpora vary hugely (from
    word-level linguistically annotated `<w lemma="..." pos="...">` to
    plain untokenized prose in `<p>`), so this covers two common cases and
    documents what it does NOT cover: bespoke TEI customizations, complex
    apparatus criticus, or word-level annotation via a scheme other than
    `@lemma`/`@pos` attributes on `<w>` (e.g. `@ana` pointing to a separate
    feature-structure library) are NOT supported.

    - Word-level mode (used when the file has any `<w>` element at all):
      each `<s>` (sentence) becomes one document, same fine-grained
      granularity as CoNLL-U. `deps` is always empty -- TEI's dependency
      annotation (if any) isn't standardized enough to support generically.
    - Plain-text fallback (no `<w>` at all): each `<p>` (or the whole
      `<body>` if there's no `<p>`) becomes one document of whitespace-
      split tokens with pos="" -- same coarse granularity, and the same
      Turkish-stopword content-word fallback, as CSV/JSON.
    - Date: the nearest enclosing `<date>` element's `@when`/`@from`/
      `@notBefore` attribute or text content, walked top-down so a
      `<date>` in an outer `<div>` applies to sentences/paragraphs
      nested inside it unless overridden by a closer one. Falls back to
      _detect_date_from_filename if no `<date>` is found anywhere.
    """
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"Could not parse XML: {e}")

    base_date = _detect_date_from_filename(filename) or ""
    has_words = any(_local_name(el.tag) == "w" for el in root.iter())

    rows: list[tuple[str, list[tuple[str, str]], str, list[tuple[str, str, str]]]] = []

    if has_words:
        _walk_tei_word_level(root, base_date, filename, rows)
        return rows

    # Plain-text fallback: one document per <p>, or the whole <body>/root
    # if there are no <p> elements at all. Date: the first <date> found
    # ANYWHERE in the document (most commonly the header's publication
    # date) applies to every block -- a per-paragraph nearest-ancestor
    # lookup would need real parent-tracking (ElementTree has no parent
    # pointers) for a case (a whole TEI file per differently-dated
    # paragraph) that's unusual for what's normally one dated document
    # per file, matching CSV/JSON's equally simple one-date-per-row model.
    current_date = base_date
    for date_el in root.iter():
        if _local_name(date_el.tag) == "date":
            found_date = _tei_date_text(date_el)
            if found_date:
                current_date = found_date
            break

    paragraphs = [el for el in root.iter() if _local_name(el.tag) == "p"]
    blocks = paragraphs if paragraphs else [root]

    for block in blocks:
        text = " ".join("".join(block.itertext()).split())
        if not text:
            continue
        tokens = re.split(r"\s+", text.strip())
        words = [(t, "") for t in tokens if t]
        if words:
            rows.append((current_date, words, text, []))

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
    elif ext in (".xml", ".tei"):
        metadata["format"] = "tei"
        rows = parse_tei(content, filename)
    else:
        return [], "unsupported", metadata

    metadata["rows_parsed"] = len(rows)
    return rows, "corpus", metadata
