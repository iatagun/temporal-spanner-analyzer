import Link from 'next/link';
import SupportButton from '../SupportButton';

export default function Nav() {
  return (
    <nav className="sticky top-0 z-10 bg-[var(--page-bg)] border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <svg className="w-6 h-6 text-gray-900 dark:text-gray-100 flex-shrink-0" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <circle cx="6" cy="9" r="2" fill="currentColor" />
            <circle cx="6" cy="23" r="2" fill="currentColor" />
            <circle cx="15" cy="16" r="2" fill="currentColor" />
            <circle cx="26" cy="16" r="2" fill="currentColor" />
            <path d="M6 9 L6 23 M6 9 L15 16 M6 23 L15 16 M15 16 L26 16"
              stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
          <span className="font-serif text-lg font-medium tracking-tight text-gray-900 dark:text-gray-100">
            Temporal Spanner Analyzer
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <SupportButton />
          <Link href="/app"
            className="px-4 py-1.5 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 transition-colors">
            Aracı Aç
          </Link>
        </div>
      </div>
    </nav>
  );
}
