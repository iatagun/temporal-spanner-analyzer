'use client';

import { useState } from 'react';

const IBAN = 'TR56 0082 9000 0949 1613 1254 40';

export default function Header() {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(IBAN);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <header className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <svg className="w-8 h-8 text-gray-900 dark:text-gray-100 flex-shrink-0" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <circle cx="6" cy="9" r="2" fill="currentColor" />
            <circle cx="6" cy="23" r="2" fill="currentColor" />
            <circle cx="15" cy="16" r="2" fill="currentColor" />
            <circle cx="26" cy="16" r="2" fill="currentColor" />
            <path d="M6 9 L6 23 M6 9 L15 16 M6 23 L15 16 M15 16 L26 16"
              stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
          <h1 className="font-serif text-2xl font-medium tracking-tight text-gray-900 dark:text-gray-100">
            Temporal Spanner Analyzer
          </h1>
        </div>
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
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-2xl leading-relaxed ml-11">
        Derlem dilbiliminde kavramların zamansal evrimini analiz eden bir araç.
        Baligács (2026) lineer spanner algoritmasıyla kelime birlikteliklerini
        seyrek zamanlı çizgelere indirger; kavram kümelerinin doğum, büyüme ve
        kayboluş süreçlerini görünür kılar.
      </p>
      <div className="flex gap-3 mt-3 ml-11 text-xs text-gray-400 dark:text-gray-500">
        <span>Girdi: CSV, JSON, CoNLL-U, VRT</span>
        <span>&middot;</span>
        <span>Çıktı: Spanner çizgeler, trend grafikleri, karşılaştırma, keşif</span>
      </div>
    </header>
  );
}
