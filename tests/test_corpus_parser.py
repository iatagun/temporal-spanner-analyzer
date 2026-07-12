from backend.services.corpus_parser import parse_conllu, parse_vrt


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
    date, words = rows[0]
    assert words == [("ev", "NOUN"), ("ve", "CCONJ"), ("bahce", "NOUN")]


def test_parse_conllu_multiword_tokens_skipped():
    content = (
        "1-2\tdedi\t_\t_\t_\t_\t_\t_\t_\t_\n"
        "1\tde\tde\tVERB\t_\t_\t0\troot\t_\t_\n"
        "2\tdi\tdi\tAUX\t_\t_\t1\taux\t_\t_\n"
    )
    rows = parse_conllu(content, filename="test.conllu")
    assert len(rows) == 1
    _, words = rows[0]
    assert words == [("de", "VERB"), ("di", "AUX")]


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
    date, words = rows[0]
    assert date == "2020-01-01"
    assert words == [("kitap", "NOUN"), ("ve", "CCONJ"), ("kalem", "NOUN")]


def test_parse_vrt_falls_back_to_word_only_without_extra_columns():
    content = (
        "<text date=\"2020-01-01\">\n"
        "elma\n"
        "armut\n"
        "</text>\n"
    )
    rows = parse_vrt(content, filename="test.vrt")
    assert len(rows) == 1
    _, words = rows[0]
    assert words == [("elma", ""), ("armut", "")]
