from backend.services.graph_utils import build_static_adj, maximal_cliques
from backend.models import GraphSchema, EdgeSchema


def _complete_multipartite(group_count: int, group_size: int) -> dict[str, set[str]]:
    """Moon-Moser worst case: complete multipartite graph with equal-sized
    parts has 3^(n/3) maximal cliques when group_size == 3 -- the classic
    adversarial input for Bron-Kerbosch enumeration."""
    groups = [
        [f"{gi}_{k}" for k in range(group_size)] for gi in range(group_count)
    ]
    vertices = [v for group in groups for v in group]
    edges = []
    for gi in range(len(groups)):
        for gj in range(gi + 1, len(groups)):
            for a in groups[gi]:
                for b in groups[gj]:
                    edges.append(EdgeSchema(u=a, v=b, label=0.0))
    graph = GraphSchema(vertices=vertices, edges=edges)
    return build_static_adj(graph)


def test_maximal_cliques_finds_all_on_small_graph():
    adj = _complete_multipartite(group_count=3, group_size=3)
    cliques, truncated = maximal_cliques(adj, min_size=3)
    assert not truncated
    assert len(cliques) == 3 ** 3
    assert all(len(c) == 3 for c in cliques)


def test_maximal_cliques_has_no_count_based_early_stop():
    # maximal_cliques has no max_cliques param -- an early count-based stop
    # would return arbitrary DFS-order cliques, not the largest ones (see
    # spanner_service.enumerate_cliques for where "top N by size" actually
    # gets applied, over the full enumeration).
    adj = _complete_multipartite(group_count=4, group_size=3)
    cliques, truncated = maximal_cliques(adj, min_size=3)
    assert not truncated
    assert len(cliques) == 3 ** 4


def test_maximal_cliques_budget_bounds_adversarial_search():
    # Without a budget this would enumerate 3^20 (~3.5e9) maximal cliques.
    # The budget must make it return a partial, truncated result quickly
    # instead of hanging.
    adj = _complete_multipartite(group_count=20, group_size=3)
    cliques, truncated = maximal_cliques(adj, min_size=3, budget=10_000)
    assert truncated
    assert len(cliques) < 3 ** 20


def test_maximal_cliques_empty_graph():
    cliques, truncated = maximal_cliques({}, min_size=3)
    assert cliques == []
    assert truncated is False
