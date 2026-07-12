'use client';

import { useRef, useState } from 'react';

export default function ControlPanel({
  loading, onUpload, minFreq, setMinFreq, onSample,
  minCliqueSize, setMinCliqueSize, maxCliques, setMaxCliques,
  pmiThreshold, setPmiThreshold,
  showAdvanced, setShowAdvanced,
}) {
  const fileRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  return (
    <div className="mb-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragOver ? 'border-gray-400 bg-gray-50 dark:border-gray-500 dark:bg-gray-900' : 'border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const file = e.dataTransfer.files?.[0];
          if (file) onUpload(file);
        }}
      >
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          CoNLL-U, VRT, CSV veya JSON dosyası sürükleyin
        </div>

        <div className="flex items-center justify-center gap-3">
          <label className="inline-block px-4 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md cursor-pointer hover:bg-gray-800 dark:hover:bg-gray-300 transition-colors">
            Dosya Seç
            <input
              type="file"
              accept=".csv,.json,.conllu,.conll,.vrt"
              ref={fileRef}
              className="hidden"
              onChange={() => {
                const file = fileRef.current?.files?.[0];
                if (file) onUpload(file);
              }}
            />
          </label>

          <span className="text-xs text-gray-400 dark:text-gray-500">veya</span>

          <button
            onClick={onSample}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300 font-medium rounded-md hover:bg-gray-50 dark:hover:bg-gray-900 disabled:opacity-50 transition-colors"
          >
            Örnek Veri ile Dene
          </button>
        </div>

        <div className="mt-3 text-xs text-gray-400 dark:text-gray-500">
          .conllu .vrt .csv .json
        </div>
      </div>

      <div className="flex items-center gap-4 mt-3 ml-1">
        <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          Min Frekans
          <input
            type="number" min={1} max={20} value={minFreq}
            onChange={e => setMinFreq(Math.max(1, Number(e.target.value)))}
            className="w-16 px-2 py-1.5 border border-gray-200 dark:border-gray-700 rounded text-xs bg-white dark:bg-gray-900 dark:text-gray-100"
          />
        </label>

        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-xs text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
        >
          {showAdvanced ? 'Gelişmiş ▲' : 'Gelişmiş ▼'}
        </button>

        {loading && (
          <span className="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <svg className="animate-spin w-3 h-3" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            İşleniyor...
          </span>
        )}
      </div>

      {showAdvanced && (
        <div className="mt-2 ml-1 animate-in">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              Min Klik Boyutu
              <input
                type="number" min={2} max={10} value={minCliqueSize}
                onChange={e => setMinCliqueSize(Math.max(2, Number(e.target.value)))}
                className="w-16 px-2 py-1.5 border border-gray-200 dark:border-gray-700 rounded text-xs bg-white dark:bg-gray-900 dark:text-gray-100"
              />
            </label>
            <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              Maks Klik
              <input
                type="number" min={0} max={5000} value={maxCliques}
                onChange={e => setMaxCliques(Math.max(0, Number(e.target.value)))}
                placeholder="0=sınırsız"
                className="w-20 px-2 py-1.5 border border-gray-200 dark:border-gray-700 rounded text-xs bg-white dark:bg-gray-900 dark:text-gray-100"
              />
            </label>
            <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              PMI Eşiği
              <input
                type="number" min={-1} max={1} step={0.05} value={pmiThreshold}
                onChange={e => setPmiThreshold(Math.min(1, Math.max(-1, Number(e.target.value))))}
                className="w-16 px-2 py-1.5 border border-gray-200 dark:border-gray-700 rounded text-xs bg-white dark:bg-gray-900 dark:text-gray-100"
              />
            </label>
          </div>
          <ul className="mt-2 space-y-0.5 text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
            <li><strong className="text-gray-500 dark:text-gray-400 font-medium">Min Klik Boyutu</strong> — spanner'a dahil edilecek en küçük kelime kümesi büyüklüğü.</li>
            <li><strong className="text-gray-500 dark:text-gray-400 font-medium">Maks Klik</strong> — işlenecek klik sayısı üst sınırı (0 = sınırsız).</li>
            <li><strong className="text-gray-500 dark:text-gray-400 font-medium">PMI Eşiği</strong> — kelime çiftinin kenar sayılması için gereken minimum NPMI anlamlılık skoru (-1..1). Yükleme anında uygulanır, dosyayı yeniden yüklemeniz gerekir.</li>
          </ul>
        </div>
      )}
    </div>
  );
}
