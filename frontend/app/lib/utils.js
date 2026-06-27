const CLIQUE_COLORS = [
  '#ef4444', '#22c55e', '#f59e0b', '#3b82f6', '#8b5cf6',
  '#06b6d4', '#f97316', '#6366f1', '#14b8a6', '#ec4899',
  '#84cc16', '#a855f7', '#eab308', '#3b82f6', '#64748b',
];

export function formatTime(t) {
  if (t === undefined || t === null) return '';
  const n = Number(t);
  if (Number.isNaN(n)) return String(t);
  if (n > 1e10) {
    const d = new Date(n * 1000);
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
      if (!multi.has(v)) colorMap[v] = CLIQUE_COLORS[i % CLIQUE_COLORS.length];
    });
  });
  multi.forEach(v => { colorMap[v] = '#f1c40f'; });

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
  let vertices = [...vSet];

  if (freq > 1) {
    const degree = {};
    filtered.forEach(e => {
      degree[e.u] = (degree[e.u] || 0) + 1;
      degree[e.v] = (degree[e.v] || 0) + 1;
    });
    vertices = vertices.filter(v => (degree[v] || 0) >= freq);
  }

  const edges = filtered.filter(e => vertices.includes(e.u) && vertices.includes(e.v));
  return { vertices, edges };
}

export function getSavingsDescription(pct) {
  if (pct > 50) return 'oldukça verimli';
  if (pct > 20) return 'verimli';
  return 'az verimli';
}
