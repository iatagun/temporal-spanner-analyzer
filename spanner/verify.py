from __future__ import annotations
from spanner.types import TemporalGraph, VertexID
from spanner.core import (
    exists_temporal_path_in_subgraph,
    random_temporal_clique,
    spanner_for_clique,
)

ALLOW_LESS = True  # spanner may also be smaller than 7n


class VerificationError(AssertionError):
    pass


def verify_spanner(G: TemporalGraph, E_spanner: set[tuple[VertexID, VertexID]], max_allowed: int) -> bool:
    if not ALLOW_LESS and len(E_spanner) > max_allowed:
        raise VerificationError(
            f"Size {len(E_spanner)} exceeds {max_allowed}"
        )
    for u in G.V:
        for v in G.V:
            if u == v:
                continue
            if not exists_temporal_path_in_subgraph(u, v, E_spanner, G):
                raise VerificationError(
                    f"No temporal path between {u} and {v} in spanner"
                )
    return True


def run_test(n: int, trials: int = 5, seed_base: int = 42) -> None:
    for t in range(trials):
        G = random_temporal_clique(n, seed=seed_base + t)
        E = spanner_for_clique(G)
        bound = 7 * n
        try:
            verify_spanner(G, E, bound)
            ratio = len(E) / n
            savings = 1 - len(E) / (n * (n - 1) // 2)
            status = "OK"
        except VerificationError as e:
            status = f"FAIL: {e}"
            ratio = float("nan")
            savings = float("nan")
        print(f"  trial {t + 1}: |E|={len(E):>5}, 7n={bound:>5}, |E|/n={ratio:.2f}, "
              f"savings={savings:.1%}  [{status}]")


def run_all_tests():
    for n in [4, 6, 8, 10, 20, 50]:
        print(f"\nn = {n}")
        run_test(n, trials=3, seed_base=n * 100)


if __name__ == "__main__":
    run_all_tests()
