'use client';

import { useState, useCallback } from 'react';
import { formatTime } from '../lib/utils';
import { searchWordCliques, checkClique } from '../lib/api';

export default function ExploreView({ fullGraph }) {
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

  const searchWord = useCallback(async () => {
    if (!wordQuery.trim() || !fullGraph) return;
    setWordLoading(true); setWordError(null);
    try {
      setWordData(await searchWordCliques(fullGraph, wordQuery.trim(), 10));
    } catch (e) {
      setWordError(e.message);
    } finally {
      setWordLoading(false);
    }
  }, [wordQuery, fullGraph]);

  const checkCliqueHandler = useCallback(async () => {
    const words = cliqueWords.split(',').map(w => w.trim()).filter(Boolean);
    if (words.length < 2 || !fullGraph) return;
    setCliqueLoading(true); setCliqueError(null);
    try {
      setCliqueCheck(await checkClique(fullGraph, words));
    } catch (e) {
      setCliqueError(e.message);
    } finally {
      setCliqueLoading(false);
    }
  }, [cliqueWords, fullGraph]);

  if (!hasGraph) {
    return (
      <div className="py-12 text-center text-text-muted bg-slate-50 rounded-xl text-sm">
        No graph data available. Upload a CSV or generate a synthetic graph first.
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit mb-5">
        <button onClick={() => setActiveView('word')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${activeView === 'word' ? 'bg-white text-primary shadow-sm' : 'text-text-muted hover:text-text hover:bg-white/50'}`}>
          Word Cliques
        </button>
        <button onClick={() => setActiveView('check')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${activeView === 'check' ? 'bg-white text-primary shadow-sm' : 'text-text-muted hover:text-text hover:bg-white/50'}`}>
          Check Clique
        </button>
      </div>

      {activeView === 'word' && (
        <div className="animate-fade-in">
          <div className="flex gap-3 items-end mb-5">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">Search Word</label>
              <input type="text" value={wordQuery}
                onChange={e => setWordQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && searchWord()}
                placeholder="e.g. yapay"
                className="w-full px-4 py-2.5 border border-border rounded-lg text-sm bg-slate-50 focus:bg-white transition-colors" />
            </div>
            <button onClick={searchWord} disabled={wordLoading || !wordQuery.trim()}
              className="px-5 py-2.5 bg-gradient-to-r from-primary to-primary-dark text-white rounded-lg text-sm font-semibold shadow-md shadow-primary/25 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">
              {wordLoading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {wordError && (
            <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-fade-in">
              {wordError}
            </div>
          )}

          {wordData && (
            <div>
              <div className="text-sm text-text-muted mb-4">
                <strong className="text-text">&ldquo;{wordData.word}&rdquo;</strong> appears in{' '}
                <strong className="text-text">{wordData.cliques.length}</strong> cliques
                across <strong className="text-text">{wordData.total_snapshots}</strong> snapshots
              </div>
              <div className="flex flex-col gap-3">
                {wordData.cliques.map((c, i) => (
                  <div key={i} className="bg-white border border-border rounded-xl p-4 hover:shadow-md transition-shadow">
                    <div className="text-sm font-semibold text-text mb-2">{c.label}</div>
                    {c.description && (
                      <div className="text-xs text-text-muted mb-2">{c.description}</div>
                    )}
                    <div className="flex gap-1.5 flex-wrap mb-3">
                      {c.members.map((m, j) => (
                        <span key={j} className={`px-2 py-0.5 rounded-md text-xs font-medium ${m === wordData.word ? 'bg-primary text-white' : 'bg-slate-100 text-text'}`}>
                          {m}
                        </span>
                      ))}
                    </div>
                    {c.snapshots && (
                      <div className="flex gap-1.5 flex-wrap">
                        {c.snapshots.map((s, j) => (
                          <span key={j} className="px-2 py-1 rounded-md text-xs bg-accent/10 text-accent font-medium"
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

          {!wordData && !wordLoading && !wordError && (
            <div className="py-12 text-center text-text-muted text-sm">
              Search for a word to see which cliques contain it
            </div>
          )}
        </div>
      )}

      {activeView === 'check' && (
        <div className="animate-fade-in">
          <div className="flex gap-3 items-end mb-5">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">Words (comma-separated)</label>
              <input type="text" value={cliqueWords}
                onChange={e => setCliqueWords(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && checkCliqueHandler()}
                placeholder="e.g. yapay, zeka, veri"
                className="w-full px-4 py-2.5 border border-border rounded-lg text-sm bg-slate-50 focus:bg-white transition-colors" />
            </div>
            <button onClick={checkCliqueHandler} disabled={cliqueLoading || cliqueWords.split(',').filter(Boolean).length < 2}
              className="px-5 py-2.5 bg-gradient-to-r from-accent to-primary text-white rounded-lg text-sm font-semibold shadow-md shadow-accent/25 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200">
              {cliqueLoading ? 'Checking...' : 'Check'}
            </button>
          </div>

          {cliqueError && (
            <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-fade-in">
              {cliqueError}
            </div>
          )}

          {cliqueCheck && (
            <div className={`p-5 rounded-xl border ${cliqueCheck.is_clique ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'} animate-fade-in`}>
              <div className={`text-lg font-bold mb-2 ${cliqueCheck.is_clique ? 'text-emerald-700' : 'text-amber-700'}`}>
                {cliqueCheck.is_clique ? 'Tam Clique' : 'Tam Clique Degil'}
              </div>
              {cliqueCheck.is_clique && (
                <div className="text-sm text-emerald-800">
                  Word count: <strong>{cliqueCheck.word_count}</strong>
                  {' | '}Edge count: <strong>{cliqueCheck.edge_count}</strong>
                  {' | '}Expected: <strong>{cliqueCheck.expected_edges}</strong>
                </div>
              )}
              {!cliqueCheck.is_clique && cliqueCheck.missing_edges && (
                <div className="text-sm text-amber-800 mt-2">
                  <div className="font-semibold mb-1">Missing edges:</div>
                  <div className="flex flex-col gap-0.5">
                    {cliqueCheck.missing_edges.map((e, i) => (
                      <span key={i} className="text-xs">{e.join(' — ')}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {!cliqueCheck && !cliqueLoading && !cliqueError && (
            <div className="py-12 text-center text-text-muted text-sm">
              Enter a set of words to check if they form a temporal clique
            </div>
          )}
        </div>
      )}
    </div>
  );
}
