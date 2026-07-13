// Small line-drawing icons matching the app's ink-stroke mark/favicon style
// -- deliberately hand-drawn inline SVGs rather than pulling in an icon
// library, so the visual language stays consistent with icon.svg/Header.
function SpannerIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" aria-hidden="true">
      <circle cx="5" cy="6" r="1.6" fill="currentColor" />
      <circle cx="5" cy="18" r="1.6" fill="currentColor" />
      <circle cx="19" cy="12" r="1.6" fill="currentColor" />
      <path d="M5 6 L5 18 M5 12 L19 12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function TrendsIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" aria-hidden="true">
      <path d="M4 18 L9 11 L14 15 L20 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="9" cy="11" r="1.3" fill="currentColor" />
      <circle cx="14" cy="15" r="1.3" fill="currentColor" />
    </svg>
  );
}

function CompareIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" aria-hidden="true">
      <rect x="3" y="5" width="7" height="14" rx="1" stroke="currentColor" strokeWidth="1.3" />
      <rect x="14" y="5" width="7" height="14" rx="1" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}

function ExploreIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" aria-hidden="true">
      <circle cx="10" cy="10" r="6" stroke="currentColor" strokeWidth="1.4" />
      <path d="M14.5 14.5 L20 20" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

const FEATURES = [
  { Icon: SpannerIcon, title: 'Spanner', desc: 'Orijinal ve seyreltilmiş çizge' },
  { Icon: TrendsIcon, title: 'Trendler', desc: 'Kliklerin zaman çizelgesi' },
  { Icon: CompareIcon, title: 'Karşılaştır', desc: 'İki dönem yan yana' },
  { Icon: ExploreIcon, title: 'Keşfet', desc: 'Kelime ve klik sorgulama' },
];

export default function FeatureGrid() {
  return (
    <section className="max-w-5xl mx-auto px-6 py-16 border-t border-gray-200 dark:border-gray-800">
      <h2 className="font-serif text-2xl font-medium tracking-tight text-gray-900 dark:text-gray-100 mb-8 text-center">
        Görünümler
      </h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {FEATURES.map(({ Icon, title, desc }) => (
          <div key={title} className="border border-gray-200 dark:border-gray-800 rounded-lg p-5 bg-white dark:bg-gray-950">
            <div className="text-gray-500 dark:text-gray-400 mb-3">
              <Icon />
            </div>
            <h3 className="font-serif text-base text-gray-900 dark:text-gray-100 mb-1">{title}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">{desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
