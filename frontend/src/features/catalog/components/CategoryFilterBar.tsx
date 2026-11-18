import { cn } from "../../../lib/cn";
import { ALL_FILTER } from "../catalog";
import type { CatalogCategory } from "../types";

interface CategoryFilterBarProps {
  categories: readonly CatalogCategory[];
  selectedId: string;
  counts: Record<string, number>;
  onChange: (categoryId: string) => void;
}

export function CategoryFilterBar({
  categories,
  selectedId,
  counts,
  onChange,
}: CategoryFilterBarProps) {
  const options = [
    { id: ALL_FILTER, label: "Todas", count: Object.values(counts).reduce((sum, n) => sum + n, 0) },
    ...categories.map((category) => ({
      id: category.id,
      label: category.name,
      count: counts[category.id] ?? 0,
    })),
  ];

  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar por categoría">
      {options.map((option) => {
        const isSelected = selectedId === option.id;
        return (
          <button
            key={option.id}
            type="button"
            aria-pressed={isSelected}
            onClick={() => onChange(option.id)}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-medium transition motion-reduce:transition-none",
              isSelected
                ? "border-brand-400/50 bg-brand-500/20 text-brand-100"
                : "border-white/10 bg-white/5 text-slate-400 hover:border-white/20 hover:text-white",
            )}
          >
            {option.label}
            <span className="ml-2 text-xs text-slate-500">{option.count}</span>
          </button>
        );
      })}
    </div>
  );
}
