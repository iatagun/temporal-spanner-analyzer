'use client';

export default function LoadingSkeleton() {
  return (
    <div className="animate-in">
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 mb-6 bg-white dark:bg-gray-950">
        <div className="grid grid-cols-2 sm:grid-cols-4 border border-gray-100 dark:border-gray-800 rounded-lg overflow-hidden">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-950 p-4">
              <div className="h-2.5 w-12 bg-gray-100 dark:bg-gray-800 rounded mb-2" />
              <div className="h-4 w-8 bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
          ))}
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <div className="h-[450px] bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg" />
        <div className="h-[450px] bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg" />
      </div>
    </div>
  );
}
