import { formatDate } from "../../../lib/format";
import type { Product } from "../types";

interface ProductSpecsProps {
  product: Product;
}

export function ProductSpecs({ product }: ProductSpecsProps) {
  const specs = [
    { label: "Desarrollador", value: product.developer },
    { label: "Categoría", value: product.category.name },
    { label: "Género", value: product.genre.name },
    { label: "Lanzamiento", value: formatDate(product.releaseDate) },
    ...product.features,
  ];

  return (
    <section aria-labelledby="specs-heading">
      <h2 id="specs-heading" className="text-lg font-bold text-white">
        Ficha técnica
      </h2>
      <dl className="mt-3 grid gap-x-6 gap-y-3 sm:grid-cols-2">
        {specs.map((spec) => (
          <div
            key={spec.label}
            className="border-b border-white/5 pb-2 last:border-0 sm:last:border-b"
          >
            <dt className="text-xs uppercase tracking-wider text-slate-500">{spec.label}</dt>
            <dd className="mt-1 text-sm text-slate-200">{spec.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
