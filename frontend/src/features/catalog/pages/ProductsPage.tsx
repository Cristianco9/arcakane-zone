import { useSearchParams } from "react-router-dom";
import { PageHeader } from "../../../components/layout/PageHeader";
import { Button } from "../../../components/ui/Button";
import { EmptyState } from "../../../components/ui/EmptyState";
import { buildProductsUrl, filterParams } from "../../../app/routes";
import { ALL_FILTER, filterProducts, getAvailablePlatforms } from "../catalog";
import { ProductFiltersBar } from "../components/ProductFiltersBar";
import { ProductGrid } from "../components/ProductGrid";
import { categories, products } from "../data/mockData";

const categoryOptions = [
  { value: ALL_FILTER, label: "Todas las categorías" },
  ...categories.map((category) => ({ value: category.id, label: category.name })),
];

const platformOptions = [
  { value: ALL_FILTER, label: "Todas las plataformas" },
  ...getAvailablePlatforms(products).map((platform) => ({
    value: platform,
    label: platform,
  })),
];

export function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get(filterParams.query) ?? "";
  const category = searchParams.get(filterParams.category) ?? ALL_FILTER;
  const platform = searchParams.get(filterParams.platform) ?? ALL_FILTER;

  const filteredProducts = filterProducts(products, {
    query,
    categoryId: category,
    platform,
  });

  function updateParam(key: string, value: string) {
    const nextParams = new URLSearchParams(searchParams);
    if (!value || value === ALL_FILTER) {
      nextParams.delete(key);
    } else {
      nextParams.set(key, value);
    }
    setSearchParams(nextParams, { replace: true });
  }

  function clearFilters() {
    setSearchParams(new URLSearchParams(), { replace: true });
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <PageHeader
        eyebrow="Tienda"
        title="Productos"
        description="Consulta todos los videojuegos disponibles en esta demostración. Usa los filtros para acotar la lista por título, categoría o plataforma."
      />

      <ProductFiltersBar
        query={query}
        category={category}
        platform={platform}
        categoryOptions={categoryOptions}
        platformOptions={platformOptions}
        resultCount={filteredProducts.length}
        onQueryChange={(value) => updateParam(filterParams.query, value)}
        onCategoryChange={(value) => updateParam(filterParams.category, value)}
        onPlatformChange={(value) => updateParam(filterParams.platform, value)}
        onClear={clearFilters}
      />

      <div className="mt-8">
        {filteredProducts.length > 0 ? (
          <ProductGrid products={filteredProducts} />
        ) : (
          <EmptyState
            title="No encontramos productos"
            description="Prueba con otro término de búsqueda o quita alguno de los filtros aplicados."
            action={
              <Button onClick={clearFilters}>Limpiar filtros</Button>
            }
          />
        )}
      </div>

      <p className="mt-10 text-center text-xs text-slate-600">
        Los productos mostrados son datos de prueba. El enlace{" "}
        <a className="text-brand-300 underline-offset-4 hover:underline" href={buildProductsUrl()}>
          /productos
        </a>{" "}
        conserva los filtros en la URL para compartirlos.
      </p>
    </div>
  );
}
