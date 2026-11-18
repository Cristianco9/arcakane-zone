import { PageHeader } from "../components/layout/PageHeader";
import { ButtonLink } from "../components/ui/Button";
import { routes } from "./routes";

export function NotFoundPage() {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <PageHeader
        eyebrow="Error 404"
        title="No encontramos esa vista"
        description="La página que buscas no existe o el producto ya no está disponible en esta demostración."
      />
      <div className="flex flex-wrap gap-3">
        <ButtonLink to={routes.home}>Volver al inicio</ButtonLink>
        <ButtonLink to={routes.products} variant="secondary">
          Ver productos
        </ButtonLink>
      </div>
    </div>
  );
}
