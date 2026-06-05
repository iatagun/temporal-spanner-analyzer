from spanner.types import TemporalGraph
from spanner.core import spanner_for_clique, random_temporal_clique
from spanner.verify import verify_spanner, VerificationError


def test_verify_small_clique():
    G = random_temporal_clique(4, 42)
    E = spanner_for_clique(G)
    try:
        verify_spanner(G, E, 7 * len(G.V))
        assert True
    except VerificationError:
        assert False, "Verification failed for small clique"


def test_verify_medium_clique():
    G = random_temporal_clique(8, 1)
    E = spanner_for_clique(G)
    try:
        verify_spanner(G, E, 7 * len(G.V))
        assert True
    except VerificationError:
        assert False, "Verification failed for medium clique"


def test_verify_multiple_seeds():
    for seed in range(10):
        G = random_temporal_clique(6, seed)
        E = spanner_for_clique(G)
        try:
            verify_spanner(G, E, 7 * len(G.V))
        except VerificationError:
            assert False, f"Verification failed for seed {seed}"


def test_verify_spanner_size_bound():
    for n in [3, 4, 5, 6, 7, 8]:
        G = random_temporal_clique(n, 7)
        E = spanner_for_clique(G)
        assert len(E) <= 7 * n, f"Spanner size {len(E)} exceeds 7n={7*n} for n={n}"
