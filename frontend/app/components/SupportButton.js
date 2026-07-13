'use client';

import { useState } from 'react';

const IBAN = 'TR56 0082 9000 0949 1613 1254 40';

// Shared between the tool's Header and the landing page's Nav -- same
// IBAN-copy mechanic in both places, extracted so there's one definition
// instead of two independently-maintained copies.
export default function SupportButton() {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(IBAN);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div className="relative">
      <button
        onClick={handleCopy}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium
                   rounded-lg bg-amber-50 text-amber-700 border border-amber-200
                   hover:bg-amber-100 hover:border-amber-300 transition-colors cursor-pointer
                   dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800 dark:hover:bg-amber-950/60"
        title="IBAN'ı panoya kopyala"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
        <span>Destek Ol</span>
      </button>
      {copied && (
        <div className="absolute top-full right-0 mt-2 w-72 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 shadow-lg animate-in fade-in slide-in-from-top-2 z-50 dark:bg-amber-950/60 dark:border-amber-800 dark:text-amber-300">
          <p className="text-xs text-amber-600 dark:text-amber-400">IBAN kopyalandı. Kahveni yudumlarken bu araca emek veren bir insan olduğunu hatırladığın için çok teşekkür ederim :)</p>
        </div>
      )}
    </div>
  );
}
