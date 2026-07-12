import csv
import io
import os
from xml.sax.saxutils import escape as xml_escape

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from backend.models import SpannerRequest, SpannerResponse, UploadResponse
from backend.services.graph_builder import parse_csv, parse_json, parse_corpus_rows
from backend.services.corpus_parser import detect_and_parse
from backend.services.spanner_service import build_spanner_response, enumerate_cliques

router = APIRouter()

# NPMI is bounded to [-1, 1] (see graph_builder._compute_pmi); 0.15 is a
# small positive floor that drops chance-level and weakly-associated pairs
# while keeping real collocations. Actually wired to /api/upload's
# pmi_threshold form field below -- it used to be a hardcoded constant that
# silently ignored whatever the request sent.
PMI_THRESHOLD_DEFAULT = 0.15
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))


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
    pmi_threshold: float = Form(PMI_THRESHOLD_DEFAULT, ge=-1.0, le=1.0),
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
            graph, dates, rows_parsed, stopwords_filtered = parse_corpus_rows(
                rows, pmi_threshold=pmi_threshold
            )
        elif is_json:
            graph, dates, rows_parsed, stopwords_filtered = parse_json(
                content, pmi_threshold=pmi_threshold
            )
        else:
            graph, dates, rows_parsed, stopwords_filtered = parse_csv(
                content, pmi_threshold=pmi_threshold
            )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return UploadResponse(
        graph=graph,
        rows_parsed=rows_parsed,
        time_range=[min(dates), max(dates)] if dates else ["", ""],
        stopwords_filtered=stopwords_filtered,
        pmi_threshold=pmi_threshold,
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
