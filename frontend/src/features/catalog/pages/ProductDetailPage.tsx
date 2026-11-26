import { Link, useParams } from "react-router-dom";
import { LoadingFallback } from "../../../app/LoadingFallback";
import { NotFoundPage } from "../../../app/NotFoundPage";
import { routes } from "../../../app/routes";
import { ArrowLeftIcon } from "../../../components/icons";
import { Badge } from "../../../components/ui/Badge";
import { ButtonLink } from "../../../components/ui/Button";
import { EmptyState } from "../../../components/ui/EmptyState";
import { formatPrice } from "../../../lib/format";
import {
  getPublishedOffers,
  getRelatedProducts,
  getStartingPrice,
  isProductAvailable,
} from "../catalog";
import { useCatalogProduct, useCatalogProducts } from "../api";
import { ProductGrid } from "../components/ProductGrid";
import { ProductOffers } from "../components/ProductOffers";
import { ProductSpecs } from "../components/ProductSpecs";

export function ProductDetailPage() {
  const { productId } = useParams();
  const producto = useCatalogProduct(productId);
  const catalogo = useCatalogProducts();

  if (producto.isPending || catalogo.isPending) {
    return <LoadingFallback />;
  }

  if (producto.isError || catalogo.isError) {
    return (
      <div className="mx-auto w-full max-w-3xl px-4 py-16 sm:px-6">
        <EmptyState
          title="No se pudo cargar el videojuego"
          description="Inténtalo de nuevo en unos instantes. Los datos se leen desde la API."
        />
      </div>
    );
  }

  const product = producto.data;
  if (!product) {
    return <NotFoundPage />;
  }

  const startingPrice = getStartingPrice(product);
  const relatedProducts = getRelatedProducts(product, catalogo.data ?? []);
  const previewImages = [product.cover, ...product.gallery];

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
      <nav aria-label="Ruta de navegación">
        <ol className="flex flex-wrap items-center gap-2 text-sm text-slate-500">
          <li>
            <Link className="hover:text-brand-300" to={routes.home}>
              Inicio
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>
            <Link className="hover:text-brand-300" to={routes.products}>
              Productos
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-slate-300" aria-current="page">
            {product.title}
          </li>
        </ol>
      </nav>

      <div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:gap-14">
        <div>
          <figure className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-ink-900">
            <img
              src={product.cover}
              alt={`Portada de ${product.title}`}
              className="aspect-[4/5] w-full object-cover"
            />
            <figcaption className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink-950 via-ink-950/70 to-transparent p-6 pt-20 text-lg font-bold text-white">
              {product.title}
            </figcaption>
          </figure>

          <ul className="mt-4 grid grid-cols-3 gap-3" aria-label="Imágenes del producto">
            {previewImages.map((image, index) => (
              <li key={`${image}-${index}`} className="overflow-hidden rounded-xl border border-white/10">
                <img
                  src={image}
                  alt={
                    index === 0
                      ? `Portada de ${product.title}`
                      : `Vista ${index} de ${product.title}`
                  }
                  className="aspect-video w-full object-cover"
                  loading="lazy"
                />
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div className="flex flex-wrap gap-2">
            <Badge tone="aqua">{product.category.name}</Badge>
            <Badge tone={isProductAvailable(product) ? "success" : "warning"}>
              {isProductAvailable(product) ? "Disponible" : "Agotado"}
            </Badge>
          </div>

          <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            {product.title}
          </h1>
          <p className="mt-4 text-base leading-relaxed text-slate-400">{product.longDescription}</p>

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-brand-400/20 bg-brand-500/10 p-5">
            <div>
              <p className="text-xs uppercase tracking-wider text-brand-200">Precio desde</p>
              <p className="mt-1 text-3xl font-extrabold text-white">
                {startingPrice === null ? "Sin precio" : formatPrice(startingPrice)}
              </p>
            </div>
            <p className="text-sm text-slate-300">
              {getPublishedOffers(product).length}{" "}
              {getPublishedOffers(product).length === 1 ? "edición publicada" : "ediciones publicadas"}
            </p>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {product.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-10 space-y-10">
            <ProductOffers product={product} />
            <ProductSpecs product={product} />
          </div>

          <ButtonLink to={routes.products} variant="secondary" className="mt-10">
            <ArrowLeftIcon className="h-4 w-4" />
            Volver a productos
          </ButtonLink>
        </div>
      </div>

      {relatedProducts.length > 0 ? (
        <section className="mt-20" aria-labelledby="related-heading">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-[0.22em] text-brand-300">
                También te puede gustar
              </p>
              <h2 id="related-heading" className="text-2xl font-bold text-white">
                Más de {product.category.name}
              </h2>
            </div>
            <ButtonLink to={routes.catalog} variant="ghost" className="hidden sm:inline-flex">
              Ver catálogo
            </ButtonLink>
          </div>
          <ProductGrid products={relatedProducts} />
        </section>
      ) : null}
    </div>
  );
}
