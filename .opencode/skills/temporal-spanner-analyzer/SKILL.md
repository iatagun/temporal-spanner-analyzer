# Temporal Spanner Analyzer — Skill

Baligács (2026) "Temporal Cliques Admit Linear Spanners" implementation.
CSV → PMI graph → maximal cliques → linear spanner (≤7n edges) → trends/comparison.

## Trigger

When the user mentions `weekly-project`, `temporal-spanner`, `Baligács`, `spanner analyzer`, or opens files under `C:\Users\user\OneDrive\Masaüstü\weekly-project`, load this skill.

## Quick Start

```bash
# Backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend && npm run dev

# Tests
python -m pytest tests/ -v
```

## Architecture

```
main.py (CLI)                ← CLI entry for algorithm testing
backend/
  main.py                    ← FastAPI app, CORS, router registration
  models.py                  ← 15 Pydantic models (GraphSchema, SpannerResponse, etc.)
  routers/
    spanner.py               ← POST /api/spanner, /api/upload, /api/export
    trends.py                ← POST /api/trends
    compare.py               ← POST /api/compare
    explore.py               ← POST /api/word-cliques, /api/check-clique
  services/
    graph_builder.py         ← CSV/JSON → PMI graph (stopwords, date parsing)
    graph_utils.py           ← Adjacency list, Bron–Kerbosch maximal cliques
    spanner_service.py       ← Pipeline: label dict → cliques → spanner edges
    trend_analyzer.py        ← Time-windowed clique evolution tracking
  algorithm/
    temporal_graph.py        ← Nmin, Nmax, pos, BFS
    bi_clique.py             ← Lemma 4: Clique → Biclique
    simple_star.py           ← Def 7-8: Ordered labeling, simple star cover
    extended_star.py         ← Def 12: Extended star (s* and t* centric)
    cut_crossing.py          ← Lemma 16: 3-hop-k-cut-crossing detection
    dismountability.py       ← Lemma 5 + Obs 19: Dismountability
    main_algorithm.py        ← Lemma 17, Thm 18: Recursive EM spanner
    clique_optimization.py   ← Thm 2 + Thm 20: Clique 7n shortcut
spanner/
  types.py                   ← TemporalGraph, TemporalBiClique dataclasses
  core.py                    ← Re-export facade for all algorithm functions
  verify.py                  ← verify_spanner, VerificationError
frontend/
  app/
    page.js                  ← Main SPA (645 lines: state, API calls, layout)
    components/
      GraphViewer.js         ← Cytoscape.js graph visualization
      TrendsView.js          ← D3.js Gantt + line chart
      ExploreView.js         ← Word cliques search + clique checker
tests/
  test_integration.py        ← FastAPI TestClient: upload, spanner, export, health
  test_explore.py            ← check_clique, word_cliques
  test_compare.py            ← compare two graphs
  test_verify.py             ← verify_spanner unit tests
  test_algorithm/            ← One test file per algorithm module
examples/
  teknoloji_ornek.csv        ← 26 rows: AI/tech terms 2018–2024
  pandemic_ornek.csv         ← 30 rows: pandemic discourse 2019–2024
```

## Data Flow

```
CSV/JSON → parse_csv/parse_json → PMI computation → GraphSchema
  → maximal_cliques (Bron–Kerbosch)
  → for each clique: spanner_for_clique (Lemma 17/Thm 18)
  → all_spanner_edges ∪ uncovered edges
  → verify_spanner + stretch_factor
```

## Code Conventions

### Python
- **Files**: `snake_case.py`
- **Classes**: `PascalCase` (e.g., `TemporalGraph`, `CliqueQualitySchema`)
- **Functions/Methods**: `snake_case` (e.g., `compute_spanner_pipeline`, `_edge_key`)
- **Private helpers**: `_leading_underscore` (e.g., `_build_graph`, `_process_clique`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `PMI_THRESHOLD_DEFAULT`, `TURKISH_STOPWORDS`)
- **Type hints**: Required on ALL function signatures (params + return)
- **Imports order**: stdlib → third-party → local (absolute paths from project root, e.g. `from backend.models import GraphSchema`)
- **`from __future__ import annotations`**: Used in all algorithm files (enables PEP 604 `X | Y` syntax)
- **Error handling**: `HTTPException(status_code, "message")` in routers; `try/except` with `ValueError` in services; `VerificationError` (custom) in verify module
- **No async**: All FastAPI endpoints are sync (threadpool)
- **No relative imports**: Always absolute from project root

### JavaScript
- **Files**: `PascalCase.js` (matching component name, e.g. `GraphViewer.js`)
- **Functions**: `camelCase` (e.g., `computeSpanner`, `handleUpload`)
- **Variables**: `camelCase` (e.g., `trendData`, `uploadInfo`)
- **Imports**: React hooks first, then local components, then third-party
- **API constant**: `const API = 'http://127.0.0.1:8000'` (hardcoded in every file)
- **State**: Raw `useState` hooks only (no Redux, no Context)
- **Callbacks**: All API-calling functions wrapped in `useCallback`
- **Derived state**: `useMemo` for computed values (e.g., `currentGraph`, `compareGraph`)
- **Styling**: Inline style objects (90%), no CSS-in-JS library, no Tailwind

### API Design
- All routes under `/api` prefix via `APIRouter`
- POST for all state-changing operations
- Pydantic `BaseModel` for request/response schemas
- Multipart form for file upload (`UploadFile`)
- CORS wide open (`allow_origins=["*"]`)

### Testing
- Framework: `pytest`
- Test files: `test_<module>.py` naming
- Test functions: `test_<description>()` with plain `assert`
- Integration tests: `fastapi.testclient.TestClient`
- Algorithm tests: Direct import from `spanner.core`

## Bug Fix History (Critical — Do Not Re-introduce)

| # | Issue | File | Fix | Type |
|---|-------|------|-----|------|
| 1 | Stretch factor masks missing paths | `routers/spanner.py` | `if d_spanner is None: continue` | Critical |
| 2 | PMI Laplace smoothing | `services/graph_builder.py` | Raw PMI, `min_codf ≥ 1` (Church & Hanks) | Critical |
| 3 | Self-loop edges corrupt BFS | `routers/spanner.py` | `if u == v: continue` | Critical |
| 4 | BK pivot excludes pivot vertex | `services/graph_utils.py` | `P - adj[pivot]` NOT `P - (adj[pivot] \| {pivot})` (latter breaks complete graphs) | Critical |
| 5 | BFS O(V·E) exponential | `algorithm/temporal_graph.py` | Adjacency-list BFS O(V+E) | Critical |
| 6 | Duplicate edge labels | `services/spanner_service.py` | Minimum (earliest) label kept | High |
| 7 | Nmin/Nmax crash | `algorithm/dismountability.py` | try/except guard | High |
| 8 | Lemma 17 n=2 empty loop | `algorithm/main_algorithm.py` | Early return for n < 3 | High |
| 9 | _jaccard(∅,∅) = 0.0 | `services/trend_analyzer.py` | Return `1.0` | High |
| 10 | Timeline death last window | `services/trend_analyzer.py` | Guard before assigning death | High |
| 11 | pos() crash | `algorithm/temporal_graph.py` | try/except, returns `-1` | Medium |
| 12 | Duplicate edges in graph_builder | `services/graph_builder.py` | Earliest label wins | Medium |
| 13 | Full graph verify missing | `services/spanner_service.py` | Union spanner verified after pipeline | Medium |
| 14 | Non-deterministic stretch | `routers/spanner.py` | `sorted(clique_pairs)[:50]` | Medium |
| 15 | int/str VertexID crash | `spanner/types.py` | `__post_init__` normalizes all to str | Medium |
| 16 | Unparseable dates | `services/graph_builder.py` | Sentinel + >50% threshold raises ValueError | Low |
| 17 | CSV word-splitting | `services/graph_builder.py` | `re.split(r'[,\s]+', ...)` | Low |
| 18 | Biclique complete-graph assumption | `algorithm/temporal_graph.py` | Filter candidates by existing edges | Low |
| 19 | _canonicalize drops duplicates | `spanner/types.py` | logging.warning + earliest label kept | Low |
| 20 | 2-column CSV without header rejected | `services/graph_builder.py` | `len(row) < 3` → `< 2` + detect header vs data | Critical |
| 21 | A=B comparison same range | `frontend/app/page.js` | A = first 40%, B = last 40% | High |

## PMI Formula
```
pmi(w1,w2) = log( N * co-occurrence(w1,w2) / (df(w1) * df(w2)) )
```
- `N` = total documents/rows
- `df` = document frequency (how many documents contain the word)
- `co-occurrence` = how many documents contain BOTH words
- Threshold: `min_codf ≥ 1` (raw PMI, no Laplace smoothing)
- Edges below `pmi_threshold` (default 0.0) are filtered out

## CSV Format
Two supported formats:
1. **With header**: `date,words` + data rows (auto-detected)
2. **Without header**: `date,word1 word2 word3` (auto-detected if first cell is parseable date)

If first cell is NOT parseable as date, it's treated as a header row and skipped.

Date formats: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`, `DD.MM.YYYY`, `DD/MM/YYYY`, or numeric timestamps.
Turkish stopwords (47 words) automatically filtered. Words shorter than 2 characters removed.

## Spanner Algorithm (Baligács 2026)

1. **Clique → Biclique** (Lemma 4): Split clique vertices into two ordered partitions
2. **Dismountability** (Lemma 5/Obs 19): Remove "sökülebilir" (dismountable) vertices that can be served by {1,2}-hop paths. Each removal adds ≤4 edges to spanner. Result: EM (Earliest-Minimum/Maximum) biclique.
3. **Recursive EM Biclique Spanner** (Lemma 17/Thm 18):
   - Pick `s*` (first source), `k = n // 2`
   - Order T by `pos(s*, t)`, map each t to its Nmin partner
   - Test 3-hop-k-cut-crossing (Lemma 16) for all `s_i` (i > k)
   - **Case i (all crossing)**: Simple star (Def 8) + 3-hop paths + Emax edges. Cover `(S, T')` where T' = first k. Recurse on `(S, T_rem)`.
   - **Case ii (some non-crossing)**: Extended stars (Def 12) centered on `s*` and offending `t_i`. Cover `(S', T)`where S' = remaining. Recurse on `(S_rem, T)`.
   - Each recursion halves the problem; each level adds ≤ 6n edges
4. **Clique shortcut** (Thm 20): Direct 7n bound for cliques
5. **Verify**: spanner_paths ≥ original_paths for all pairs

## Key Metrics
- `savings_pct = round((1 - spanner_count / uploaded_count) * 100, 1)`
- `ratio_per_n = round(spanner_count / n, 2)`
- `bound_7n = 7 * n` (theoretical upper bound per Baligács)
- `stretch_factor`: average ratio of spanner path length to original path length (sampled up to 50 clique pairs)

## Known Limitations
- Frontend is monolithic SPA (645 lines, all state in one component)
- API URL hardcoded in 4 JS files (`http://127.0.0.1:8000`)
- No persistence layer (all in-memory)
- Trends work best with datasets that have multiple edges per time window
- No TypeScript (plain JS)
- Max 80 vertices for synthetic generation (UI constraint)
