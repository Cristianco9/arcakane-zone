import { Link } from "react-router-dom";
import { LoadingFallback } from "../../../app/LoadingFallback";
import { buildCatalogUrl, buildProductsUrl } from "../../../app/routes";
import { ArrowRightIcon, SparklesIcon } from "../../../components/icons";
import { ButtonLink } from "../../../components/ui/Button";
import { EmptyState } from "../../../components/ui/EmptyState";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { Badge } from "../../../components/ui/Badge";
import { formatPrice } from "../../../lib/format";
import { getPublishedOffers, getStartingPrice } from "../catalog";
import { alFallarPortada } from "../cover";
import { useCatalogCategories, useCatalogPlatforms, useCatalogProducts } from "../api";
import { ProductGrid } from "../components/ProductGrid";

export function HomePage() {
  const categorias = useCatalogCategories();
  const plataformas = useCatalogPlatforms();
  const catalogo = useCatalogProducts();

  if (categorias.isPending || plataformas.isPending || catalogo.isPending) {
    return <LoadingFallback />;
  }

  if (categorias.isError || plataformas.isError || catalogo.isError) {
    return (
      <div className="mx-auto w-full max-w-3xl px-4 py-16 sm:px-6">
        <EmptyState
          title="No se pudo cargar el catálogo"
          description="Inténtalo de nuevo en unos instantes. Los datos se leen desde la API."
        />
      </div>
    );
  }

  const categories = categorias.data ?? [];
  const products = catalogo.data ?? [];
  const featuredProducts = products
    .filter((product) => getPublishedOffers(product).length > 0)
    .slice(0, 4);
  const heroProduct = products[0];

  const stats = [
    { value: String(products.length), label: "videojuegos" },
    { value: String(categories.length), label: "categorías" },
    { value: String((plataformas.data ?? []).length), label: "plataformas" },
  ];

  return (
    <>
      <section className="mx-auto w-full max-w-7xl px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <Badge tone="aqua" className="mb-5">
              <SparklesIcon className="h-3 w-3" />
              Catálogo en vivo
            </Badge>
            <h1 className="text-balance text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl lg:text-6xl">
              Tu próxima aventura empieza aquí.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-400 sm:text-lg">
              Descubre videojuegos, compara ediciones por plataforma y explora un catálogo
              pensado para encontrar rápidamente tu próximo título favorito.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <ButtonLink to={buildCatalogUrl()} size="lg">
                Explorar catálogo
                <ArrowRightIcon className="h-4 w-4" />
              </ButtonLink>
              <ButtonLink to={buildProductsUrl()} size="lg" variant="secondary">
                Ver productos
              </ButtonLink>
            </div>

            <dl className="mt-12 grid max-w-lg grid-cols-3 gap-4 border-t border-white/10 pt-6">
              {stats.map((stat) => (
                <div key={stat.label}>
                  <dt className="sr-only">{stat.label}</dt>
                  <dd>
                    <span className="block text-2xl font-extrabold text-white sm:text-3xl">
                      {stat.value}
                    </span>
                    <span className="mt-1 block text-xs text-slate-500">{stat.label}</span>
                  </dd>
                </div>
              ))}
            </dl>
          </div>

          {heroProduct ? (
            <div className="relative">
              <div className="absolute -inset-6 rounded-[2.5rem] bg-gradient-to-br from-brand-500/25 via-transparent to-aqua-500/20 blur-2xl" />
              <Link
                to={`/productos/${heroProduct.id}`}
                className="relative block overflow-hidden rounded-[2rem] border border-white/15 bg-ink-900 shadow-2xl shadow-brand-500/10"
                aria-label={`Ver detalle de ${heroProduct.title}`}
              >
                <img
                  src={heroProduct.cover}
                  alt={`Portada destacada de ${heroProduct.title}`}
                  onError={alFallarPortada}
                  className="aspect-[4/5] w-full object-cover sm:aspect-[5/4] lg:aspect-[4/5]"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink-950 via-ink-950/20 to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-6 sm:p-8">
                  <Badge tone="brand">Destacado de la semana</Badge>
                  <h2 className="mt-3 text-2xl font-extrabold text-white sm:text-3xl">
                    {heroProduct.title}
                  </h2>
                  <p className="mt-2 line-clamp-2 text-sm text-slate-300">
                    {heroProduct.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between gap-4">
                    <span className="text-lg font-bold text-white">
                      {formatPrice(getStartingPrice(heroProduct) ?? 0)}
                    </span>
                    <span className="inline-flex items-center gap-1 text-sm font-semibold text-brand-200">
                      Ver detalle
                      <ArrowRightIcon className="h-4 w-4" />
                    </span>
                  </div>
                </div>
              </Link>
            </div>
          ) : null}
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="Selección destacada"
          title="Juegos que vale la pena descubrir"
          description="Una muestra de los títulos que puedes encontrar en el catálogo."
          action={
            <ButtonLink to={buildProductsUrl()} variant="secondary">
              Ver todos los productos
            </ButtonLink>
          }
        />
        <div className="mt-8">
          <ProductGrid products={featuredProducts} />
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <SectionHeading
          eyebrow="Explora por categoría"
          title="Encuentra tu próximo género favorito"
          description="Cada catálogo agrupa títulos con experiencias parecidas."
        />
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((category) => {
            const count = products.filter(
              (product) => product.category.id === category.id,
            ).length;
            return (
              <Link
                key={category.id}
                to={buildCatalogUrl(category.id)}
                className="group rounded-2xl border border-white/10 bg-gradient-to-br from-ink-800/90 to-ink-900/50 p-5 transition hover:border-brand-400/50 motion-reduce:transition-none"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{category.name}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-400">
                      {category.description}
                    </p>
                  </div>
                  <ArrowRightIcon className="h-5 w-5 shrink-0 text-brand-300 transition group-hover:translate-x-1 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0" />
                </div>
                <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-brand-300">
                  {count} {count === 1 ? "título" : "títulos"}
                </p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl border border-brand-400/20 bg-gradient-to-r from-brand-600/25 via-ink-900 to-aqua-500/10 px-6 py-10 sm:px-10 sm:py-14">
          <div className="relative max-w-2xl">
            <h2 className="text-2xl font-extrabold text-white sm:text-3xl">
              ¿Listo para recorrer el catálogo completo?
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-300 sm:text-base">
              Filtra por título, categoría o plataforma y consulta toda la información de
              cada juego antes de elegir.
            </p>
            <ButtonLink to={buildProductsUrl()} className="mt-6" size="lg">
              Abrir vista de productos
              <ArrowRightIcon className="h-4 w-4" />
            </ButtonLink>
          </div>
        </div>
      </section>
    </>
  );
}
