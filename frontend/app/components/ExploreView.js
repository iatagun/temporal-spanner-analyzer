'use client';

import { useState, useCallback } from 'react';
import { formatTime } from '../lib/utils';
import { searchWordCliques, checkClique } from '../lib/api';

export default function ExploreView({ fullGraph, onSample }) {
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
    try { setWordData(await searchWordCliques(fullGraph, wordQuery.trim(), 10)); }
    catch (e) { setWordError(e.message); }
    finally { setWordLoading(false); }
  }, [wordQuery, fullGraph]);

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
          {wordData && (
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                <strong className="text-gray-900 dark:text-gray-100">&ldquo;{wordData.word}&rdquo;</strong>:
                {wordData.cliques.length} klik, {wordData.total_snapshots} anlık-görüntü
              </div>
              <div className="flex flex-col gap-3">
                {wordData.cliques.map((c, i) => (
                  <div key={i} className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 bg-white dark:bg-gray-950">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1.5">{c.label}</div>
                    {c.description && <div className="text-xs text-gray-400 dark:text-gray-500 mb-2">{c.description}</div>}
                    <div className="flex gap-1 flex-wrap mb-3">
                      {c.members.map((m, j) => (
                        <span key={j} className={`px-1.5 py-0.5 rounded text-xs ${m === wordData.word ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>{m}</span>
                      ))}
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
            <div className={`p-4 rounded-lg border animate-in ${cliqueCheck.is_clique ? 'border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900' : 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/40'}`}>
              <div className={`text-sm font-medium mb-1 ${cliqueCheck.is_clique ? 'text-gray-900 dark:text-gray-100' : 'text-amber-800 dark:text-amber-400'}`}>
                {cliqueCheck.is_clique ? 'Tam Klik' : 'Tam Klik Değil'}
              </div>
              {cliqueCheck.is_clique && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {cliqueCheck.word_count} kelime, {cliqueCheck.edge_count} bağlantı (beklenen: {cliqueCheck.expected_edges})
                </div>
              )}
              {!cliqueCheck.is_clique && cliqueCheck.missing_edges && (
                <div className="text-xs text-amber-700 dark:text-amber-400 mt-2">
                  Eksik bağlantılar: {cliqueCheck.missing_edges.map((e, i) => <span key={i}>{e.join(' &mdash; ')}{i < cliqueCheck.missing_edges.length - 1 ? ', ' : ''}</span>)}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
