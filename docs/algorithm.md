# Algorithm Module

Baligács (2026) makalesinin Lemma/Theorem bazlı implementasyonu.

## Modules

| File | Paper | Description |
|------|-------|-------------|
| `temporal_graph.py` | §2 | Temporal graph types, labeling, `Nmin`, `Nmax`, `pos_v(u)` |
| `bi_clique.py` | Lemma 4 | Temporal clique → bi-clique conversion |
| `dismountability.py` | Lemma 5, Obs 19 | Dismountability reduction to EM bi-clique |
| `simple_star.py` | Def 7-8 | Ordered labelings, simple star construction |
| `extended_star.py` | Def 12 | Extended star (`Emin` + `Emax` + `s*` edges) |
| `cut_crossing.py` | Lemma 16 | 3-hop-k-cut-crossing detection |
| `main_algorithm.py` | Lemma 17, Thm 18 | Recursive EM bi-clique spanner |
| `clique_optimization.py` | Thm 20, Thm 2 | Clique 7n optimization |

## Algorithm Flow

```
Temporal Clique G (n vertices)
    │
    ├─ {1,2}-hop dismountability (Obs 19)
    │   → V' ⊆ V, E_dismount
    │
    ├─ Theorem 20: V⁻, V⁺ partition check
    │   ├─ if valid: EM bi-clique → 7n' edges
    │   └─ if not: Lemma 4 → general bi-clique → 14n' edges
    │
    └─ spanner edges = E_dismount ∪ E_biclique
```

### EM Bi-clique Spanner (Theorem 18)

```
f(n): EM bi-clique spanner edge count
f(n) ≤ 6n + (3n - 4x) + f(x)  where x ≤ n/2
∴ f(n) ≤ 14n  (by induction)
```

### Key Optimizations

- **{1,2}-hop dismountability**: Removes vertices that can be served via 2-hop paths (4 edges per removal).
- **Theorem 20 shortcut**: When V⁻ and V⁺ partition V', directly build EM bi-clique for 7n bound.
- **Fallback**: Lemma 4 approach used when partition fails (still ≤ 7n total via `max(O(n), E_total) > cap` guard).

## Performance

- Spanner computation: O(n²) worst-case due to all-pairs edge fill-in.
- Stretch factor: sampled to max 50 random pairs for n > 10.
- Trend analysis: Bron–Kerbosch maximal clique finding per window.
- Typical real-world graphs (< 100 vertices, < 5000 edges): all operations < 1s.
