import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { routes } from "../../app/routes";
import { cn } from "../../lib/cn";
import { CloseIcon, GamesIcon, MenuIcon } from "../icons";

const navigation = [
  { label: "Inicio", to: routes.home, end: true },
  { label: "Productos", to: routes.products, end: false },
  { label: "Catálogos", to: routes.catalog, end: false },
] as const;

function navLinkClass(isActive: boolean): string {
  return cn(
    "rounded-lg px-3 py-2 text-sm font-medium transition motion-reduce:transition-none",
    isActive
      ? "bg-brand-500/15 text-brand-200"
      : "text-slate-400 hover:bg-white/5 hover:text-white",
  );
}

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-ink-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          to={routes.home}
          className="flex items-center gap-2.5 text-white"
          onClick={() => setMenuOpen(false)}
        >
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-aqua-500 shadow-lg shadow-brand-500/25">
            <GamesIcon className="h-5 w-5" />
          </span>
          <span className="text-base font-extrabold tracking-tight">
            Arkane<span className="text-brand-300">Zone</span>
          </span>
        </Link>

        <nav aria-label="Navegación principal" className="hidden items-center gap-1 md:flex">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => navLinkClass(isActive)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden md:block">
          <NavLink
            to={routes.catalog}
            className="rounded-xl border border-brand-400/30 bg-brand-500/10 px-4 py-2 text-sm font-semibold text-brand-200 transition hover:bg-brand-500/20 motion-reduce:transition-none"
          >
            Explorar catálogo
          </NavLink>
        </div>

        <button
          type="button"
          className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 text-slate-200 md:hidden"
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={menuOpen}
          aria-controls="mobile-navigation"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <CloseIcon className="h-5 w-5" /> : <MenuIcon className="h-5 w-5" />}
        </button>
      </div>

      {menuOpen ? (
        <nav
          id="mobile-navigation"
          aria-label="Navegación móvil"
          className="border-t border-white/10 bg-ink-900/95 px-4 py-3 md:hidden"
        >
          <ul className="flex flex-col gap-1">
            {navigation.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.end}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) => cn("block", navLinkClass(isActive))}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
    </header>
  );
}
