import { Link, useSearchParams } from "react-router-dom";
import { LoadingFallback } from "../../../app/LoadingFallback";
import { buildProductsUrl, filterParams } from "../../../app/routes";
import { ArrowRightIcon } from "../../../components/icons";
import { PageHeader } from "../../../components/layout/PageHeader";
import { EmptyState } from "../../../components/ui/EmptyState";
import { SectionHeading } from "../../../components/ui/SectionHeading";
import { ALL_FILTER, groupProductsByCategory } from "../catalog";
import { useCatalogCategories, useCatalogProducts } from "../api";
import { CategoryFilterBar } from "../components/CategoryFilterBar";
import { ProductGrid } from "../components/ProductGrid";

export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedCategory = searchParams.get(filterParams.category) ?? ALL_FILTER;

  const categorias = useCatalogCategories();
  const catalogo = useCatalogProducts();

  if (categorias.isPending || catalogo.isPending) {
    return <LoadingFallback />;
  }

  if (categorias.isError || catalogo.isError) {
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
  const allGroups = groupProductsByCategory(products, categories);
  const counts = Object.fromEntries(
    allGroups.map((group) => [group.category.id, group.products.length]),
  );

  const groups = groupProductsByCategory(
    selectedCategory === ALL_FILTER
      ? products
      : products.filter((product) => product.category.id === selectedCategory),
    categories,
  );

  function selectCategory(categoryId: string) {
    const nextParams = new URLSearchParams(searchParams);
    if (categoryId === ALL_FILTER) {
      nextParams.delete(filterParams.category);
    } else {
      nextParams.set(filterParams.category, categoryId);
    }
    setSearchParams(nextParams, { replace: true });
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <PageHeader
        eyebrow="Colecciones"
        title="Catálogos"
        description="Explora los juegos organizados por categorías. Cada agrupación reúne títulos con experiencias y temáticas similares."
      />

      <CategoryFilterBar
        categories={categories}
        selectedId={selectedCategory}
        counts={counts}
        onChange={selectCategory}
      />

      <div className="mt-12 space-y-16">
        {groups.length > 0 ? (
          groups.map((group) => (
            <section key={group.category.id} aria-labelledby={`category-${group.category.id}`}>
              <SectionHeading
                eyebrow={`${group.products.length} ${
                  group.products.length === 1 ? "título" : "títulos"
                }`}
                title={group.category.name}
                description={group.category.description}
                action={
                  <Link
                    to={buildProductsUrl({ category: group.category.id })}
                    className="inline-flex items-center gap-2 text-sm font-semibold text-brand-300 hover:text-brand-200"
                  >
                    Ver en productos
                    <ArrowRightIcon className="h-4 w-4" />
                  </Link>
                }
              />
              <h2 id={`category-${group.category.id}`} className="sr-only">
                {group.category.name}
              </h2>
              <div className="mt-6">
                <ProductGrid products={group.products} />
              </div>
            </section>
          ))
        ) : (
          <EmptyState
            title="Categoría sin títulos"
            description="Todavía no hay videojuegos en esta categoría. Prueba con otra agrupación."
          />
        )}
      </div>
    </div>
  );
}
