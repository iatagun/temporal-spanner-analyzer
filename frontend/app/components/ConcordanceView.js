'use client';

import { useMemo } from 'react';
import { formatTime } from '../lib/utils';

// Splits `text` on the query words (case-insensitive, word-boundary aware)
// so they can be rendered bold -- a manual scan instead of one combined
// regex so words containing regex metacharacters (rare, but corpora are
// user data) can't break the match.
function highlightSegments(text, words) {
  if (!text) return [{ text: '', hit: false }];
  const wordSet = new Set(words.map(w => w.toLowerCase()));
  const tokens = text.split(/(\s+)/);
  return tokens.map(tok => ({
    text: tok,
    hit: wordSet.has(tok.toLowerCase().replace(/[.,;:!?"'()]/g, '')),
  }));
}

export default function ConcordanceView({ rawDocuments, words, onClose }) {
  const matches = useMemo(() => {
    if (!rawDocuments || !words || words.length === 0) return [];
    const wordSet = new Set(words.map(w => w.toLowerCase()));
    return rawDocuments
      .filter(doc => doc.words && wordSet.size > 0 && [...wordSet].every(w => doc.words.some(dw => dw.toLowerCase() === w)))
      .filter(doc => doc.text);
  }, [rawDocuments, words]);

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 bg-white dark:bg-gray-950 animate-in">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
          Bağlamda: {words.join(', ')} ({matches.length} eşleşme)
        </div>
        {onClose && (
          <button onClick={onClose} className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            Kapat
          </button>
        )}
      </div>
      {matches.length === 0 && (
        <div className="text-xs text-gray-400 dark:text-gray-500">
          Bu kelimeler için saklanmış cümle metni bulunamadı.
        </div>
      )}
      <div className="flex flex-col gap-2 max-h-96 overflow-y-auto">
        {matches.map((doc, i) => (
          <div key={i} className="text-xs text-gray-600 dark:text-gray-400 border-b border-gray-100 dark:border-gray-800 pb-2 last:border-0">
            <div className="text-[10px] text-gray-400 dark:text-gray-500 mb-0.5">{formatTime(doc.label)}</div>
            <div>
              {highlightSegments(doc.text, words).map((seg, j) => (
                seg.hit
                  ? <strong key={j} className="text-gray-900 dark:text-gray-100 bg-[var(--color-warning-bg)] px-0.5 rounded">{seg.text}</strong>
                  : <span key={j}>{seg.text}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
