'use client';

import { useState, useCallback } from 'react';

const API = 'http://127.0.0.1:8000';

function formatTime(t) {
  if (t === undefined || t === null) return '';
  const n = Number(t);
  if (Number.isNaN(n)) return String(t);
  if (n > 1e10) {
    const d = new Date(n * 1000);
    return d.toISOString().slice(0, 10);
  }
  return n.toFixed(2);
}

export default function ExploreView({ fullGraph }) {
  const hasGraph = fullGraph && fullGraph.vertices && fullGraph.vertices.length > 0;
  const [wordQuery, setWordQuery] = useState('');
  const [wordData, setWordData] = useState(null);
  const [wordLoading, setWordLoading] = useState(false);
  const [wordError, setWordError] = useState(null);

  const [cliqueWords, setCliqueWords] = useState('');
  const [cliqueCheck, setCliqueCheck] = useState(null);
  const [cliqueLoading, setCliqueLoading] = useState(false);
  const [cliqueError, setCliqueError] = useState(null);

  const [activeView, setActiveView] = useState('word');

  const searchWord = useCallback(async () => {
    if (!wordQuery.trim() || !fullGraph) return;
    setWordLoading(true);
    setWordError(null);
    try {
      const res = await fetch(`${API}/api/word-cliques`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph: fullGraph, word: wordQuery.trim(), windows: 10 }),
      });
      if (!res.ok) throw new Error(await res.text());
      setWordData(await res.json());
    } catch (e) {
      setWordError(e.message);
    } finally {
      setWordLoading(false);
    }
  }, [wordQuery, fullGraph]);

  const checkClique = useCallback(async () => {
    const words = cliqueWords.split(',').map(w => w.trim()).filter(Boolean);
    if (words.length < 2 || !fullGraph) return;
    setCliqueLoading(true);
    setCliqueError(null);
    try {
      const res = await fetch(`${API}/api/check-clique`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph: fullGraph, words }),
      });
      if (!res.ok) throw new Error(await res.text());
      setCliqueCheck(await res.json());
    } catch (e) {
      setCliqueError(e.message);
    } finally {
      setCliqueLoading(false);
    }
  }, [cliqueWords, fullGraph]);

  const tabStyle = (active) => ({
    padding: '8px 20px',
    border: 'none',
    background: active ? '#4a90d9' : '#e0e0e0',
    color: active ? '#fff' : '#555',
    borderRadius: '6px 6px 0 0',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 13,
  });

  if (!hasGraph) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: '#999', background: '#f8f9fa', borderRadius: 8 }}>
        No graph data available. Upload a CSV or generate a synthetic graph first.
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 4, marginBottom: 16 }}>
        <button style={tabStyle(activeView === 'word')} onClick={() => setActiveView('word')}>Word Cliques</button>
        <button style={tabStyle(activeView === 'check')} onClick={() => setActiveView('check')}>Check Clique</button>
      </div>

      {activeView === 'word' && (
        <div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', marginBottom: 16 }}>
            <div style={{ flex: 1 }}>
              <label htmlFor="search-word" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Search Word</label>
              <input id="search-word" name="search-word" type="text" value={wordQuery}
                onChange={e => setWordQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && searchWord()}
                placeholder="e.g. yapay"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ccc', borderRadius: 6, fontSize: 14 }} />
            </div>
            <button onClick={searchWord} disabled={wordLoading || !wordQuery.trim()}
              style={{
                padding: '9px 20px', background: wordLoading ? '#999' : '#4a90d9', color: '#fff',
                border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                cursor: wordLoading ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap',
              }}>
              {wordLoading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {wordError && (
            <div style={{ padding: 10, background: '#fde8e8', borderRadius: 6, color: '#c0392b', fontSize: 13, marginBottom: 12 }}>
              {wordError}
            </div>
          )}

          {wordData && (
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>
                "{wordData.word}" appears in <strong>{wordData.timeline_count}</strong> cliques across <strong>{wordData.snapshots.length}</strong> time windows
              </div>

              {wordData.snapshots.length === 0 ? (
                <div style={{ padding: 20, textAlign: 'center', color: '#999', background: '#f8f9fa', borderRadius: 8 }}>
                  No clique membership found for "{wordData.word}"
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {wordData.snapshots.map((s, i) => (
                    <div key={i} style={{
                      padding: 12, background: '#f8f9fa', borderRadius: 8,
                      border: '1px solid #eee', fontSize: 13,
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600 }}>{s.clique_label}</span>
                        <span style={{ color: '#999' }}>Window {s.window}</span>
                      </div>
                      <div style={{ color: '#666', marginBottom: 4 }}>
                        {formatTime(s.window_start)} — {formatTime(s.window_end)}
                      </div>
                      <div style={{ color: '#888' }}>
                        Members ({s.size}): {s.members.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeView === 'check' && (
        <div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', marginBottom: 16 }}>
            <div style={{ flex: 1 }}>
              <label htmlFor="clique-words" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Words (comma-separated)</label>
              <input id="clique-words" name="clique-words" type="text" value={cliqueWords}
                onChange={e => setCliqueWords(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && checkClique()}
                placeholder="e.g. yapay, zekâ, derin, öğrenme"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ccc', borderRadius: 6, fontSize: 14 }} />
            </div>
            <button onClick={checkClique} disabled={cliqueLoading || !cliqueWords.trim()}
              style={{
                padding: '9px 20px', background: cliqueLoading ? '#999' : '#8e44ad', color: '#fff',
                border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                cursor: cliqueLoading ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap',
              }}>
              {cliqueLoading ? 'Checking...' : 'Check'}
            </button>
          </div>

          {cliqueError && (
            <div style={{ padding: 10, background: '#fde8e8', borderRadius: 6, color: '#c0392b', fontSize: 13, marginBottom: 12 }}>
              {cliqueError}
            </div>
          )}

          {cliqueCheck && (
            <div style={{
              padding: 20, borderRadius: 8,
              background: cliqueCheck.is_clique ? '#eafaf1' : '#fde8e8',
              border: `1px solid ${cliqueCheck.is_clique ? '#27ae60' : '#e74c3c'}`,
            }}>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                {cliqueCheck.is_clique ? '✓ Temporal Clique' : '✗ Not a Temporal Clique'}
              </div>
              <div style={{ fontSize: 13, color: '#555', marginBottom: 4 }}>
                {cliqueCheck.total_pairs} total pairs, {cliqueCheck.edge_count} edges found
              </div>
              {cliqueCheck.missing_pairs.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#c0392b', marginBottom: 4 }}>Missing edges:</div>
                  <div style={{ fontSize: 13 }}>
                    {cliqueCheck.missing_pairs.map(([u, v], i) => (
                      <span key={i} style={{ background: '#fde8e8', padding: '2px 8px', borderRadius: 4, marginRight: 4 }}>
                        {u} — {v}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
