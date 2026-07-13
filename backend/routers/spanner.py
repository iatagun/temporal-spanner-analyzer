import csv
import io
import os
from xml.sax.saxutils import escape as xml_escape

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from backend.models import SpannerRequest, SpannerResponse, UploadResponse, RawDocumentSchema, AssociationMeasure
from backend.services.graph_builder import parse_csv, parse_json, parse_corpus_rows
from backend.services.corpus_parser import detect_and_parse
from backend.services.spanner_service import build_spanner_response, enumerate_cliques

router = APIRouter()

# NPMI is bounded to [-1, 1] (see graph_builder.compute_npmi); 0.15 is a
# small positive floor that drops chance-level and weakly-associated pairs
# while keeping real collocations. Actually wired to /api/upload's
# pmi_threshold form field below -- it used to be a hardcoded constant that
# silently ignored whatever the request sent. Only a sane default for the
# "npmi" measure -- other measures (log-likelihood/dice/t_score) have
# their own scale and default, applied client-side when the measure changes.
# Raised from 5MB after measuring real upload+trends timing on synthetic
# CoNLL-U corpora up to 27MB (Render's free plan is 512MB RAM -- this
# isn't "how much can the box hold" but "how much can a single request
# still feel responsive"). /api/upload itself stays fast even at 27MB
# (~10s) once graph_builder dedups per-pair scores across edge
# occurrences (see _words_to_edges_filtered) -- the real ceiling is
# /api/trends' per-window association-measure recompute, whose cost grows
# faster than corpus size (bounded by vocabulary-squared as more documents
# saturate the same word pairs): 1.4MB->99ms, 5.4MB->2.8s, 11MB->13.5s.
# 10MB keeps that well under ~5s while giving real corpora meaningfully
# more room than 5MB; corpora that lean heavily on /api/trends with a
# narrow, densely-repeating vocabulary may still want to stay smaller.
# See CLAUDE.md's "Büyük derlem" note.
PMI_THRESHOLD_DEFAULT = 0.15
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))


@router.post("/spanner")
def compute_spanner(req: SpannerRequest) -> SpannerResponse:
    cliques, truncated = enumerate_cliques(
        req.graph, min_clique_size=req.min_clique_size, max_cliques=req.max_cliques
    )
    return build_spanner_response(req.graph, cliques, truncated)


def _read_upload_bounded(file: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    chunk_size = 1024 * 1024
    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                413,
                f"File exceeds the {max_bytes // (1024 * 1024)}MB upload limit",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/upload", response_model=UploadResponse)
def upload_csv(
    file: UploadFile = File(...),
    pmi_threshold: float = Form(PMI_THRESHOLD_DEFAULT, ge=-1000.0, le=1000.0),
    association_measure: AssociationMeasure = Form("npmi"),
    collocation_mode: str = Form("window"),
    lemmatize: bool = Form(False),
):
    if not file.filename:
        raise HTTPException(400, "File is required")

    content = _read_upload_bounded(file, MAX_UPLOAD_BYTES)
    ext = file.filename.lower()

    is_json = ext.endswith(".json")
    is_csv = ext.endswith(".csv")
    is_corpus = ext.endswith(".conllu") or ext.endswith(".conll") or ext.endswith(".vrt")

    if not is_csv and not is_json and not is_corpus:
        raise HTTPException(
            400,
            "Only CSV, JSON, CoNLL-U (.conllu/.conll), and VRT (.vrt) files are supported",
        )

    # Syntactic (dependency-based) collocation needs HEAD/DEPREL, which
    # only CoNLL-U carries -- reject it upfront for other formats instead
    # of silently falling back to window mode (parse_corpus_rows itself
    # rejects a CoNLL-U file with no dependency info at all, e.g. VRT never
    # reaches it in the first place since it's routed through here too).
    if collocation_mode == "syntactic" and not ext.endswith((".conllu", ".conll")):
        raise HTTPException(
            400,
            "collocation_mode=syntactic requires a CoNLL-U file (HEAD/DEPREL columns); "
            "VRT/CSV/JSON have no dependency information.",
        )

    try:
        if is_corpus:
            content_str = content.decode("utf-8-sig")
            rows, fmt, meta = detect_and_parse(content_str, file.filename)
            if not rows:
                raise ValueError(
                    f"No valid rows found in {fmt} file. "
                    "CoNLL-U: tab-separated columns with word/lemma in column 2/3. "
                    "VRT: <text> tags with tab-separated word lines."
                )
            graph, dates, rows_parsed, stopwords_filtered, documents = parse_corpus_rows(
                rows, pmi_threshold=pmi_threshold, measure=association_measure,
                collocation_mode=collocation_mode,
            )
        elif is_json:
            graph, dates, rows_parsed, stopwords_filtered, documents = parse_json(
                content, pmi_threshold=pmi_threshold, measure=association_measure, lemmatize=lemmatize
            )
        else:
            graph, dates, rows_parsed, stopwords_filtered, documents = parse_csv(
                content, pmi_threshold=pmi_threshold, measure=association_measure, lemmatize=lemmatize
            )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return UploadResponse(
        graph=graph,
        rows_parsed=rows_parsed,
        time_range=[min(dates), max(dates)] if dates else ["", ""],
        stopwords_filtered=stopwords_filtered,
        pmi_threshold=pmi_threshold,
        association_measure=association_measure,
        raw_documents=[
            RawDocumentSchema(label=label, words=words, text=text) for label, words, text in documents
        ],
    )


@router.post("/export")
def export_graph(req: SpannerRequest, fmt: str = "json"):
    if fmt == "json":
        return Response(
            content=req.graph.model_dump_json(indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=graph.json"
            },
        )
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["source", "target", "label"])
        for e in req.graph.edges:
            writer.writerow([e.u, e.v, e.label])
        return Response(
            content=buf.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=graph.csv"},
        )
    elif fmt == "graphml":
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <key id="d0" for="edge" attr.name="label" attr.type="double"/>',
            '  <graph edgedefault="undirected">',
        ]
        for v in req.graph.vertices:
            lines.append(f'    <node id="{xml_escape(v, {chr(34): "&quot;"})}"/>')
        for i, e in enumerate(req.graph.edges):
            u = xml_escape(e.u, {chr(34): "&quot;"})
            v = xml_escape(e.v, {chr(34): "&quot;"})
            lines.append(f'    <edge id="e{i}" source="{u}" target="{v}">')
            lines.append(f'      <data key="d0">{xml_escape(str(e.label))}</data>')
            lines.append("    </edge>")
        lines.append("  </graph>")
        lines.append("</graphml>")
        return Response(
            content="\n".join(lines),
            media_type="application/xml",
            headers={
                "Content-Disposition": "attachment; filename=graph.graphml"
            },
        )
    raise HTTPException(400, f"Unsupported format: {fmt}")
