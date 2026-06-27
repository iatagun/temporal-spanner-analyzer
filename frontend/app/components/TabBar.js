'use client';

export default function TabBar({ tabs, active, onChange }) {
  return (
    <div className="flex border-b border-gray-200">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-4 py-2.5 text-sm border-b-2 -mb-px transition-colors ${
            active === tab.key
              ? 'border-gray-900 text-gray-900 font-medium'
              : 'border-transparent text-gray-400 hover:text-gray-600 hover:border-gray-300'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
