'use client';

export default function TabBar({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
            active === tab.key
              ? 'bg-white text-primary shadow-sm shadow-slate-200'
              : 'text-text-muted hover:text-text hover:bg-white/50'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
