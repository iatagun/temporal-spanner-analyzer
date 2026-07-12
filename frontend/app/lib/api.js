'use client';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function errorMessageFrom(res) {
  const raw = await res.text();
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed.detail === 'string') return parsed.detail;
    if (Array.isArray(parsed.detail)) {
      // FastAPI/Pydantic validation errors: [{loc, msg, ...}, ...]
      return parsed.detail.map(d => d.msg || JSON.stringify(d)).join('; ');
    }
  } catch {
    // not JSON, fall through to raw text
  }
  return raw || `${res.status} ${res.statusText}`;
}

async function post(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await errorMessageFrom(res));
  return res.json();
}

async function upload(path, formData) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(await errorMessageFrom(res));
  return res.json();
}

export function computeSpanner(graph, opts = {}) {
  return post('/api/spanner', {
    graph,
    min_clique_size: opts.minCliqueSize || 3,
    max_cliques: opts.maxCliques || 0,
  });
}

export function computeTrends(graph, windows = 10) {
  return post('/api/trends', { graph, windows });
}

export function computeCompare(graph1, graph2) {
  return post('/api/compare', { graph1, graph2 });
}

export function uploadCSV(file, pmiThreshold) {
  const fd = new FormData();
  fd.append('file', file);
  if (pmiThreshold !== undefined && pmiThreshold !== null) {
    fd.append('pmi_threshold', String(pmiThreshold));
  }
  return upload('/api/upload', fd);
}

export function searchWordCliques(graph, word, windows = 10) {
  return post('/api/word-cliques', { graph, word, windows });
}

export function checkClique(graph, words) {
  return post('/api/check-clique', { graph, words });
}
