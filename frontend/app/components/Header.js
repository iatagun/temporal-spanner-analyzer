'use client';

export default function Header() {
  return (
    <header className="mb-8">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/25">
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-text tracking-tight">Temporal Spanner Analyzer</h1>
          <p className="text-sm text-text-muted mt-0.5">
            Balig&aacute;cs (2026) &mdash; Temporal clique &rarr; linear spanner. Full clique &le; 7n edges.
          </p>
        </div>
      </div>
    </header>
  );
}
