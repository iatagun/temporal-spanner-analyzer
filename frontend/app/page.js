'use client';

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import GraphViewer from './components/GraphViewer';
import TrendsView from './components/TrendsView';
import ExploreView from './components/ExploreView';

const API = 'http://127.0.0.1:8000';

function maximalCliques(vertices, edges) {
  const adj = {};
  vertices.forEach(v => adj[v] = new Set());
  edges.forEach(({ u, v }) => { adj[u].add(v); adj[v].add(u); });
  const results = [];
  function bk(R, P, X) {
    if (P.size === 0 && X.size === 0) { if (R.size >= 2) results.push([...R]); return; }
    const pivot = [...(P.size ? P : X)][0];
    for (const v of [...P].filter(v => !adj[pivot].has(v))) {
      bk(new Set([...R, v]), new Set([...P].filter(x => adj[v].has(x))), new Set([...X].filter(x => adj[v].has(x))));
      P.delete(v); X.add(v);
    }
  }
  bk(new Set(), new Set(vertices), new Set());
  return results;
}

function buildCliqueColorMap(vertices, cliques) {
  const colors = ['#e74c3c','#2ecc71','#f39c12','#3498db','#9b59b6','#1abc9c','#e67e22','#34495e','#16a085','#c0392b','#27ae60','#8e44ad','#d35400','#2980b9','#2c3e50'];
  const membership = {}; vertices.forEach(v => membership[v] = []);
  cliques.forEach((c, i) => c.forEach(v => membership[v].push(i)));
  const multi = new Set(); vertices.forEach(v => { if (membership[v].length > 1) multi.add(v); });
  const colorMap = {};
  cliques.forEach((c, i) => c.forEach(v => { if (!multi.has(v)) colorMap[v] = colors[i % colors.length]; }));
  multi.forEach(v => colorMap[v] = '#f1c40f');
  return colorMap;
}

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

export default function Home() {
  const [mode, setMode] = useState('synthetic');
  const [view, setView] = useState('spanner');
  const [n, setN] = useState(10);
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [fullGraph, setFullGraph] = useState(null);
  const [timeRange, setTimeRange] = useState(null);
  const [timeMin, setTimeMin] = useState(0);
  const [timeMax, setTimeMax] = useState(1);
  const [minFreq, setMinFreq] = useState(1);
  const [liveMode, setLiveMode] = useState(false);
  const [timeMin2, setTimeMin2] = useState(0);
  const [timeMax2, setTimeMax2] = useState(1);
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const debounceRef = useRef(null);
  const fileRef = useRef(null);

  const generateGraph = useCallback(() => {
    const V = Array.from({ length: n }, (_, i) => String(i));
    const edges = [];
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const r = ((i + 1) * (j + 1) * (seed + 1)) % 1000 / 1000;
        edges.push({ u: String(i), v: String(j), label: r });
      }
    }
    return { vertices: V, edges };
  }, [n, seed]);

  const filterGraph = useCallback((graph, tMin, tMax, freq) => {
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
      filtered.forEach(e => { degree[e.u] = (degree[e.u] || 0) + 1; degree[e.v] = (degree[e.v] || 0) + 1; });
      vertices = vertices.filter(v => (degree[v] || 0) >= freq);
    }
    const edges = filtered.filter(e => vertices.includes(e.u) && vertices.includes(e.v));
    return { vertices, edges };
  }, []);

  const uploadTimeRange = useMemo(() => {
    if (!timeRange) return null;
    return { min: Math.min(...timeRange.map(Number)), max: Math.max(...timeRange.map(Number)) };
  }, [timeRange]);

  const currentGraph = useMemo(() => {
    if (mode === 'synthetic') return uploadInfo?.graph || null;
    if (!fullGraph || !timeRange) return uploadInfo?.graph || null;
    return filterGraph(fullGraph, timeMin, timeMax, minFreq);
  }, [mode, uploadInfo, fullGraph, timeRange, timeMin, timeMax, minFreq, filterGraph]);

  const compareGraph = useMemo(() => {
    if (!fullGraph || !timeRange) return null;
    return filterGraph(fullGraph, timeMin2, timeMax2, minFreq);
  }, [fullGraph, timeRange, timeMin2, timeMax2, minFreq, filterGraph]);

  const computeSpanner = useCallback(async (graph) => {
    if (!graph || graph.vertices.length < 2) {
      setResult(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/spanner`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const computeTrends = useCallback(async (graph) => {
    if (!graph || graph.edges.length === 0) {
      setTrendData(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/trends`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph, windows: 10 }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }
      const data = await res.json();
      setTrendData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const computeCompare = useCallback(async (graphA, graphB) => {
    if (!graphA || !graphB || graphA.vertices.length < 2 || graphB.vertices.length < 2) {
      setCompareData(null);
      return;
    }
    setCompareLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph1: graphA, graph2: graphB }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }
      const data = await res.json();
      setCompareData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setCompareLoading(false);
    }
  }, []);

  const handleSynthetic = () => {
    const graph = generateGraph();
    setFullGraph(null);
    setTimeRange(null);
    setUploadInfo({ graph, label: `Synthetic (n=${n}, seed=${seed})` });
    setResult(null);
    computeSpanner(graph);
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) { setError('Select a CSV file'); return; }
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/api/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }
      const data = await res.json();
      setFullGraph(data.graph);
      const tr = data.time_range.filter(t => t !== '').map(Number);
      if (tr.length >= 2) {
        setTimeRange(tr);
        const fullMin = Math.min(...tr);
        const fullMax = Math.max(...tr);
        const range = fullMax - fullMin;
        setTimeMin(fullMin);
        setTimeMax(fullMin + range * 0.4);
        setTimeMin2(fullMin + range * 0.6);
        setTimeMax2(fullMax);
      } else {
        setTimeRange(null);
      }
      setUploadInfo({
        graph: data.graph,
        label: `${data.graph.vertices.length} vertices, ${data.graph.edges.length} edges`,
      });
      setResult(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilter = () => {
    if (currentGraph) {
      computeSpanner(currentGraph);
    }
  };

  useEffect(() => {
    if (!liveMode || !currentGraph || currentGraph.vertices.length < 2) return;
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => computeSpanner(currentGraph), 400);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [liveMode, timeMin, timeMax, currentGraph, computeSpanner]);

  const MetricCard = ({ label, value, desc }) => (
    <div style={{
      background: '#f8f9fa', borderRadius: 8, padding: '12px 16px',
      textAlign: 'center', border: '1px solid #eee', position: 'relative',
    }} title={desc}>
      <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: '#222' }}>{value}</div>
      {desc && <div style={{ fontSize: 10, color: '#aaa', marginTop: 2, fontStyle: 'italic' }}>{desc}</div>}
    </div>
  );

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

  const rangeStyle = {
    width: '100%',
    height: 6,
    borderRadius: 3,
    background: '#ddd',
    outline: 'none',
    WebkitAppearance: 'none',
    accentColor: '#4a90d9',
    margin: '6px 0',
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 16px', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 4px 0' }}>Temporal Spanner Analyzer</h1>
        <p style={{ fontSize: 14, color: '#666', margin: 0 }}>
          Baligács (2026) — Temporal clique → linear spanner. Full clique ≤ 7n edges.
        </p>
      </header>

      <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: 10, padding: 20, marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 4, marginBottom: 16 }}>
          <button style={tabStyle(mode === 'synthetic')} onClick={() => { setMode('synthetic'); setResult(null); setUploadInfo(null); setFullGraph(null); setTimeRange(null); }}>Synthetic</button>
          <button style={tabStyle(mode === 'upload')} onClick={() => { setMode('upload'); setResult(null); setUploadInfo(null); setFullGraph(null); setTimeRange(null); }}>CSV Upload</button>
        </div>

        {mode === 'synthetic' ? (
          <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div>
              <label htmlFor="vertices-n" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Vertices (n)</label>
              <input id="vertices-n" name="vertices-n" type="number" min={2} max={80} value={n} onChange={e => setN(Number(e.target.value))}
                style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 6, fontSize: 14, width: 100 }} />
            </div>
            <div>
              <label htmlFor="seed" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Seed</label>
              <input id="seed" name="seed" type="number" value={seed} onChange={e => setSeed(Number(e.target.value))}
                style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 6, fontSize: 14, width: 100 }} />
            </div>
            <button onClick={handleSynthetic} disabled={loading}
              style={{
                padding: '10px 24px', background: loading ? '#999' : '#4a90d9', color: '#fff',
                border: 'none', borderRadius: 6, fontSize: 14, fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}>
              {loading ? 'Computing...' : 'Compute Spanner'}
            </button>
          </div>
        ) : (
          <div>
            <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: uploadTimeRange ? 16 : 0 }}>
              <div>
                <label htmlFor="csv-file" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>CSV File (date,words)</label>
                <input id="csv-file" name="csv-file" type="file" accept=".csv,.json" ref={fileRef}
                  style={{ fontSize: 13, padding: '6px 0' }} />
              </div>
              <div>
                <label htmlFor="min-freq" style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Min Freq</label>
                <input id="min-freq" name="min-freq" type="number" min={1} max={20} value={minFreq}
                  onChange={e => setMinFreq(Math.max(1, Number(e.target.value)))}
                  style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 6, fontSize: 14, width: 70 }} />
              </div>
              <button onClick={handleUpload} disabled={loading}
                style={{
                  padding: '10px 24px', background: loading ? '#999' : '#4a90d9', color: '#fff',
                  border: 'none', borderRadius: 6, fontSize: 14, fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}>
                {loading ? 'Processing...' : 'Upload CSV'}
              </button>
            </div>

            {uploadTimeRange && view !== 'compare' && (
              <div style={{
                marginTop: 8, padding: 16, background: '#f8f9fa', borderRadius: 8,
                border: '1px solid #eee',
              }}>
                <div style={{ fontSize: 12, color: '#555', marginBottom: 8, fontWeight: 600 }}>
                  Time Range: {formatTime(timeMin)} — {formatTime(timeMax)}
                  <span style={{ fontWeight: 400, color: '#999' }}>
                    {' '}(full: {formatTime(uploadTimeRange.min)} — {formatTime(uploadTimeRange.max)})
                  </span>
                </div>
                <div style={{ position: 'relative', height: 24 }}>
                  <input
                    id="time-min" name="time-min"
                    type="range"
                    min={uploadTimeRange.min}
                    max={uploadTimeRange.max}
                    step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                    value={timeMin}
                    onChange={e => {
                      const v = Number(e.target.value);
                      if (v <= timeMax) setTimeMin(v);
                    }}
                    style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto' }}
                  />
                  <input
                    id="time-max" name="time-max"
                    type="range"
                    min={uploadTimeRange.min}
                    max={uploadTimeRange.max}
                    step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                    value={timeMax}
                    onChange={e => {
                      const v = Number(e.target.value);
                      if (v >= timeMin) setTimeMax(v);
                    }}
                    style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto' }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#999', margin: '2px 0 8px 0' }}>
                  <span>{formatTime(uploadTimeRange.min)}</span>
                  <span>{formatTime(uploadTimeRange.max)}</span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button onClick={handleApplyFilter} disabled={loading || !currentGraph}
                    style={{
                      padding: '8px 20px', background: loading || !currentGraph ? '#999' : '#4a90d9', color: '#fff',
                      border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                      cursor: loading || !currentGraph ? 'not-allowed' : 'pointer',
                    }}>
                    {loading ? 'Computing...' : `Spanner (${currentGraph?.vertices?.length || 0}v, ${currentGraph?.edges?.length || 0}e)`}
                  </button>
                  <button onClick={() => setLiveMode(!liveMode)}
                    style={{
                      padding: '8px 16px', background: liveMode ? '#e67e22' : '#f0f0f0', color: liveMode ? '#fff' : '#555',
                      border: `1px solid ${liveMode ? '#e67e22' : '#ccc'}`, borderRadius: 6, fontSize: 13, fontWeight: 600,
                      cursor: 'pointer',
                    }}>
                    {liveMode ? 'Live: ON' : 'Live: OFF'}
                  </button>
                  <button onClick={() => computeTrends(fullGraph)} disabled={loading || !fullGraph}
                    style={{
                      padding: '8px 20px', background: loading || !fullGraph ? '#999' : '#27ae60', color: '#fff',
                      border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                      cursor: loading || !fullGraph ? 'not-allowed' : 'pointer',
                    }}>
                    {loading ? 'Computing...' : 'Trends'}
                  </button>
                </div>
              </div>
            )}

            {uploadTimeRange && view === 'compare' && (
              <div style={{
                marginTop: 8, padding: 16, background: '#f8f9fa', borderRadius: 8,
                border: '1px solid #eee',
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div>
                    <div style={{ fontSize: 12, color: '#4a90d9', marginBottom: 6, fontWeight: 600 }}>
                      Period A: {formatTime(timeMin)} — {formatTime(timeMax)}
                    </div>
                    <div style={{ position: 'relative', height: 24 }}>
                      <input id="compare-a-min" name="compare-a-min" type="range" min={uploadTimeRange.min} max={uploadTimeRange.max}
                        step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                        value={timeMin}
                        onChange={e => { const v = Number(e.target.value); if (v <= timeMax) setTimeMin(v); }}
                        style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto', accentColor: '#4a90d9' }} />
                      <input id="compare-a-max" name="compare-a-max" type="range" min={uploadTimeRange.min} max={uploadTimeRange.max}
                        step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                        value={timeMax}
                        onChange={e => { const v = Number(e.target.value); if (v >= timeMin) setTimeMax(v); }}
                        style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto', accentColor: '#4a90d9' }} />
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 12, color: '#e67e22', marginBottom: 6, fontWeight: 600 }}>
                      Period B: {formatTime(timeMin2)} — {formatTime(timeMax2)}
                    </div>
                    <div style={{ position: 'relative', height: 24 }}>
                      <input id="compare-b-min" name="compare-b-min" type="range" min={uploadTimeRange.min} max={uploadTimeRange.max}
                        step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                        value={timeMin2}
                        onChange={e => { const v = Number(e.target.value); if (v <= timeMax2) setTimeMin2(v); }}
                        style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto', accentColor: '#e67e22' }} />
                      <input id="compare-b-max" name="compare-b-max" type="range" min={uploadTimeRange.min} max={uploadTimeRange.max}
                        step={(uploadTimeRange.max - uploadTimeRange.min) / 100 || 0.01}
                        value={timeMax2}
                        onChange={e => { const v = Number(e.target.value); if (v >= timeMin2) setTimeMax2(v); }}
                        style={{ ...rangeStyle, position: 'absolute', top: 0, left: 0, background: 'transparent', pointerEvents: 'auto', accentColor: '#e67e22' }} />
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#999', margin: '2px 0 10px 0' }}>
                  <span>{formatTime(uploadTimeRange.min)}</span>
                  <span>{formatTime(uploadTimeRange.max)}</span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button onClick={() => computeCompare(currentGraph, compareGraph)} disabled={compareLoading || !currentGraph || !compareGraph}
                    style={{
                      padding: '8px 20px', background: compareLoading || !currentGraph || !compareGraph ? '#999' : '#8e44ad', color: '#fff',
                      border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                      cursor: compareLoading || !currentGraph || !compareGraph ? 'not-allowed' : 'pointer',
                    }}>
                    {compareLoading ? 'Comparing...' : `Compare (${currentGraph?.vertices?.length || 0}v × ${compareGraph?.vertices?.length || 0}v)`}
                  </button>
                  <button onClick={() => computeTrends(fullGraph)} disabled={loading || !fullGraph}
                    style={{
                      padding: '8px 16px', background: loading || !fullGraph ? '#999' : '#27ae60', color: '#fff',
                      border: 'none', borderRadius: 6, fontSize: 13, fontWeight: 600,
                      cursor: loading || !fullGraph ? 'not-allowed' : 'pointer',
                    }}>
                    {loading ? 'Computing...' : 'Trends'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div style={{ marginTop: 12, padding: 10, background: '#fde8e8', borderRadius: 6, color: '#c0392b', fontSize: 13, whiteSpace: 'pre-wrap' }}>
            {error}
          </div>
        )}
      </div>

      {uploadInfo?.graph && (
        <div style={{ display: 'flex', gap: 4, marginBottom: 16, marginTop: -8 }}>
          <button style={tabStyle(view === 'spanner')} onClick={() => { setView('spanner'); if (!result) handleApplyFilter(); }}>Spanner</button>
          <button style={tabStyle(view === 'trends')} onClick={() => { setView('trends'); if (!trendData) computeTrends(fullGraph || currentGraph); }}>Trends</button>
          <button style={tabStyle(view === 'compare')} onClick={() => { setView('compare'); if (!compareData && currentGraph && compareGraph) computeCompare(currentGraph, compareGraph); }}>Compare</button>
          <button style={tabStyle(view === 'explore')} onClick={() => setView('explore')}>Explore</button>
        </div>
      )}

      {view === 'spanner' && result && (
        <>
          {(() => {
            const m = result.metrics;
            const savingsText = m.savings_pct > 50 ? 'oldukça verimli' : m.savings_pct > 20 ? 'verimli' : 'az verimli';
            return (
              <div style={{
                padding: '14px 18px', background: '#eafaf1', borderRadius: 8,
                border: '1px solid #27ae60', marginBottom: 20, fontSize: 14, lineHeight: 1.6,
              }}>
                <strong>📊 Ne oldu?</strong> Grafınızda <strong>{m.uploaded_edges}</strong> bağlantı vardı.
                Spanner algoritması gereksiz bağlantıları temizleyerek sadece <strong>{m.spanner_edges}</strong> bağlantı bıraktı.
                Bu <strong>%{m.savings_pct} tasarruf</strong> demek — {savingsText} bir sonuç.
                Tüm kelimeler arasında zamansal yol hâlâ korunuyor ✅
              </div>
            );
          })()}

          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: 12, marginBottom: 24,
          }}>
            <MetricCard label="Yüklenen Bağlantı" value={result.metrics.uploaded_edges} desc="CSV'deki toplam kelime birlikteliği" />
            <MetricCard label="Olası Tüm Bağlantı" value={result.metrics.full_clique_edges} desc="Eğer her kelime her kelimeyle bağlantılı olsaydı" />
            <MetricCard label="Spanner'daki Bağlantı" value={result.metrics.spanner_edges} desc="Algoritmanın seçtiği minimum bağlantı sayısı" />
            <MetricCard label="Tasarruf" value={`${result.metrics.savings_pct}%`} desc="Gereksiz bağlantıların yüzdesi" />
            <MetricCard label="Düğüm Başına Bağlantı" value={result.metrics.ratio_per_n} desc="Her kelime için ortalama bağlantı sayısı" />
            <MetricCard label="Teorik Üst Sınır" value={result.metrics.bound_7n} desc="Makalenin kanıtladığı maksimum (7×düğüm)" />
            <MetricCard label="Doğrulama" value={result.metrics.verified ? 'Başarılı ✅' : 'Hata ❌'} desc="Tüm yollar korunuyor mu?" />
            <MetricCard label="Uzatma Faktörü" value={result.metrics.stretch_factor != null ? result.metrics.stretch_factor : '-'} desc="Spanner yolları orijinale göre kaç kat uzun?" />
          </div>

          {(() => {
            const cliques = maximalCliques(result.original.vertices, result.original.edges);
            const cmap = buildCliqueColorMap(result.original.vertices, cliques);
            return (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 32 }}>
                <GraphViewer graph={result.original} label={`Orijinal — Tüm Bağlantılar (${cliques.length} klik bulundu)`} height={450} colorMap={cmap} />
                <GraphViewer graph={result.spanner} label={`Spanner — Seyreltilmiş Ağ`} height={450} />
              </div>
            );
          })()}
        </>
      )}

      {view === 'trends' && trendData && (
        <div style={{ marginBottom: 32 }}>
          <TrendsView data={trendData} height={400} />
        </div>
      )}

      {view === 'explore' && (
        <div style={{ marginBottom: 32 }}>
          <ExploreView fullGraph={uploadInfo?.graph || currentGraph} />
        </div>
      )}

      {view === 'compare' && compareData && (
        <div>
          <div style={{
            padding: '14px 18px', background: '#f0f4ff', borderRadius: 8,
            border: '1px solid #4a90d9', marginBottom: 20, fontSize: 14, lineHeight: 1.6,
          }}>
            <strong>📊 Karşılaştırma:</strong> İki dönem arasında
            kelimelerin <strong>%{compareData.comparison.vertex_overlap_pct}'i</strong> ortak,
            bağlantıların <strong>%{compareData.comparison.edge_overlap_pct}'si</strong> ortak.
            Klik benzerliği: <strong>{compareData.comparison.clique_jaccard}</strong>.
            {compareData.comparison.savings_compare !== 'Equal' && (
              <> Spanner verimliliğinde <strong>{compareData.comparison.savings_compare}</strong>.</>
            )}
          </div>

          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
            gap: 12, marginBottom: 24,
          }}>
            <MetricCard label="Ortak Kelime" value={`${compareData.comparison.vertex_overlap_pct}%`} desc="İki dönemde de geçen kelimelerin oranı" />
            <MetricCard label="Ortak Bağlantı" value={`${compareData.comparison.edge_overlap_pct}%`} desc="İki dönemde de var olan birliktelikler" />
            <MetricCard label="Kazanan" value={compareData.comparison.savings_compare} desc="Hangi dönemin spanner'ı daha verimli?" />
            <MetricCard label="Klik Sayısı (A)" value={compareData.comparison.clique_count_1} desc="A dönemindeki kelime kümeleri" />
            <MetricCard label="Klik Sayısı (B)" value={compareData.comparison.clique_count_2} desc="B dönemindeki kelime kümeleri" />
            <MetricCard label="Klik Benzerliği" value={compareData.comparison.clique_jaccard} desc="1=tamamen aynı kümeler, 0=hiç ortak yok" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <div style={{
              background: '#f0f4ff', borderRadius: 8, padding: 12,
              border: '1px solid #d0d8ff',
            }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#4a90d9', marginBottom: 8 }}>
                A Dönemi — Detay
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <MetricCard label="Toplam Bağlantı" value={compareData.spanner1.metrics.uploaded_edges} />
                <MetricCard label="Spanner'da Kalan" value={compareData.spanner1.metrics.spanner_edges} />
                <MetricCard label="Tasarruf" value={`${compareData.spanner1.metrics.savings_pct}%`} />
                <MetricCard label="Düğüm Başı" value={compareData.spanner1.metrics.ratio_per_n} />
              </div>
            </div>
            <div style={{
              background: '#fff8f0', borderRadius: 8, padding: 12,
              border: '1px solid #ffe0b0',
            }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#e67e22', marginBottom: 8 }}>
                B Dönemi — Detay
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <MetricCard label="Toplam Bağlantı" value={compareData.spanner2.metrics.uploaded_edges} />
                <MetricCard label="Spanner'da Kalan" value={compareData.spanner2.metrics.spanner_edges} />
                <MetricCard label="Tasarruf" value={`${compareData.spanner2.metrics.savings_pct}%`} />
                <MetricCard label="Düğüm Başı" value={compareData.spanner2.metrics.ratio_per_n} />
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 32 }}>
            {(() => {
              const ca = maximalCliques(compareData.spanner1.original.vertices, compareData.spanner1.original.edges);
              const cb = maximalCliques(compareData.spanner2.original.vertices, compareData.spanner2.original.edges);
              const cma = buildCliqueColorMap(compareData.spanner1.original.vertices, ca);
              const cmb = buildCliqueColorMap(compareData.spanner2.original.vertices, cb);
              return (<>
                <GraphViewer graph={compareData.spanner1.spanner} label={`A Dönemi — Spanner (${ca.length} klik)`} height={400} colorMap={cma} />
                <GraphViewer graph={compareData.spanner2.spanner} label={`B Dönemi — Spanner (${cb.length} klik)`} height={400} colorMap={cmb} />
              </>);
            })()}
          </div>
        </div>
      )}

      <footer style={{ fontSize: 12, color: '#999', textAlign: 'center', marginTop: 48, padding: '16px 0', borderTop: '1px solid #eee' }}>
        Temporal Spanner Analyzer — Based on Baligács (2026)
      </footer>
    </div>
  );
}
