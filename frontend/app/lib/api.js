'use client';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function post(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function upload(path, formData) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text());
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

export function uploadCSV(file) {
  const fd = new FormData();
  fd.append('file', file);
  return upload('/api/upload', fd);
}

export function searchWordCliques(graph, word, windows = 10) {
  return post('/api/word-cliques', { graph, word, windows });
}

export function checkClique(graph, words) {
  return post('/api/check-clique', { graph, words });
}
