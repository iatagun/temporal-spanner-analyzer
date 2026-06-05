from __future__ import annotations

from backend.models import GraphSchema


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
    adj: dict[str, set[str]], min_size: int = 3
) -> list[set[str]]:
    cliques: list[set[str]] = []

    def bk(R: set[str], P: set[str], X: set[str]):
        if not P and not X:
            if len(R) >= min_size:
                cliques.append(set(R))
            return
        pivot = next(iter(P | X))
        for v in list(P - adj[pivot]):
            bk(R | {v}, P & adj[v], X & adj[v])
            P.remove(v)
            X.add(v)

    bk(set(), set(adj.keys()), set())
    return cliques
