import { Link } from "react-router-dom";
import { routes } from "../../app/routes";
import { GamesIcon } from "../icons";

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t border-white/10 bg-ink-950/60">
      <div className="mx-auto grid w-full max-w-7xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-[1.4fr_1fr] lg:px-8">
        <div>
          <div className="flex items-center gap-2.5 text-white">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-500/20 text-brand-300">
              <GamesIcon className="h-4 w-4" />
            </span>
            <span className="font-extrabold tracking-tight">ArkaneZone</span>
          </div>
          <p className="mt-3 max-w-md text-sm leading-relaxed text-slate-500">
            Tu escaparate de videojuegos. Explora títulos, compara ediciones y descubre tu
            próxima aventura.
          </p>
        </div>

        <nav aria-label="Navegación del pie de página">
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Explorar</p>
          <ul className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400 sm:flex-col">
            <li>
              <Link className="hover:text-brand-300" to={routes.home}>
                Inicio
              </Link>
            </li>
            <li>
              <Link className="hover:text-brand-300" to={routes.products}>
                Productos
              </Link>
            </li>
            <li>
              <Link className="hover:text-brand-300" to={routes.catalog}>
                Catálogos
              </Link>
            </li>
          </ul>
        </nav>
      </div>

      <div className="border-t border-white/5 px-4 py-5 text-center text-xs text-slate-600">
        © {new Date().getFullYear()} Arkane Zone · Interfaces con datos de demostración
      </div>
    </footer>
  );
}
