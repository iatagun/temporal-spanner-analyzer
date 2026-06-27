'use client';

export default function Header() {
  return (
    <header className="mb-8">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 bg-gray-900 flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h1 className="text-xl font-semibold tracking-tight text-gray-900">
          Temporal Spanner Analyzer
        </h1>
      </div>
      <p className="text-sm text-gray-500 max-w-2xl leading-relaxed ml-11">
        Derlem dilbiliminde kavramlarin zamansal evrimini analiz eden bir arac.
        Baligacs (2026) lineer spanner algoritmasiyla kelime birlikteliklerini
        seyrek zamanli cizgelere indirger; kavram kumelerinin dogum, buyume ve
        kaybolus sureclerini gorunur kilar.
      </p>
      <div className="flex gap-3 mt-3 ml-11 text-xs text-gray-400">
        <span>Girdi: CSV, JSON, CoNLL-U, VRT</span>
        <span>&middot;</span>
        <span>Cikti: Spanner cizgeler, trend grafikleri, karsilastirma, kesif</span>
      </div>
    </header>
  );
}
