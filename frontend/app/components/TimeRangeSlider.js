'use client';

import { formatTime } from '../lib/utils';

export default function TimeRangeSlider({
  timeRange, timeMin, timeMax, onMinChange, onMaxChange,
  liveMode, onLiveToggle, loading, currentGraph, fullGraph,
  onApply, onTrends,
}) {
  if (!timeRange) return null;

  const range = timeRange.max - timeRange.min;
  const step = range / 100 || 0.01;

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 mb-4 bg-white dark:bg-gray-950 animate-in">
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        {formatTime(timeMin)} &mdash; {formatTime(timeMax)}
        <span className="text-gray-400 dark:text-gray-500 ml-1">
          (tümü: {formatTime(timeRange.min)} &mdash; {formatTime(timeRange.max)})
        </span>
      </div>

      <div className="relative h-8 mb-1">
        <input type="range" min={timeRange.min} max={timeRange.max} step={step}
          value={timeMin}
          onChange={e => { const v = Number(e.target.value); if (v <= timeMax) onMinChange(v); }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-900 dark:[&::-webkit-slider-thumb]:bg-gray-100
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
        <input type="range" min={timeRange.min} max={timeRange.max} step={step}
          value={timeMax}
          onChange={e => { const v = Number(e.target.value); if (v >= timeMin) onMaxChange(v); }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-500 dark:[&::-webkit-slider-thumb]:bg-gray-400
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
        <div className="absolute top-2 left-0 right-0 h-2 bg-gray-200 dark:bg-gray-700 rounded-full pointer-events-none">
          <div className="absolute h-full bg-gray-300 dark:bg-gray-500 rounded-full"
            style={{ left: `${((timeMin - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax - timeRange.min) / range) * 100}%` }} />
        </div>
      </div>

      <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mb-4">
        <span>{formatTime(timeRange.min)}</span>
        <span>{formatTime(timeRange.max)}</span>
      </div>

      <div className="flex gap-2 items-center flex-wrap">
        <button onClick={onApply} disabled={loading || !currentGraph}
          className="px-4 py-1.5 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {loading ? 'Hesaplanıyor...' : `Spanner (${currentGraph?.vertices?.length || 0}v, ${currentGraph?.edges?.length || 0}e)`}
        </button>
        <button onClick={onLiveToggle}
          className={`px-3 py-1.5 text-xs font-medium rounded-md border transition-colors ${
            liveMode ? 'bg-[var(--color-warning-bg)] border-[var(--color-warning-border)] text-[var(--color-warning)]' : 'border-gray-200 text-gray-500 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800'
          }`}>
          {liveMode ? 'Canlı: Açık' : 'Canlı: Kapalı'}
        </button>
        <button onClick={() => onTrends(fullGraph)} disabled={loading || !fullGraph}
          className="px-4 py-1.5 border border-gray-200 dark:border-gray-700 text-xs font-medium text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          Trendler
        </button>
      </div>
    </div>
  );
}
