import { CheckIcon } from "../../../components/icons";
import { Badge } from "../../../components/ui/Badge";
import { formatPrice } from "../../../lib/format";
import { getPublishedOffers } from "../catalog";
import type { Product } from "../types";

interface ProductOffersProps {
  product: Product;
}

export function ProductOffers({ product }: ProductOffersProps) {
  const offers = getPublishedOffers(product);

  return (
    <section aria-labelledby="offers-heading">
      <h2 id="offers-heading" className="text-lg font-bold text-white">
        Ediciones disponibles
      </h2>
      <ul className="mt-3 space-y-2">
        {offers.map((offer) => (
          <li
            key={offer.id}
            className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
          >
            <div>
              <p className="text-sm font-semibold text-slate-100">{offer.platform}</p>
              <p className="mt-0.5 text-xs text-slate-500">SKU {offer.sku}</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge tone={offer.stock > 0 ? "success" : "warning"}>
                {offer.stock > 0 ? (
                  <>
                    <CheckIcon className="h-3 w-3" />
                    {offer.stock} en stock
                  </>
                ) : (
                  "Agotado"
                )}
              </Badge>
              <span className="text-base font-bold text-white">{formatPrice(offer.price)}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
