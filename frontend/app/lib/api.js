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

export function computeTrends(graph, windows = 10, opts = {}) {
  return post('/api/trends', {
    graph,
    windows,
    raw_documents: opts.rawDocuments || [],
    pmi_threshold: opts.pmiThreshold ?? 0.15,
    association_measure: opts.associationMeasure || 'npmi',
  });
}

export function computeCompare(graph1, graph2) {
  return post('/api/compare', { graph1, graph2 });
}

export function uploadCSV(file, pmiThreshold, associationMeasure, collocationMode, lemmatize) {
  const fd = new FormData();
  fd.append('file', file);
  if (pmiThreshold !== undefined && pmiThreshold !== null) {
    fd.append('pmi_threshold', String(pmiThreshold));
  }
  if (associationMeasure) {
    fd.append('association_measure', associationMeasure);
  }
  if (collocationMode) {
    fd.append('collocation_mode', collocationMode);
  }
  if (lemmatize) {
    fd.append('lemmatize', 'true');
  }
  return upload('/api/upload', fd);
}

export function searchWordCliques(graph, word, windows = 10, opts = {}) {
  return post('/api/word-cliques', {
    graph,
    word,
    windows,
    raw_documents: opts.rawDocuments || [],
    pmi_threshold: opts.pmiThreshold ?? 0.15,
    association_measure: opts.associationMeasure || 'npmi',
  });
}

export function checkClique(graph, words) {
  return post('/api/check-clique', { graph, words });
}

export function fetchMweCandidates(rawDocuments, opts = {}) {
  return post('/api/mwe-candidates', {
    raw_documents: rawDocuments,
    max_n: opts.maxN ?? 4,
    min_freq: opts.minFreq ?? 2,
    top_n: opts.topN ?? 50,
  });
}

export function fetchPairConfidence(rawDocuments, word1, word2, opts = {}) {
  return post('/api/pair-confidence', {
    raw_documents: rawDocuments,
    word1,
    word2,
    association_measure: opts.associationMeasure || 'npmi',
    n_resamples: opts.nResamples ?? 500,
  });
}
