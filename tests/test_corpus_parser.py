import pytest

from backend.services.corpus_parser import parse_conllu, parse_vrt, parse_tei


def test_parse_conllu_keeps_upos_alongside_lemma():
    # Regression test: UPOS (column 4) used to be parsed and discarded --
    # it must now travel with each (word, pos) pair so callers can do
    # content-word filtering.
    content = (
        "1\televlerin\tev\tNOUN\t_\t_\t2\tnmod\t_\t_\n"
        "2\tve\tve\tCCONJ\t_\t_\t3\tcc\t_\t_\n"
        "3\tbahce\tbahce\tNOUN\t_\t_\t0\troot\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    date, words, text, deps = rows[0]
    assert words == [("ev", "NOUN"), ("ve", "CCONJ"), ("bahce", "NOUN")]


def test_parse_conllu_multiword_tokens_skipped():
    content = (
        "1-2\tdedi\t_\t_\t_\t_\t_\t_\t_\t_\n"
        "1\tde\tde\tVERB\t_\t_\t0\troot\t_\t_\n"
        "2\tdi\tdi\tAUX\t_\t_\t1\taux\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, words, _, _ = rows[0]
    assert words == [("de", "VERB"), ("di", "AUX")]


def test_parse_conllu_uses_text_comment_when_present():
    # The standard CoNLL-U way to carry the original sentence -- must be
    # used verbatim (not reconstructed from FORM) since it may include
    # punctuation/spacing that a naive join would get wrong.
    content = (
        "# text = Ev ve bahce, guzeldi.\n"
        "1\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "2\tve\tve\tCCONJ\t_\t_\t1\tcc\t_\t_\n"
        "3\tbahce\tbahce\tNOUN\t_\t_\t1\tconj\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, _, text, _ = rows[0]
    assert text == "Ev ve bahce, guzeldi."


def test_parse_conllu_reconstructs_text_from_form_without_comment():
    # No "# text = " comment -- fall back to joining FORM (raw surface
    # form, not LEMMA) in token order.
    content = (
        "1\tevlerin\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
        "2\tbahcesi\tbahce\tNOUN\t_\t_\t1\tnmod\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, _, text, _ = rows[0]
    assert text == "evlerin bahcesi"


def test_parse_conllu_captures_head_and_deprel():
    # deps must be index-aligned with the returned word list (not the raw
    # token_id, since multiword tokens and non-content words are never
    # dropped from `deps` here -- filtering happens downstream in
    # graph_builder, which needs the full alignment to resolve HEAD
    # references correctly).
    content = (
        "1\tbuyuk\tbuyuk\tADJ\t_\t_\t2\tamod\t_\t_\n"
        "2\tev\tev\tNOUN\t_\t_\t0\troot\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, words, _, deps = rows[0]
    assert words == [("buyuk", "ADJ"), ("ev", "NOUN")]
    assert deps == [("1", "2", "amod"), ("2", "0", "root")]


def test_parse_conllu_deps_empty_when_head_column_missing():
    # A minimal 4-column CoNLL-U-like file (no HEAD/DEPREL) must not
    # crash -- deps just stays empty for that token.
    content = "1\tev\tev\tNOUN\n"
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, _, _, deps = rows[0]
    assert deps == [("1", "", "")]


def test_parse_vrt_uses_lemma_and_pos_when_present():
    # Common VRT convention: word\tlemma\tpos. The raw inflected form used
    # to be the only thing kept; lemma reduces sparsity for agglutinative
    # languages (e.g. Turkish "kitaplar" -> "kitap"), and pos enables
    # content-word filtering.
    content = (
        "<text date=\"2020-01-01\">\n"
        "kitaplar\tkitap\tNOUN\n"
        "ve\tve\tCCONJ\n"
        "kalemler\tkalem\tNOUN\n"
        "</text>\n"
    )
    rows = parse_vrt(content, filename="test.vrt")
    assert len(rows) == 1
    date, words, text, deps = rows[0]
    assert date == "2020-01-01"
    assert words == [("kitap", "NOUN"), ("ve", "CCONJ"), ("kalem", "NOUN")]
    # text preserves the raw surface FORM (column 1), not the lemma --
    # VRT has no raw-text comment, so this is reconstructed from tokens.
    assert text == "kitaplar ve kalemler"
    # VRT never carries dependency annotation.
    assert deps == []


def test_parse_vrt_falls_back_to_word_only_without_extra_columns():
    content = (
        "<text date=\"2020-01-01\">\n"
        "elma\n"
        "armut\n"
        "</text>\n"
    )
    rows = parse_vrt(content, filename="test.vrt")
    assert len(rows) == 1
    _, words, text, deps = rows[0]
    assert words == [("elma", ""), ("armut", "")]
    assert text == "elma armut"
    assert deps == []


def test_parse_tei_word_level_with_namespace():
    # Namespace-aware: TEI files typically declare
    # xmlns="http://www.tei-c.org/ns/1.0", which ElementTree prefixes
    # every tag with -- _local_name() must strip that so <w>/<s>/<date>
    # matching still works.
    content = """<?xml version="1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader><fileDesc><sourceDesc><bibl><date when="2020-01-15"/></bibl></sourceDesc></fileDesc></teiHeader>
  <text><body><div>
    <s><w lemma="yapay" pos="ADJ">yapay</w><w lemma="zeka" pos="NOUN">zeka</w></s>
    <s><w lemma="derin" pos="ADJ">derin</w><w lemma="ogrenme" pos="NOUN">ogrenme</w></s>
  </div></body></text>
</TEI>"""
    rows = parse_tei(content, filename="test.xml")
    assert len(rows) == 2
    date0, words0, text0, deps0 = rows[0]
    # Regression test: a <date> in <teiHeader> (a sibling that comes
    # BEFORE <text>, not an ancestor of the <s> elements) must still
    # reach every sentence -- the recursive walker threads current_date
    # through return values precisely so an update in one subtree isn't
    # silently lost once that recursive call returns.
    assert date0 == "2020-01-15"
    assert words0 == [("yapay", "ADJ"), ("zeka", "NOUN")]
    assert text0 == "yapay zeka"
    assert deps0 == []
    assert rows[1][0] == "2020-01-15"


def test_parse_tei_word_level_without_namespace():
    content = """<TEI>
  <teiHeader><date when="2022-03-01"/></teiHeader>
  <text><body><s><w lemma="test" pos="NOUN">test</w></s></body></text>
</TEI>"""
    rows = parse_tei(content, filename="test.xml")
    assert len(rows) == 1
    assert rows[0][0] == "2022-03-01"
    assert rows[0][1] == [("test", "NOUN")]


def test_parse_tei_falls_back_to_plain_text_without_w_elements():
    content = """<TEI>
  <teiHeader><date when="2021-06-01"/></teiHeader>
  <text><body>
    <p>yapay zeka ve derin ogrenme konusu</p>
    <p>baska bir paragraf metni burada</p>
  </body></text>
</TEI>"""
    rows = parse_tei(content, filename="test.xml")
    assert len(rows) == 2
    for date, words, text, deps in rows:
        assert date == "2021-06-01"  # header date applies to every paragraph
        assert deps == []
        assert all(pos == "" for _word, pos in words)  # no POS at all in plain-text mode
    assert rows[0][2] == "yapay zeka ve derin ogrenme konusu"


def test_parse_tei_unknown_pos_scheme_falls_back_to_empty_pos():
    # A POS tagset other than Universal POS (e.g. Penn Treebank "NN") must
    # NOT be passed through as if it were UPOS -- _is_content_word would
    # then misclassify every single token as a function word. Falling
    # back to pos="" instead degrades to the Turkish-stopword heuristic.
    content = """<TEI>
  <text><body><s><w lemma="ev" pos="NN">ev</w></s></body></text>
</TEI>"""
    rows = parse_tei(content, filename="test.xml")
    assert rows[0][1] == [("ev", "")]


def test_parse_tei_rejects_malformed_xml():
    try:
        parse_tei("<TEI><unclosed>", filename="bad.xml")
        assert False, "expected ValueError for malformed XML"
    except ValueError:
        pass
