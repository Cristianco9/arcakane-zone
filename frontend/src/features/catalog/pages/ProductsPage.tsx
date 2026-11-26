import { useSearchParams } from "react-router-dom";
import { LoadingFallback } from "../../../app/LoadingFallback";
import { PageHeader } from "../../../components/layout/PageHeader";
import { Button } from "../../../components/ui/Button";
import { EmptyState } from "../../../components/ui/EmptyState";
import { buildProductsUrl, filterParams } from "../../../app/routes";
import { ALL_FILTER, filterProducts, getAvailablePlatforms } from "../catalog";
import {
  useCatalogCategories,
  useCatalogPlatforms,
  useCatalogProducts,
} from "../api";
import { ProductFiltersBar } from "../components/ProductFiltersBar";
import { ProductGrid } from "../components/ProductGrid";

export function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get(filterParams.query) ?? "";
  const category = searchParams.get(filterParams.category) ?? ALL_FILTER;
  const platform = searchParams.get(filterParams.platform) ?? ALL_FILTER;

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

  const products = catalogo.data ?? [];
  const categoryOptions = [
    { value: ALL_FILTER, label: "Todas las categorías" },
    ...(categorias.data ?? []).map((item) => ({
      value: item.id,
      label: item.name,
    })),
  ];

  const platformOptions = [
    { value: ALL_FILTER, label: "Todas las plataformas" },
    ...getAvailablePlatforms(products, plataformas.data ?? []).map((item) => ({
      value: item,
      label: item,
    })),
  ];

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
        description="Consulta todos los videojuegos del catálogo. Usa los filtros para acotar la lista por título, categoría o plataforma."
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
            action={<Button onClick={clearFilters}>Limpiar filtros</Button>}
          />
        )}
      </div>

      <p className="mt-10 text-center text-xs text-slate-600">
        Los productos mostrados provienen del catálogo de la API. El enlace{" "}
        <a className="text-brand-300 underline-offset-4 hover:underline" href={buildProductsUrl()}>
          /productos
        </a>{" "}
        conserva los filtros en la URL para compartirlos.
      </p>
    </div>
  );
}
