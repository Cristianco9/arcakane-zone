export function LoadingFallback() {
  return (
    <div className="grid min-h-[60svh] place-items-center" role="status" aria-live="polite">
      <div className="flex items-center gap-3 text-sm text-slate-400">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/15 border-t-brand-400 motion-reduce:animate-none" />
        Cargando vista…
      </div>
    </div>
  );
}
