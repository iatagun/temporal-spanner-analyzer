'use client';

export default function LoadingSkeleton() {
  return (
    <div className="animate-fade-in">
      <div className="bg-white rounded-2xl border border-border shadow-sm p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-slate-200 animate-pulse" />
          <div className="h-5 w-48 bg-slate-200 rounded animate-pulse" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="h-3 w-16 bg-slate-200 rounded animate-pulse mb-2" />
              <div className="h-6 w-12 bg-slate-200 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-5 mb-8">
        <div className="h-[450px] bg-slate-100 rounded-xl animate-pulse" />
        <div className="h-[450px] bg-slate-100 rounded-xl animate-pulse" />
      </div>
    </div>
  );
}
