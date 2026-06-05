import sys
import time
from spanner.core import random_temporal_clique, spanner_for_clique
from spanner.verify import verify_spanner, VerificationError


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print(f"=== Temporal Clique Spanner (Baligács 2026) ===")
    print(f"n = {n}, seed = {seed}")
    print(f"Full clique edges: {n * (n - 1) // 2}")
    print(f"7n bound: {7 * n}")
    print()

    t0 = time.time()
    G = random_temporal_clique(n, seed=seed)
    E = spanner_for_clique(G)
    elapsed = time.time() - t0

    try:
        verify_spanner(G, E, 7 * n)
        savings = 1 - len(E) / (n * (n - 1) // 2)
        print(f"Spanner size:  |E| = {len(E)}")
        print(f"Ratio:         |E|/n = {len(E)/n:.2f}")
        print(f"Savings:       {savings:.1%} vs full clique")
        print(f"Time:          {elapsed:.2f}s")
        print()
        ok = len(E) <= 7 * n
        print(f"Bound:         |E| <= 7n = {7 * n}  {'OK' if ok else 'FAIL'}")
        return 0
    except VerificationError as e:
        print(f"FAIL: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
