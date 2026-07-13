from bisect import bisect_left
from backend.models import (
    GraphSchema,
    CliqueSnapshot,
    CliqueTimeline,
    TrendResponse,
)
from backend.services.graph_builder import compute_npmi
from backend.services.graph_utils import maximal_cliques


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _window_bounds(t_min: float, t_max: float, step: float, windows: int, w: int) -> tuple[float, float]:
    ws = t_min + w * step
    we = ws + step if w < windows - 1 else t_max + 0.001
    return ws, we


def _windows_from_global_graph(
    graph: GraphSchema, windows: int
) -> tuple[float, float, float, list[int], list[list[set[str]]], bool]:
    """Original approach: slice the one corpus-global NPMI-filtered edge
    set by the window each edge's document date falls in. A pair's
    presence here was decided once, from the whole corpus's statistics --
    see raw-documents variant below for the per-window recomputation."""
    sorted_edges = sorted(graph.edges, key=lambda e: e.label)
    edge_labels = [e.label for e in sorted_edges]

    t_min = edge_labels[0]
    t_max = edge_labels[-1]
    if t_max == t_min:
        t_max = t_min + 1.0
    step = (t_max - t_min) / windows

    window_edges: list[int] = []
    window_cliques: list[list[set[str]]] = []
    any_truncated = False

    for w in range(windows):
        ws, we = _window_bounds(t_min, t_max, step, windows, w)

        start_idx = bisect_left(edge_labels, ws)
        end_idx = bisect_left(edge_labels, we)

        v_set: set[str] = set()
        e_list: list[tuple[str, str]] = []
        for e in sorted_edges[start_idx:end_idx]:
            v_set.add(e.u)
            v_set.add(e.v)
            e_list.append((e.u, e.v))

        window_edges.append(len(e_list))

        window_adj: dict[str, set[str]] = {v: set() for v in v_set}
        for u, v in e_list:
            window_adj[u].add(v)
            window_adj[v].add(u)

        cliques, truncated = maximal_cliques(window_adj, min_size=2)
        any_truncated = any_truncated or truncated
        window_cliques.append(cliques)

    return t_min, t_max, step, window_edges, window_cliques, any_truncated


def _windows_from_raw_documents(
    raw_documents: list[tuple[float, list[str]]], windows: int, pmi_threshold: float
) -> tuple[float, float, float, list[int], list[list[set[str]]], bool]:
    """Recomputes NPMI independently within each time window's own
    documents, instead of slicing a single corpus-global edge set. A pair
    can be strongly significant in one window and never clear the global
    threshold (diluted by the rest of the corpus), or vice versa -- this
    is the only way to surface that."""
    docs_sorted = sorted(raw_documents, key=lambda d: d[0])
    doc_labels = [d[0] for d in docs_sorted]
    doc_words = [d[1] for d in docs_sorted]

    t_min = doc_labels[0]
    t_max = doc_labels[-1]
    if t_max == t_min:
        t_max = t_min + 1.0
    step = (t_max - t_min) / windows

    window_edges: list[int] = []
    window_cliques: list[list[set[str]]] = []
    any_truncated = False

    for w in range(windows):
        ws, we = _window_bounds(t_min, t_max, step, windows, w)

        start_idx = bisect_left(doc_labels, ws)
        end_idx = bisect_left(doc_labels, we)
        window_docs = doc_words[start_idx:end_idx]

        npmi = compute_npmi(window_docs)
        window_adj: dict[str, set[str]] = {}
        edge_count = 0
        for (u, v), score in npmi.items():
            if score >= pmi_threshold:
                window_adj.setdefault(u, set()).add(v)
                window_adj.setdefault(v, set()).add(u)
                edge_count += 1

        window_edges.append(edge_count)

        cliques, truncated = maximal_cliques(window_adj, min_size=2)
        any_truncated = any_truncated or truncated
        window_cliques.append(cliques)

    return t_min, t_max, step, window_edges, window_cliques, any_truncated


def compute_trends(
    graph: GraphSchema,
    windows: int = 10,
    raw_documents: list[tuple[float, list[str]]] | None = None,
    pmi_threshold: float = 0.15,
) -> TrendResponse:
    if raw_documents:
        t_min, t_max, step, window_edges, window_cliques, any_truncated = (
            _windows_from_raw_documents(raw_documents, windows, pmi_threshold)
        )
    else:
        if not graph.edges:
            return TrendResponse(timelines=[], time_range=[0, 0], window_edges=[], truncated=False)
        t_min, t_max, step, window_edges, window_cliques, any_truncated = (
            _windows_from_global_graph(graph, windows)
        )

    timelines: list[CliqueTimeline] = []
    next_id = 0

    for w, cliques in enumerate(window_cliques):
        ws, we = _window_bounds(t_min, t_max, step, windows, w)

        pre_existing = len(timelines)
        matched: set[int] = set()
        active_timelines = [(i, tl) for i, tl in enumerate(timelines) if tl.death is None]
        last_snap_sets = [(i, tl, set(tl.snapshots[-1].members)) for i, tl in active_timelines]

        for c in cliques:
            best_idx = -1
            best_tl = None
            best_score = 0.0
            c_set = c
            for idx, tl, snap_set in last_snap_sets:
                score = _jaccard(c_set, snap_set)
                if score > best_score:
                    best_score = score
                    best_tl = tl
                    best_idx = idx

            if best_tl and best_score >= 0.25:
                matched.add(best_idx)
                best_tl.snapshots.append(
                    CliqueSnapshot(
                        window=w,
                        window_start=round(ws, 4),
                        window_end=round(we, 4),
                        members=sorted(c),
                        size=len(c),
                    )
                )
                best_tl.max_size = max(best_tl.max_size, len(c))
            else:
                tl = CliqueTimeline(
                    id=f"c{next_id}",
                    label=f"Clique {next_id}",
                    birth=ws,
                    death=None,
                    snapshots=[
                        CliqueSnapshot(
                            window=w,
                            window_start=round(ws, 4),
                            window_end=round(we, 4),
                            members=sorted(c),
                            size=len(c),
                        )
                    ],
                    max_size=len(c),
                )
                timelines.append(tl)
                next_id += 1

        if w < windows - 1:
            for i in range(pre_existing):
                tl = timelines[i]
                if tl.death is None and i not in matched:
                    tl.death = ws

    # A size-2 clique (a single co-occurring word pair) that only ever
    # shows up in one window never demonstrated any persistence -- it's
    # co-occurrence noise, not an evolving concept. Real corpora produce
    # hundreds of these, drowning out the timelines that actually show
    # birth/growth/death. Keep a timeline if it either persisted across
    # more than one window, or was a genuinely larger clique (>=3 members)
    # even when only observed once.
    meaningful_timelines = [
        tl for tl in timelines
        if len(tl.snapshots) > 1 or tl.max_size >= 3
    ]

    return TrendResponse(
        timelines=meaningful_timelines,
        time_range=[round(t_min, 4), round(t_max, 4)],
        window_edges=window_edges,
        truncated=any_truncated,
    )
