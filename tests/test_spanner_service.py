from backend.models import GraphSchema, EdgeSchema
from backend.services.spanner_service import enumerate_cliques


def _clique_edges(vertices):
    edges = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            edges.append(EdgeSchema(u=vertices[i], v=vertices[j], label=0.0))
    return edges


def test_enumerate_cliques_max_cliques_keeps_largest_not_first_found():
    # Regression test: max_cliques used to bound the Bron-Kerbosch search
    # itself, so it returned whichever cliques the DFS traversal reached
    # first -- not the largest. Four disjoint cliques of increasing size
    # are inserted smallest-first, which is exactly the ordering that would
    # have made the old bug return the small cliques instead of the large
    # ones.
    small = [f"s{i}" for i in range(3)]
    medium = [f"m{i}" for i in range(4)]
    large = [f"l{i}" for i in range(5)]
    biggest = [f"b{i}" for i in range(6)]

    vertices = small + medium + large + biggest
    edges = (
        _clique_edges(small)
        + _clique_edges(medium)
        + _clique_edges(large)
        + _clique_edges(biggest)
    )
    graph = GraphSchema(vertices=vertices, edges=edges)

    cliques, truncated = enumerate_cliques(graph, min_clique_size=3, max_cliques=2)

    sizes = sorted((len(c) for c in cliques), reverse=True)
    assert sizes == [6, 5]
    # max_cliques discarded 2 real (smaller) cliques, so this is a
    # meaningful "results narrowed by request" signal, not just a
    # search-budget hit.
    assert truncated


def test_enumerate_cliques_max_cliques_zero_means_unbounded():
    small = [f"s{i}" for i in range(3)]
    biggest = [f"b{i}" for i in range(6)]
    graph = GraphSchema(
        vertices=small + biggest,
        edges=_clique_edges(small) + _clique_edges(biggest),
    )

    cliques, truncated = enumerate_cliques(graph, min_clique_size=3, max_cliques=0)

    assert not truncated
    assert sorted((len(c) for c in cliques), reverse=True) == [6, 3]
