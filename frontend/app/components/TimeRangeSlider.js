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
    <div className="bg-gradient-to-br from-slate-50 to-blue-50/50 rounded-xl border border-border p-5 mt-4 animate-slide-in">
      <div className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
        <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {formatTime(timeMin)} &mdash; {formatTime(timeMax)}
        <span className="font-normal text-text-muted text-xs ml-1">
          (full: {formatTime(timeRange.min)} &mdash; {formatTime(timeRange.max)})
        </span>
      </div>

      <div className="relative h-8 mb-1">
        <input
          type="range"
          min={timeRange.min}
          max={timeRange.max}
          step={step}
          value={timeMin}
          onChange={e => {
            const v = Number(e.target.value);
            if (v <= timeMax) onMinChange(v);
          }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:shadow-md
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10"
        />
        <input
          type="range"
          min={timeRange.min}
          max={timeRange.max}
          step={step}
          value={timeMax}
          onChange={e => {
            const v = Number(e.target.value);
            if (v >= timeMin) onMaxChange(v);
          }}
          className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent [&::-webkit-slider-thumb]:shadow-md
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10"
        />
        <div className="absolute top-2 left-0 right-0 h-2 bg-slate-200 rounded-full pointer-events-none">
          <div
            className="absolute h-full bg-gradient-to-r from-primary to-accent rounded-full"
            style={{
              left: `${((timeMin - timeRange.min) / range) * 100}%`,
              right: `${100 - ((timeMax - timeRange.min) / range) * 100}%`,
            }}
          />
        </div>
      </div>

      <div className="flex justify-between text-xs text-text-muted mb-4">
        <span>{formatTime(timeRange.min)}</span>
        <span>{formatTime(timeRange.max)}</span>
      </div>

      <div className="flex gap-3 items-center flex-wrap">
        <button
          onClick={onApply}
          disabled={loading || !currentGraph}
          className="px-5 py-2 bg-gradient-to-r from-primary to-primary-dark text-white rounded-lg
                     text-sm font-semibold shadow-md shadow-primary/25 hover:shadow-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {loading ? 'Computing...' : `Spanner (${currentGraph?.vertices?.length || 0}v, ${currentGraph?.edges?.length || 0}e)`}
        </button>
        <button
          onClick={onLiveToggle}
          className={`px-4 py-2 rounded-lg text-sm font-semibold border transition-all duration-200 ${
            liveMode
              ? 'bg-warning/10 text-warning border-warning/30 shadow-sm shadow-warning/10'
              : 'bg-white text-text-muted border-border hover:border-slate-300'
          }`}
        >
          <span className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${liveMode ? 'bg-warning animate-pulse' : 'bg-slate-300'}`} />
            {liveMode ? 'Live: ON' : 'Live: OFF'}
          </span>
        </button>
        <button
          onClick={() => onTrends(fullGraph)}
          disabled={loading || !fullGraph}
          className="px-5 py-2 bg-gradient-to-r from-success to-emerald-600 text-white rounded-lg
                     text-sm font-semibold shadow-md shadow-success/25 hover:shadow-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          Trends
        </button>
      </div>
    </div>
  );
}
