from __future__ import annotations

from backend.models import GraphSchema

# Bron-Kerbosch enumerates *all* maximal cliques, which is worst-case
# exponential in graph density (Moon-Moser: up to 3^(n/3) cliques). A dense
# upload (e.g. a small vocabulary co-occurring in every time window) can
# otherwise make the recursion run for an unbounded amount of time. The
# budget below caps the number of recursive calls so a pathological graph
# degrades gracefully (partial, `truncated=True` result) instead of hanging
# the request. Tuned so realistic corpus-sized graphs (a few hundred
# vertices, moderate density) finish well under the cap.
DEFAULT_SEARCH_BUDGET = 500_000


def edge_key(u: str, v: str) -> tuple[str, str]:
    return (u, v) if u <= v else (v, u)


def build_static_adj(graph: GraphSchema) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {}
    for v in graph.vertices:
        adj[v] = set()
    for e in graph.edges:
        adj[e.u].add(e.v)
        adj[e.v].add(e.u)
    return adj


def maximal_cliques(
    adj: dict[str, set[str]],
    min_size: int = 3,
    max_cliques: int = 0,
    budget: int = DEFAULT_SEARCH_BUDGET,
) -> tuple[list[set[str]], bool]:
    """Enumerate maximal cliques of size >= min_size via Bron-Kerbosch
    (Tomita pivot). Returns (cliques, truncated) — truncated is True when
    the search stopped early because it hit `max_cliques` results or the
    recursive-call `budget`, meaning the result is a partial (but still
    valid) set of maximal cliques rather than the complete enumeration.
    """
    cliques: list[set[str]] = []
    state = {"truncated": False, "calls": 0}
    if not adj:
        return cliques, False

    def bk(R: set[str], P: set[str], X: set[str]):
        if state["truncated"]:
            return
        state["calls"] += 1
        if state["calls"] > budget:
            state["truncated"] = True
            return
        if max_cliques > 0 and len(cliques) >= max_cliques:
            state["truncated"] = True
            return
        if len(R) + len(P) < min_size:
            return
        if not P and not X:
            if len(R) >= min_size:
                cliques.append(set(R))
            return
        pivot = max(P | X, key=lambda v: len(adj[v] & P))
        for v in list(P - adj[pivot]):
            bk(R | {v}, P & adj[v], X & adj[v])
            if state["truncated"]:
                return
            P.remove(v)
            X.add(v)

    bk(set(), set(adj.keys()), set())
    return cliques, state["truncated"]
