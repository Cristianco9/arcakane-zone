import { Link } from "react-router-dom";
import { routes } from "../../../app/routes";
import { ArrowRightIcon } from "../../../components/icons";
import { Badge } from "../../../components/ui/Badge";
import { formatPrice } from "../../../lib/format";
import { getPublishedOffers, getStartingPrice } from "../catalog";
import type { Product } from "../types";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const startingPrice = getStartingPrice(product);
  const offerCount = getPublishedOffers(product).length;

  return (
    <Link
      to={routes.productDetail(product.id)}
      aria-label={`Ver detalle de ${product.title}`}
      className="group flex h-full flex-col rounded-3xl border border-white/10 bg-ink-900/70 p-3 transition duration-300 hover:-translate-y-1 hover:border-brand-400/50 hover:bg-ink-800/80 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
    >
      <div className="relative aspect-[4/5] overflow-hidden rounded-2xl bg-ink-800">
        <img
          src={product.cover}
          alt={`Portada de ${product.title}`}
          loading="lazy"
          className="h-full w-full object-cover transition duration-500 group-hover:scale-105 motion-reduce:transition-none"
        />
        <div className="absolute inset-x-0 bottom-0 flex flex-wrap gap-2 bg-gradient-to-t from-ink-950/90 to-transparent p-3 pt-10">
          {product.featured ? <Badge tone="brand">Destacado</Badge> : null}
          <Badge tone="aqua">{product.category.name}</Badge>
        </div>
      </div>

      <div className="flex flex-1 flex-col px-1 pb-1 pt-4">
        <p className="text-xs font-medium uppercase tracking-wider text-brand-300">
          {product.genre.name} · {product.developer}
        </p>
        <h3 className="mt-2 text-lg font-bold text-white">{product.title}</h3>
        <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-400">
          {product.description}
        </p>

        <div className="mt-auto flex items-end justify-between gap-3 pt-5">
          <div>
            <p className="text-[11px] uppercase tracking-wider text-slate-500">
              Desde · {offerCount} {offerCount === 1 ? "edición" : "ediciones"}
            </p>
            <p className="mt-1 text-lg font-extrabold text-white">
              {startingPrice === null ? "Sin precio" : formatPrice(startingPrice)}
            </p>
          </div>
          <span className="inline-flex items-center gap-1 text-sm font-semibold text-brand-300 group-hover:text-brand-200">
            Ver detalle
            <ArrowRightIcon className="h-4 w-4" />
          </span>
        </div>
      </div>
    </Link>
  );
}
