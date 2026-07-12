from bisect import bisect_left, bisect_right
from backend.models import (
    GraphSchema,
    CliqueSnapshot,
    CliqueTimeline,
    TrendResponse,
)
from backend.services.graph_utils import build_static_adj, maximal_cliques


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def compute_trends(graph: GraphSchema, windows: int = 10) -> TrendResponse:
    if not graph.edges:
        return TrendResponse(timelines=[], time_range=[0, 0], window_edges=[], truncated=False)

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
        ws = t_min + w * step
        we = ws + step if w < windows - 1 else t_max + 0.001

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

    timelines: list[CliqueTimeline] = []
    next_id = 0

    for w, cliques in enumerate(window_cliques):
        ws = t_min + w * step
        we = ws + step if w < windows - 1 else t_max + 0.001

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

    return TrendResponse(
        timelines=timelines,
        time_range=[round(t_min, 4), round(t_max, 4)],
        window_edges=window_edges,
        truncated=any_truncated,
    )
