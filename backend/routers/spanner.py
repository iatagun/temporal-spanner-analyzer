import csv
import io
import os
from collections import deque
from xml.sax.saxutils import escape as xml_escape

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from backend.models import (
    SpannerRequest,
    SpannerResponse,
    GraphSchema,
    EdgeSchema,
    MetricSchema,
    UploadResponse,
)
from backend.services.graph_builder import parse_csv, parse_json, parse_corpus_rows
from backend.services.corpus_parser import detect_and_parse
from backend.services.spanner_service import compute_spanner_pipeline

router = APIRouter()

# NPMI is bounded to [-1, 1] (see graph_builder._compute_pmi); 0.15 is a
# small positive floor that drops chance-level and weakly-associated pairs
# while keeping real collocations. Actually wired to /api/upload's
# pmi_threshold form field below -- it used to be a hardcoded constant that
# silently ignored whatever the request sent.
PMI_THRESHOLD_DEFAULT = 0.15
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))


def _shortest_temporal_path_len(
    start: str, end: str, edges: list[tuple[str, str, float]]
) -> int | None:
    adj: dict[str, list[tuple[str, float]]] = {}
    for u, v, l in edges:
        if u == v:
            continue
        adj.setdefault(u, []).append((v, l))
        adj.setdefault(v, []).append((u, l))
    q: deque[tuple[str, float, int]] = deque()
    q.append((start, -float("inf"), 0))
    visited: set[tuple[str, float]] = {(start, -float("inf"))}
    while q:
        v, last_lbl, dist = q.popleft()
        if v == end:
            return dist
        for w, l in adj.get(v, []):
            if l >= last_lbl and (w, l) not in visited:
                visited.add((w, l))
                q.append((w, l, dist + 1))
    return None


def _compute_stretch_factor(
    lbl: dict,
    E_spanner: set[tuple[str, str]],
    clique_pairs: set[tuple[str, str]],
) -> float:
    all_edges = [
        (a, b, lbl.get((a, b) if a <= b else (b, a), 0.0))
        for a, b in E_spanner
    ]
    orig_edges = [
        (u, v, lbl[(u, v) if u <= v else (v, u)])
        for u, v in lbl
    ]

    pairs = sorted(clique_pairs)
    if len(pairs) > 50:
        pairs = pairs[:50]

    total_ratio = 0.0
    pairs_checked = 0

    for u, v in pairs:
        d_orig = _shortest_temporal_path_len(u, v, orig_edges)
        d_spanner = _shortest_temporal_path_len(u, v, all_edges)
        if d_orig and d_orig > 0:
            if d_spanner is None:
                continue
            total_ratio += d_spanner / d_orig
            pairs_checked += 1

    return round(total_ratio / max(pairs_checked, 1), 2)


@router.post("/spanner")
def compute_spanner(req: SpannerRequest) -> SpannerResponse:
    V = set(req.graph.vertices)
    n = len(V)

    if n < 2:
        return SpannerResponse(
            original=req.graph,
            spanner=GraphSchema(vertices=sorted(V, key=str), edges=[]),
            cliques=[],
            metrics=MetricSchema(
                uploaded_edges=len(req.graph.edges),
                full_clique_edges=0,
                spanner_edges=0,
                bound_7n=0,
                ratio_per_n=0.0,
                savings_pct=0.0,
                verified=True,
                stretch_factor=1.0,
            ),
        )

    lbl, max_label, cliques, all_spanner_edges, clique_qualities, clique_pairs, truncated = (
        compute_spanner_pipeline(req.graph, min_clique_size=req.min_clique_size, max_cliques=req.max_cliques)
    )

    uploaded_count = len(req.graph.edges)
    spanner_count = len(all_spanner_edges)

    vertices_in_cliques: set[str] = set()
    for c in cliques:
        vertices_in_cliques.update(c)
    n_covered = len(vertices_in_cliques)
    bound = 7 * max(n_covered, 1)
    for v in V:
        if v not in vertices_in_cliques:
            bound += 1

    verified_results = [cq.verified for cq in clique_qualities] if clique_qualities else []
    if not verified_results:
        all_verified = None
    elif all(v is None for v in verified_results):
        all_verified = None
    else:
        all_verified = all(v for v in verified_results if v is not None)

    spanner_edges_out = [
        EdgeSchema(u=a, v=b, label=lbl.get((a, b) if a <= b else (b, a), 0.0))
        for a, b in all_spanner_edges
    ]

    savings_base = max(uploaded_count, 1)
    savings = round((1 - spanner_count / savings_base) * 100, 1)

    stretch = (
        _compute_stretch_factor(lbl, all_spanner_edges, clique_pairs)
        if spanner_count > 0 and clique_pairs
        else 1.0
    )

    return SpannerResponse(
        original=req.graph,
        spanner=GraphSchema(
            vertices=sorted(V, key=str),
            edges=spanner_edges_out,
        ),
        cliques=[sorted(c) for c in cliques],
        metrics=MetricSchema(
            uploaded_edges=uploaded_count,
            full_clique_edges=len(lbl),
            spanner_edges=spanner_count,
            bound_7n=bound,
            ratio_per_n=round(spanner_count / max(n, 1), 2),
            savings_pct=savings,
            verified=all_verified,
            stretch_factor=stretch,
            cliques_processed=len(cliques),
            clique_qualities=clique_qualities,
            truncated=truncated,
        ),
    )


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
    pmi_threshold: float = Form(PMI_THRESHOLD_DEFAULT),
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
