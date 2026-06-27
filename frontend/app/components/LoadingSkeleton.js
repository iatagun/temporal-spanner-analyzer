'use client';

export default function LoadingSkeleton() {
  return (
    <div className="animate-in">
      <div className="border border-gray-200 p-4 mb-6 bg-white">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-gray-100 border border-gray-100">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white p-3.5">
              <div className="h-2.5 w-12 bg-gray-100 mb-2" />
              <div className="h-4 w-8 bg-gray-100" />
            </div>
          ))}
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <div className="h-[450px] bg-gray-50 border border-gray-200" />
        <div className="h-[450px] bg-gray-50 border border-gray-200" />
      </div>
    </div>
  );
}
