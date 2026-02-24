"use client";

export function SectionSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="bg-surface border border-white/5 rounded-xl p-6">
          <div className="h-4 w-1/3 bg-white/5 rounded mb-3" />
          <div className="h-3 w-2/3 bg-white/5 rounded mb-2" />
          <div className="h-3 w-1/2 bg-white/5 rounded" />
        </div>
      ))}
    </div>
  );
}

export function ScoreRingSkeleton() {
  return (
    <div className="animate-pulse bg-surface border border-white/5 rounded-xl p-10 flex flex-col md:flex-row items-center gap-10">
      <div className="w-40 h-40 rounded-full bg-white/5 flex-shrink-0" />
      <div className="flex-1 space-y-3">
        <div className="h-6 w-48 bg-white/5 rounded" />
        <div className="h-3 w-64 bg-white/5 rounded" />
        <div className="flex gap-2 mt-4">
          <div className="h-6 w-20 bg-white/5 rounded" />
          <div className="h-6 w-24 bg-white/5 rounded" />
          <div className="h-6 w-28 bg-white/5 rounded" />
        </div>
      </div>
    </div>
  );
}

export function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-surface border border-white/5 rounded-xl p-6">
          <div className="h-4 w-2/3 bg-white/5 rounded mb-3" />
          <div className="h-3 w-full bg-white/5 rounded mb-2" />
          <div className="h-3 w-3/4 bg-white/5 rounded mb-4" />
          <div className="h-3 w-1/3 bg-white/5 rounded" />
        </div>
      ))}
    </div>
  );
}
