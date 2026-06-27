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
    <div className="border border-gray-200 rounded-lg p-4 mb-4 bg-white animate-in">
      <div className="text-xs text-gray-500 mb-3">
        {formatTime(timeMin)} &mdash; {formatTime(timeMax)}
        <span className="text-gray-400 ml-1">
          (tümü: {formatTime(timeRange.min)} &mdash; {formatTime(timeRange.max)})
        </span>
      </div>

      <div className="relative h-8 mb-1">
        <input type="range" min={timeRange.min} max={timeRange.max} step={step}
          value={timeMin}
          onChange={e => { const v = Number(e.target.value); if (v <= timeMax) onMinChange(v); }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-900
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
        <input type="range" min={timeRange.min} max={timeRange.max} step={step}
          value={timeMax}
          onChange={e => { const v = Number(e.target.value); if (v >= timeMin) onMaxChange(v); }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-500
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
        <div className="absolute top-2 left-0 right-0 h-2 bg-gray-200 rounded-full pointer-events-none">
          <div className="absolute h-full bg-gray-300 rounded-full"
            style={{ left: `${((timeMin - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax - timeRange.min) / range) * 100}%` }} />
        </div>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-4">
        <span>{formatTime(timeRange.min)}</span>
        <span>{formatTime(timeRange.max)}</span>
      </div>

      <div className="flex gap-2 items-center flex-wrap">
        <button onClick={onApply} disabled={loading || !currentGraph}
          className="px-4 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {loading ? 'Hesaplanıyor...' : `Spanner (${currentGraph?.vertices?.length || 0}v, ${currentGraph?.edges?.length || 0}e)`}
        </button>
        <button onClick={onLiveToggle}
          className={`px-3 py-1.5 text-xs font-medium rounded-md border transition-colors ${
            liveMode ? 'bg-amber-50 border-amber-300 text-amber-700' : 'border-gray-200 text-gray-500 hover:bg-gray-50'
          }`}>
          {liveMode ? 'Canlı: Açık' : 'Canlı: Kapalı'}
        </button>
        <button onClick={() => onTrends(fullGraph)} disabled={loading || !fullGraph}
          className="px-4 py-1.5 border border-gray-200 text-xs font-medium text-gray-600 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          Trendler
        </button>
      </div>
    </div>
  );
}
