'use client';

import { useState, useCallback, useMemo } from 'react';
import { formatTime, significanceLabel, isTScoreSignificant } from '../lib/utils';
import { searchWordCliques, checkClique, fetchMweCandidates, fetchPairConfidence } from '../lib/api';
import TruncatedWarning from './TruncatedWarning';
import ConcordanceView from './ConcordanceView';

const MEASURE_SHORT_LABELS = { npmi: 'NPMI', log_likelihood: 'G²', dice: 'Dice', t_score: 't' };

// adjacency_ratio is informational (multi-word-expression detection, see
// isMultiWordExpression below); p_value/p_value_fdr/p_value_bonferroni are
// derived from log_likelihood and folded into its own label instead of
// listed separately -- none of these are comparable association measures
// in the generic "NPMI x · G² y" list.
const HIDDEN_SCORE_KEYS = new Set(['adjacency_ratio', 'p_value', 'p_value_fdr', 'p_value_bonferroni']);

function formatScores(scores) {
  if (!scores) return null;
  return Object.entries(scores)
    .filter(([key]) => !HIDDEN_SCORE_KEYS.has(key))
    .map(([key, value]) => {
      let label = `${MEASURE_SHORT_LABELS[key] || key} ${value.toFixed(2)}`;
      if (key === 'log_likelihood') {
        const sig = significanceLabel(value);
        if (sig) {
          // Testing many pairs at once inflates false positives at raw
          // p<0.05 -- the FDR-corrected verdict (Benjamini-Hochberg, see
          // graph_builder.compute_association_measures) is the one that
          // actually accounts for that, shown alongside the raw label
          // rather than replacing it so both are visible.
          const fdr = scores.p_value_fdr;
          const fdrNote = typeof fdr === 'number' ? (fdr <= 0.05 ? ', FDR: anlamlı' : ', FDR: anlamlı değil') : '';
          label += ` (${sig}${fdrNote})`;
        }
      } else if (key === 't_score' && isTScoreSignificant(value)) {
        label += ' (p<0.05)';
      }
      return label;
    })
    .join(' · ');
}

// >=50% of this pair's co-occurrences were immediate neighbors -- a
// necessary condition for a fixed multi-word expression like "yapay
// zeka", not just two words that happen to appear in the same sentence.
function isMultiWordExpression(scores) {
  return !!scores && typeof scores.adjacency_ratio === 'number' && scores.adjacency_ratio >= 0.5;
}

export default function ExploreView({ fullGraph, onSample, rawDocuments, pmiThreshold, associationMeasure }) {
  const hasGraph = fullGraph && fullGraph.vertices && fullGraph.vertices.length > 0;
  const [activeView, setActiveView] = useState('word');

  const [wordQuery, setWordQuery] = useState('');
  const [wordData, setWordData] = useState(null);
  const [wordLoading, setWordLoading] = useState(false);
  const [wordError, setWordError] = useState(null);

  const [cliqueWords, setCliqueWords] = useState('');
  const [cliqueCheck, setCliqueCheck] = useState(null);
  const [cliqueLoading, setCliqueLoading] = useState(false);
  const [cliqueError, setCliqueError] = useState(null);
  const [concordanceQuery, setConcordanceQuery] = useState(null);

  const [mweData, setMweData] = useState(null);
  const [mweLoading, setMweLoading] = useState(false);
  const [mweError, setMweError] = useState(null);

  // Keyed by "w1 w2" (same ordering convention as edgeScoreMap) -- each
  // pair's confidence interval is fetched on demand (see
  // graph_builder.bootstrap_confidence_interval's docstring for why this
  // is never computed automatically for every pair), so state lives per
  // pair rather than as one shared loading/error/result triple.
  const [confidenceMap, setConfidenceMap] = useState({});

  // Every edge already carries all four association measures (computed
  // once at upload, see graph_builder.compute_association_measures) --
  // no extra request needed to show them next to a search result.
  const edgeScoreMap = useMemo(() => {
    const map = {};
    if (!fullGraph?.edges) return map;
    for (const e of fullGraph.edges) {
      if (!e.scores || Object.keys(e.scores).length === 0) continue;
      const key = e.u <= e.v ? `${e.u} ${e.v}` : `${e.v} ${e.u}`;
      map[key] = e.scores;
    }
    return map;
  }, [fullGraph]);

  const searchWord = useCallback(async () => {
    if (!wordQuery.trim() || !fullGraph) return;
    setWordLoading(true); setWordError(null);
    try { setWordData(await searchWordCliques(fullGraph, wordQuery.trim(), 10, { rawDocuments, pmiThreshold, associationMeasure })); }
    catch (e) { setWordError(e.message); }
    finally { setWordLoading(false); }
  }, [wordQuery, fullGraph, rawDocuments, pmiThreshold, associationMeasure]);

  const searchMwe = useCallback(async () => {
    if (!rawDocuments || rawDocuments.length === 0) return;
    setMweLoading(true); setMweError(null);
    try { setMweData(await fetchMweCandidates(rawDocuments)); }
    catch (e) { setMweError(e.message); }
    finally { setMweLoading(false); }
  }, [rawDocuments]);

  const fetchConfidence = useCallback(async (key, w1, w2) => {
    if (!rawDocuments || rawDocuments.length === 0) return;
    setConfidenceMap(prev => ({ ...prev, [key]: { loading: true, error: null, result: prev[key]?.result || null } }));
    try {
      const result = await fetchPairConfidence(rawDocuments, w1, w2, { associationMeasure });
      setConfidenceMap(prev => ({ ...prev, [key]: { loading: false, error: null, result } }));
    } catch (e) {
      setConfidenceMap(prev => ({ ...prev, [key]: { loading: false, error: e.message, result: null } }));
    }
  }, [rawDocuments, associationMeasure]);

  const checkCliqueHandler = useCallback(async () => {
    const words = cliqueWords.split(',').map(w => w.trim()).filter(Boolean);
    if (words.length < 2 || !fullGraph) return;
    setCliqueLoading(true); setCliqueError(null);
    try { setCliqueCheck(await checkClique(fullGraph, words)); }
    catch (e) { setCliqueError(e.message); }
    finally { setCliqueLoading(false); }
  }, [cliqueWords, fullGraph]);

  if (!hasGraph) {
    return (
      <div className="py-16 text-center border border-gray-200 dark:border-gray-800 rounded-lg">
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">Henüz bir veri yüklenmedi</div>
        {onSample && (
          <button onClick={onSample}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            Örnek Veri ile Dene
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="flex border-b border-gray-200 dark:border-gray-800 mb-5">
        <button onClick={() => setActiveView('word')}
          className={`px-4 py-2 text-sm border-b-2 -mb-px transition-colors ${activeView === 'word' ? 'border-gray-900 text-gray-900 font-medium dark:border-gray-100 dark:text-gray-100' : 'border-transparent text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300'}`}>
          Kelime Klikleri
        </button>
        <button onClick={() => setActiveView('check')}
          className={`px-4 py-2 text-sm border-b-2 -mb-px transition-colors ${activeView === 'check' ? 'border-gray-900 text-gray-900 font-medium dark:border-gray-100 dark:text-gray-100' : 'border-transparent text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300'}`}>
          Klik Kontrol
        </button>
        <button onClick={() => setActiveView('mwe')}
          className={`px-4 py-2 text-sm border-b-2 -mb-px transition-colors ${activeView === 'mwe' ? 'border-gray-900 text-gray-900 font-medium dark:border-gray-100 dark:text-gray-100' : 'border-transparent text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300'}`}>
          MWE Adayları
        </button>
      </div>

      {activeView === 'word' && (
        <div className="animate-in">
          <div className="flex gap-3 items-end mb-5">
            <div className="flex-1">
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Kelime Ara</label>
              <input type="text" value={wordQuery} onChange={e => setWordQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && searchWord()}
                placeholder="örnek: yapay"
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md text-sm bg-white dark:bg-gray-900 dark:text-gray-100 focus:border-gray-400 dark:focus:border-gray-500 outline-none transition-colors" />
            </div>
            <button onClick={searchWord} disabled={wordLoading || !wordQuery.trim()}
              className="px-4 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              {wordLoading ? 'Aranıyor...' : 'Ara'}
            </button>
          </div>
          {wordError && <div className="p-3 mb-4 border border-red-200 dark:border-red-900 rounded-md bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 text-sm animate-in">{wordError}</div>}
          {concordanceQuery && (
            <div className="mb-4">
              <ConcordanceView rawDocuments={rawDocuments} words={concordanceQuery} onClose={() => setConcordanceQuery(null)} />
            </div>
          )}
          {wordData && (
            <div>
              {wordData.truncated && <TruncatedWarning />}
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                <strong className="text-gray-900 dark:text-gray-100">&ldquo;{wordData.word}&rdquo;</strong>:
                {wordData.cliques.length} klik, {wordData.total_snapshots} anlık-görüntü
              </div>
              <div className="flex flex-col gap-3">
                {wordData.cliques.map((c, i) => (
                  <div key={i} className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 bg-white dark:bg-gray-950">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{c.label}</div>
                      {rawDocuments && rawDocuments.length > 0 && (
                        <button
                          onClick={() => setConcordanceQuery(c.members)}
                          className="text-xs text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                        >
                          Bağlamda gör
                        </button>
                      )}
                    </div>
                    {c.description && <div className="text-xs text-gray-400 dark:text-gray-500 mb-2">{c.description}</div>}
                    <div className="flex gap-1 flex-wrap mb-3">
                      {c.members.map((m, j) => (
                        <span key={j} className={`px-1.5 py-0.5 rounded text-xs ${m === wordData.word ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>{m}</span>
                      ))}
                    </div>
                    <div className="flex flex-col gap-0.5 mb-3">
                      {c.members.filter(m => m !== wordData.word).map((m, j) => {
                        const key = wordData.word <= m ? `${wordData.word} ${m}` : `${m} ${wordData.word}`;
                        const scores = edgeScoreMap[key];
                        if (!scores) return null;
                        const conf = confidenceMap[key];
                        return (
                          <div key={j} className="text-[11px] text-gray-400 dark:text-gray-500 flex items-center gap-1.5 flex-wrap">
                            <span>{wordData.word} &ndash; {m}: {formatScores(scores)}</span>
                            {isMultiWordExpression(scores) && (
                              <span
                                className="px-1 py-0 rounded bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning-border)]"
                                title="Bu çift co-occurrence'larının çoğunda birbirine bitişik geçiyor -- sabit bir çok kelimeli birim (örn. bileşik ad) olabilir."
                              >
                                çok kelimeli birim
                              </span>
                            )}
                            {rawDocuments && rawDocuments.length > 0 && (
                              conf?.result ? (
                                <span className="tabular-nums">
                                  [{conf.result.lower.toFixed(2)}, {conf.result.upper.toFixed(2)}]
                                </span>
                              ) : (
                                <button
                                  onClick={() => fetchConfidence(key, wordData.word, m)}
                                  disabled={conf?.loading}
                                  className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 underline decoration-dotted disabled:opacity-50 transition-colors"
                                >
                                  {conf?.loading ? 'hesaplanıyor...' : 'güven aralığı hesapla'}
                                </button>
                              )
                            )}
                            {conf?.error && <span className="text-red-500 dark:text-red-400">{conf.error}</span>}
                          </div>
                        );
                      })}
                    </div>
                    {c.snapshots && (
                      <div className="flex gap-1 flex-wrap">
                        {c.snapshots.map((s, j) => (
                          <span key={j} className="px-1.5 py-0.5 bg-gray-50 dark:bg-gray-900 rounded text-xs text-gray-500 dark:text-gray-400 border border-gray-100 dark:border-gray-800"
                            title={s.members.join(', ')}>
                            w{s.window} ({s.size}): {formatTime(s.window_start)}-{formatTime(s.window_end)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeView === 'check' && (
        <div className="animate-in">
          <div className="flex gap-3 items-end mb-5">
            <div className="flex-1">
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Kelimeler (virgülle ayırın)</label>
              <input type="text" value={cliqueWords} onChange={e => setCliqueWords(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && checkCliqueHandler()}
                placeholder="örnek: yapay, zeka, veri"
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md text-sm bg-white dark:bg-gray-900 dark:text-gray-100 focus:border-gray-400 dark:focus:border-gray-500 outline-none transition-colors" />
            </div>
            <button onClick={checkCliqueHandler} disabled={cliqueLoading || cliqueWords.split(',').filter(Boolean).length < 2}
              className="px-4 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              {cliqueLoading ? 'Kontrol...' : 'Kontrol Et'}
            </button>
          </div>
          {cliqueError && <div className="p-3 mb-4 border border-red-200 dark:border-red-900 rounded-md bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 text-sm animate-in">{cliqueError}</div>}
          {cliqueCheck && (
            <div className={`p-4 rounded-lg border animate-in ${cliqueCheck.is_clique ? 'border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900' : 'border-[var(--color-warning-border)] bg-[var(--color-warning-bg)]'}`}>
              <div className={`text-sm font-medium mb-1 ${cliqueCheck.is_clique ? 'text-gray-900 dark:text-gray-100' : 'text-[var(--color-warning)]'}`}>
                {cliqueCheck.is_clique ? 'Tam Klik' : 'Tam Klik Değil'}
              </div>
              {cliqueCheck.is_clique && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {cliqueCheck.word_count} kelime, {cliqueCheck.edge_count} bağlantı (beklenen: {cliqueCheck.expected_edges})
                </div>
              )}
              {!cliqueCheck.is_clique && cliqueCheck.missing_edges && (
                <div className="text-xs text-[var(--color-warning)] mt-2">
                  Eksik bağlantılar: {cliqueCheck.missing_edges.map((e, i) => <span key={i}>{e.join(' &mdash; ')}{i < cliqueCheck.missing_edges.length - 1 ? ', ' : ''}</span>)}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeView === 'mwe' && (
        <div className="animate-in">
          <div className="text-xs text-gray-400 dark:text-gray-500 mb-4">
            Ardışık kelime dizilerini (2-4 kelime) C-value (Frantzi &amp; Ananiadou 1996)
            ile sıralar -- iç içe geçen adaylar (örn. &quot;yapay zeka&quot;nın hep daha uzun
            &quot;yapay zeka modeli&quot; içinde geçmesi) düşük puan alır.
          </div>
          {!rawDocuments || rawDocuments.length === 0 ? (
            <div className="text-sm text-gray-400 dark:text-gray-500">
              Bu analiz ham doküman metnine ihtiyaç duyuyor -- CoNLL-U/VRT/CSV/JSON yükleyin.
            </div>
          ) : (
            <button onClick={searchMwe} disabled={mweLoading}
              className="px-4 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4">
              {mweLoading ? 'Hesaplanıyor...' : 'MWE Adaylarını Hesapla'}
            </button>
          )}
          {mweError && <div className="p-3 mb-4 border border-red-200 dark:border-red-900 rounded-md bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 text-sm animate-in">{mweError}</div>}
          {mweData && (
            <div className="flex flex-col gap-1">
              {mweData.candidates.length === 0 && (
                <div className="text-sm text-gray-400 dark:text-gray-500">Aday bulunamadı.</div>
              )}
              {mweData.candidates.map((c, i) => (
                <div key={i} className="flex items-center justify-between border border-gray-200 dark:border-gray-800 rounded-md px-3 py-1.5 bg-white dark:bg-gray-950">
                  <span className="text-sm text-gray-900 dark:text-gray-100">{c.text}</span>
                  <span className="text-xs text-gray-400 dark:text-gray-500 tabular-nums">
                    C={c.c_value.toFixed(2)} · f={c.frequency}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
