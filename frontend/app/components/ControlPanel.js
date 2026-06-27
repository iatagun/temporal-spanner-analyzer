'use client';

import { useRef, useState } from 'react';

export default function ControlPanel({
  loading, onUpload, minFreq, setMinFreq, onSample,
}) {
  const fileRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  return (
    <div className="mb-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragOver ? 'border-gray-400 bg-gray-50' : 'border-gray-200 bg-white'
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
        <div className="text-sm text-gray-500 mb-3">
          CoNLL-U, VRT, CSV veya JSON dosyasi surukleyin
        </div>

        <div className="flex items-center justify-center gap-3">
          <label className="inline-block px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-md cursor-pointer hover:bg-gray-800 transition-colors">
            Dosya Sec
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

          <span className="text-xs text-gray-400">veya</span>

          <button
            onClick={onSample}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 text-sm text-gray-600 font-medium rounded-md hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Ornek Veri ile Dene
          </button>
        </div>

        <div className="mt-3 text-xs text-gray-400">
          .conllu .vrt .csv .json
        </div>
      </div>

      <div className="flex items-center gap-4 mt-3 ml-1">
        <label className="flex items-center gap-2 text-xs text-gray-500">
          Min Frekans
          <input
            type="number" min={1} max={20} value={minFreq}
            onChange={e => setMinFreq(Math.max(1, Number(e.target.value)))}
            className="w-16 px-2 py-1.5 border border-gray-200 rounded text-xs bg-white"
          />
        </label>

        {loading && (
          <span className="text-xs text-gray-400 flex items-center gap-1.5">
            <svg className="animate-spin w-3 h-3" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Isleniyor...
          </span>
        )}
      </div>
    </div>
  );
}
