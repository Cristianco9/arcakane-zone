import { lazy, Suspense } from "react";
import { HashRouter, Route, Routes } from "react-router-dom";
import { LoadingFallback } from "./app/LoadingFallback";
import { NotFoundPage } from "./app/NotFoundPage";
import { routes } from "./app/routes";
import { PageLayout } from "./components/layout/PageLayout";

const HomePage = lazy(() =>
  import("./features/catalog/pages/HomePage").then((module) => ({ default: module.HomePage })),
);
const ProductsPage = lazy(() =>
  import("./features/catalog/pages/ProductsPage").then((module) => ({
    default: module.ProductsPage,
  })),
);
const CatalogPage = lazy(() =>
  import("./features/catalog/pages/CatalogPage").then((module) => ({
    default: module.CatalogPage,
  })),
);
const ProductDetailPage = lazy(() =>
  import("./features/catalog/pages/ProductDetailPage").then((module) => ({
    default: module.ProductDetailPage,
  })),
);

export function App() {
  return (
    <HashRouter>
      <PageLayout>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path={routes.home} element={<HomePage />} />
            <Route path={routes.products} element={<ProductsPage />} />
            <Route path={routes.catalog} element={<CatalogPage />} />
            <Route path={`${routes.products}/:productId`} element={<ProductDetailPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </PageLayout>
    </HashRouter>
  );
}
