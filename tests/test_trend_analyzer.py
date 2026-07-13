from backend.models import GraphSchema, EdgeSchema
from backend.services.trend_analyzer import compute_trends


def test_compute_trends_drops_single_snapshot_pairs_but_keeps_larger_cliques():
    # A pair (2-word clique) seen in exactly one window is co-occurrence
    # noise -- it never showed any persistence. A triangle (3-word clique)
    # seen once is still a real, meaningful clique even if short-lived.
    # A pair seen across two (adjacent) windows is a genuine, if small,
    # timeline -- the timeline-matching logic only bridges consecutive
    # windows, so with windows=2 "label 0.0" and "label 1.0" fall one in
    # each of the two windows with no gap between them.
    edges = [
        # "a"-"b": appears only in the first window -> should be dropped.
        EdgeSchema(u="a", v="b", label=0.0),

        # "c"-"d": appears in both windows -> persists, kept even though
        # it's only ever a pair.
        EdgeSchema(u="c", v="d", label=0.0),
        EdgeSchema(u="c", v="d", label=1.0),

        # "e"-"f"-"g": a real triangle, only in the first window -> kept
        # because max_size >= 3 even with a single snapshot.
        EdgeSchema(u="e", v="f", label=0.0),
        EdgeSchema(u="e", v="g", label=0.0),
        EdgeSchema(u="f", v="g", label=0.0),
    ]
    graph = GraphSchema(vertices=["a", "b", "c", "d", "e", "f", "g"], edges=edges)

    trend = compute_trends(graph, windows=2)

    member_sets = [frozenset(m for s in tl.snapshots for m in s.members) for tl in trend.timelines]
    assert frozenset({"a", "b"}) not in member_sets
    assert frozenset({"c", "d"}) in member_sets
    assert frozenset({"e", "f", "g"}) in member_sets


def test_compute_trends_empty_graph_has_no_timelines():
    graph = GraphSchema(vertices=[], edges=[])
    trend = compute_trends(graph, windows=10)
    assert trend.timelines == []


def test_compute_trends_with_raw_documents_ignores_graph_edges():
    # With raw_documents supplied, compute_trends must recompute NPMI
    # independently per window instead of slicing graph.edges at all --
    # proven by passing a graph with NO edges whatsoever. Any clique in
    # the result can only have come from the per-window NPMI recompute.
    raw_documents = [
        (0.0, ["x", "y", "z"]),
        (0.0, ["x", "y", "z"]),
        (0.0, ["x", "y", "z"]),
        (1.0, ["a", "b"]),
        (1.0, ["a", "b"]),
    ]
    graph = GraphSchema(vertices=["x", "y", "z", "a", "b"], edges=[])

    trend = compute_trends(graph, windows=2, raw_documents=raw_documents, pmi_threshold=0.5)

    member_sets = [frozenset(m for s in tl.snapshots for m in s.members) for tl in trend.timelines]
    assert frozenset({"x", "y", "z"}) in member_sets
    # "a"-"b" is a single-window 2-clique -- noise, dropped same as the
    # graph-slicing path.
    assert frozenset({"a", "b"}) not in member_sets


def test_compute_trends_raw_documents_pmi_threshold_gates_local_significance():
    # "x" co-occurs with a different word in nearly every document, so no
    # pair ever repeats (codf=1 < the compute_npmi default min_codf=2) --
    # this proves the per-window recompute isn't bypassing NPMI/min_codf
    # filtering, not just accepting every co-occurring pair in a window.
    raw_documents = [
        (0.0, ["x", "y"]),
        (0.0, ["x", "p"]),
        (0.0, ["x", "q"]),
        (0.0, ["x", "r"]),
    ]
    graph = GraphSchema(vertices=["x", "y", "p", "q", "r"], edges=[])
    trend = compute_trends(graph, windows=1, raw_documents=raw_documents, pmi_threshold=0.15)
    assert trend.timelines == []


def test_compute_trends_raw_documents_respects_selected_measure():
    # A pair present in literally every document of a window is NPMI's
    # (and Dice's) maximal case (1.0) but log-likelihood's *minimal* case
    # (0.0 -- no deviation from independence to detect when there's no
    # variation in the sample). If `measure` weren't actually threaded
    # into the per-window recompute, this would silently keep using NPMI
    # regardless of what the caller asked for.
    raw_documents = [
        (0.0, ["x", "y", "z"]),
        (0.0, ["x", "y", "z"]),
        (0.0, ["x", "y", "z"]),
    ]
    graph = GraphSchema(vertices=["x", "y", "z"], edges=[])

    trend_npmi = compute_trends(
        graph, windows=1, raw_documents=raw_documents, pmi_threshold=0.5, measure="npmi"
    )
    trend_ll = compute_trends(
        graph, windows=1, raw_documents=raw_documents, pmi_threshold=0.5, measure="log_likelihood"
    )

    npmi_members = [frozenset(m for s in tl.snapshots for m in s.members) for tl in trend_npmi.timelines]
    assert frozenset({"x", "y", "z"}) in npmi_members
    assert trend_ll.timelines == []  # log-likelihood is 0.0 here, below the 0.5 gate


def test_compute_trends_picks_best_jaccard_match_among_several_candidates():
    # Regression test for the inverted-index candidate generation in the
    # timeline-matching loop (added to fix a measured O(cliques x
    # timelines) _jaccard blowup): with THREE active timelines of varying
    # overlap with a new clique -- {a,b,c} (high overlap), {a,b,d}
    # (partial overlap), {x,y} (zero overlap) -- the new {a,b,c,e} clique
    # must still match the genuinely best one ({a,b,c}, Jaccard 0.75),
    # not just whichever the index happens to list first, and the
    # zero-overlap timeline must correctly die rather than falsely match.
    edges_w0 = [
        EdgeSchema(u="a", v="b", label=0.0),
        EdgeSchema(u="a", v="c", label=0.0),
        EdgeSchema(u="b", v="c", label=0.0),
        EdgeSchema(u="a", v="d", label=0.0),
        EdgeSchema(u="b", v="d", label=0.0),
        EdgeSchema(u="x", v="y", label=0.0),
    ]
    edges_w1 = [
        EdgeSchema(u="a", v="b", label=1.0),
        EdgeSchema(u="a", v="c", label=1.0),
        EdgeSchema(u="a", v="e", label=1.0),
        EdgeSchema(u="b", v="c", label=1.0),
        EdgeSchema(u="b", v="e", label=1.0),
        EdgeSchema(u="c", v="e", label=1.0),
    ]
    graph = GraphSchema(vertices=["a", "b", "c", "d", "e", "x", "y"], edges=edges_w0 + edges_w1)

    trend = compute_trends(graph, windows=2)

    # The {a,b,c} timeline must have grown to include "e" in window 1.
    extended = [tl for tl in trend.timelines if frozenset(tl.snapshots[0].members) == frozenset({"a", "b", "c"})]
    assert len(extended) == 1
    assert frozenset(extended[0].snapshots[-1].members) == frozenset({"a", "b", "c", "e"})
    assert extended[0].death is None

    # {a,b,d} (a triangle, survives the noise filter on its own via
    # max_size>=3) must NOT have matched the new clique -- it stays at
    # just its single window-0 snapshot (death isn't set for timelines
    # unmatched in the LAST window -- there's no subsequent window to
    # trigger that check -- so snapshot count is the meaningful signal
    # here, not the `death` field).
    abd = next(t for t in trend.timelines if frozenset(t.snapshots[0].members) == frozenset({"a", "b", "d"}))
    assert len(abd.snapshots) == 1

    # {x,y} is a plain pair with zero overlap with the new clique -- it
    # neither matches nor merges into anything, and (being a single-
    # snapshot pair) gets dropped entirely by the final noise filter.
    all_members = [frozenset(m for s in tl.snapshots for m in s.members) for tl in trend.timelines]
    assert frozenset({"x", "y"}) not in all_members


def test_compute_trends_empty_raw_documents_falls_back_to_graph_slicing():
    # An empty raw_documents list (e.g. an older client that doesn't send
    # them) must fall back to the original graph-edge-slicing behavior,
    # not silently produce no timelines at all.
    edges = [EdgeSchema(u="c", v="d", label=0.0), EdgeSchema(u="c", v="d", label=1.0)]
    graph = GraphSchema(vertices=["c", "d"], edges=edges)
    trend = compute_trends(graph, windows=2, raw_documents=[])
    member_sets = [frozenset(m for s in tl.snapshots for m in s.members) for tl in trend.timelines]
    assert frozenset({"c", "d"}) in member_sets
