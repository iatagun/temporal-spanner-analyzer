'use client';

import { useRef } from 'react';

export default function ControlPanel({
  mode, setMode, n, setN, seed, setSeed,
  loading, onSynthetic, onUpload, minFreq, setMinFreq,
}) {
  const fileRef = useRef(null);

  return (
    <div className="bg-white rounded-2xl border border-border shadow-sm shadow-slate-200/50 p-6 mb-6">
      <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit mb-6">
        <button
          onClick={() => setMode('synthetic')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
            mode === 'synthetic'
              ? 'bg-white text-primary shadow-sm'
              : 'text-text-muted hover:text-text hover:bg-white/50'
          }`}
        >
          Synthetic
        </button>
        <button
          onClick={() => setMode('upload')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
            mode === 'upload'
              ? 'bg-white text-primary shadow-sm'
              : 'text-text-muted hover:text-text hover:bg-white/50'
          }`}
        >
          CSV Upload
        </button>
      </div>

      {mode === 'synthetic' ? (
        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">
              Vertices (n)
            </label>
            <input
              type="number" min={2} max={80} value={n}
              onChange={e => setN(Number(e.target.value))}
              className="w-24 px-3 py-2.5 border border-border rounded-lg text-sm bg-slate-50 
                         focus:bg-white transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">
              Seed
            </label>
            <input
              type="number" value={seed}
              onChange={e => setSeed(Number(e.target.value))}
              className="w-24 px-3 py-2.5 border border-border rounded-lg text-sm bg-slate-50 
                         focus:bg-white transition-colors"
            />
          </div>
          <button
            onClick={onSynthetic}
            disabled={loading}
            className="px-6 py-2.5 bg-gradient-to-r from-primary to-primary-dark text-white rounded-lg 
                       text-sm font-semibold shadow-md shadow-primary/25 hover:shadow-lg hover:shadow-primary/30
                       disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Computing...
              </span>
            ) : 'Compute Spanner'}
          </button>
        </div>
      ) : (
        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">
              CSV File (date, words)
            </label>
            <input
              type="file" accept=".csv,.json" ref={fileRef}
              className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 
                         file:text-sm file:font-semibold file:bg-primary file:text-white 
                         file:hover:bg-primary-dark file:transition-colors file:cursor-pointer
                         text-text-muted"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">
              Min Freq
            </label>
            <input
              type="number" min={1} max={20} value={minFreq}
              onChange={e => setMinFreq(Math.max(1, Number(e.target.value)))}
              className="w-20 px-3 py-2.5 border border-border rounded-lg text-sm bg-slate-50 
                         focus:bg-white transition-colors"
            />
          </div>
          <button
            onClick={() => onUpload(fileRef.current?.files?.[0])}
            disabled={loading}
            className="px-6 py-2.5 bg-gradient-to-r from-accent to-primary text-white rounded-lg 
                       text-sm font-semibold shadow-md shadow-accent/25 hover:shadow-lg hover:shadow-accent/30
                       disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Processing...
              </span>
            ) : 'Upload CSV'}
          </button>
        </div>
      )}
    </div>
  );
}
