import { Button } from "../../../components/ui/Button";
import { SearchField, SelectField } from "../../../components/ui/Fields";
import { ALL_FILTER } from "../catalog";

interface ProductFiltersBarProps {
  query: string;
  category: string;
  platform: string;
  categoryOptions: readonly { value: string; label: string }[];
  platformOptions: readonly { value: string; label: string }[];
  resultCount: number;
  onQueryChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
  onPlatformChange: (value: string) => void;
  onClear: () => void;
}

export function ProductFiltersBar({
  query,
  category,
  platform,
  categoryOptions,
  platformOptions,
  resultCount,
  onQueryChange,
  onCategoryChange,
  onPlatformChange,
  onClear,
}: ProductFiltersBarProps) {
  const hasFilters =
    query.length > 0 || category !== ALL_FILTER || platform !== ALL_FILTER;

  return (
    <section className="rounded-3xl border border-white/10 bg-ink-900/60 p-4 sm:p-5" aria-label="Filtros de productos">
      <div className="grid gap-3 md:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)_minmax(0,1fr)_auto]">
        <SearchField
          label="Buscar productos"
          value={query}
          onChange={onQueryChange}
          placeholder="Buscar por título, género o desarrollador…"
        />
        <SelectField
          label="Filtrar por categoría"
          value={category}
          options={categoryOptions}
          onChange={onCategoryChange}
        />
        <SelectField
          label="Filtrar por plataforma"
          value={platform}
          options={platformOptions}
          onChange={onPlatformChange}
        />
        <Button
          variant="ghost"
          onClick={onClear}
          disabled={!hasFilters}
          className="whitespace-nowrap"
        >
          Limpiar filtros
        </Button>
      </div>
      <p className="mt-4 text-sm text-slate-500" aria-live="polite">
        {resultCount} {resultCount === 1 ? "resultado" : "resultados"}
      </p>
    </section>
  );
}
