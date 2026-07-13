import { getCliqueColor } from './palette';

// Reserved for vertices that belong to more than one clique -- distinct
// from the palette itself so it can never be mistaken for a specific
// clique's identity color.
const MULTI_CLIQUE_COLOR = '#f1c40f';

export function formatTime(t) {
  if (t === undefined || t === null) return '';
  const n = Number(t);
  if (Number.isNaN(n)) return String(t);
  if (n > 1e9) {
    const d = n > 1e10 ? new Date(n) : new Date(n * 1000);
    return d.toISOString().slice(0, 10);
  }
  return n.toFixed(2);
}

export function maximalCliques(vertices, edges) {
  const adj = {};
  vertices.forEach(v => { adj[v] = new Set(); });
  edges.forEach(({ u, v }) => { adj[u].add(v); adj[v].add(u); });

  const results = [];
  function bk(R, P, X) {
    if (P.size === 0 && X.size === 0) {
      if (R.size >= 2) results.push([...R]);
      return;
    }
    const pivot = [...(P.size ? P : X)][0];
    for (const v of [...P].filter(v => !adj[pivot].has(v))) {
      bk(
        new Set([...R, v]),
        new Set([...P].filter(x => adj[v].has(x))),
        new Set([...X].filter(x => adj[v].has(x)))
      );
      P.delete(v);
      X.add(v);
    }
  }
  bk(new Set(), new Set(vertices), new Set());
  return results;
}

export function buildCliqueColorMap(vertices, cliques) {
  const membership = {};
  vertices.forEach(v => { membership[v] = []; });
  cliques.forEach((c, i) => c.forEach(v => membership[v].push(i)));

  const multi = new Set();
  vertices.forEach(v => {
    if (membership[v].length > 1) multi.add(v);
  });

  const colorMap = {};
  cliques.forEach((c, i) => {
    c.forEach(v => {
      if (!multi.has(v)) colorMap[v] = getCliqueColor(i);
    });
  });
  multi.forEach(v => { colorMap[v] = MULTI_CLIQUE_COLOR; });

  return colorMap;
}

export function generateGraph(n, seed) {
  const V = Array.from({ length: n }, (_, i) => String(i));
  const edges = [];
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const r = ((i + 1) * (j + 1) * (seed + 1)) % 1000 / 1000;
      edges.push({ u: String(i), v: String(j), label: r });
    }
  }
  return { vertices: V, edges };
}

export function filterGraph(graph, tMin, tMax, freq) {
  if (!graph) return null;
  const filtered = graph.edges.filter(e => {
    const l = Number(e.label);
    return l >= tMin && l <= tMax;
  });
  const vSet = new Set();
  filtered.forEach(e => { vSet.add(e.u); vSet.add(e.v); });

  if (freq <= 1) {
    // Every edge in `filtered` connects two vertices already in vSet by
    // construction, so there is nothing left to filter out.
    return { vertices: [...vSet], edges: filtered };
  }

  const degree = {};
  filtered.forEach(e => {
    degree[e.u] = (degree[e.u] || 0) + 1;
    degree[e.v] = (degree[e.v] || 0) + 1;
  });
  const vertexSet = new Set([...vSet].filter(v => (degree[v] || 0) >= freq));

  // Sets give O(1) membership checks -- the previous version used
  // Array.includes() here, an O(V) scan per edge (O(E*V) overall), which
  // measurably added up for corpus-sized graphs (thousands of vertices).
  const edges = filtered.filter(e => vertexSet.has(e.u) && vertexSet.has(e.v));
  return { vertices: [...vertexSet], edges };
}

export function getSavingsDescription(pct) {
  if (pct > 50) return 'oldukça verimli';
  if (pct > 20) return 'verimli';
  return 'az verimli';
}

// Log-likelihood (G^2, Dunning 1993) has a classical chi-square (df=1)
// interpretation -- these are the standard critical values. Returns null
// (no label) below p<0.05 rather than claiming "not significant" as a
// fact, since a null result here just means this particular measure
// didn't clear the bar, not that the pair is meaningless.
export function significanceLabel(logLikelihood) {
  if (logLikelihood == null || Number.isNaN(logLikelihood)) return null;
  if (logLikelihood >= 10.83) return 'p<0.001';
  if (logLikelihood >= 6.63) return 'p<0.01';
  if (logLikelihood >= 3.84) return 'p<0.05';
  return null;
}

// t-score's conventional collocation-significance cutoff (~1.96, a
// z-test-style threshold for large samples). NPMI/Dice are similarity
// coefficients, not hypothesis-test statistics -- they deliberately get
// no such label anywhere this is used, to avoid a false impression of
// statistical rigor they don't have.
export function isTScoreSignificant(tScore) {
  return typeof tScore === 'number' && !Number.isNaN(tScore) && tScore >= 1.96;
}
