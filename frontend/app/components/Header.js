'use client';

import Link from 'next/link';

export default function Header() {
  return (
    <header className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <Link href="/" className="flex items-center gap-3">
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
        </Link>
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
