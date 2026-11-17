---
name: react-vite-ts-tailwind
description: Mejores prácticas para construir, modificar y revisar aplicaciones React con TypeScript, Vite, Tailwind CSS y CSS. Úsala SIEMPRE que el usuario pida crear o editar componentes, hooks, páginas, formularios, layouts, estilos, configuración de Vite/Tailwind/tsconfig, o cualquier código .tsx/.ts/.css de un proyecto React, aunque no mencione explícitamente "React", "Tailwind" o "Vite". También aplica al refactorizar, depurar errores de tipos, optimizar rendimiento, o añadir tests a componentes.
---

# React + Vite + TypeScript + Tailwind

Guía operativa para el agente. Sigue estas reglas por defecto; si el proyecto ya tiene convenciones distintas, **las del proyecto mandan** (revisa antes el código existente).

## Flujo de trabajo obligatorio

1. **Explora primero.** Lee `package.json`, `vite.config.ts`, `tsconfig*.json`, `src/index.css` y 1–2 componentes similares al que vas a crear. Detecta el gestor de paquetes por el lockfile (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lock`) y úsalo siempre.
2. **Reutiliza antes de crear.** Busca componentes, hooks y utilidades existentes (`src/components/ui`, `src/hooks`, `src/lib`).
3. **Cambios mínimos y coherentes.** No reformatees archivos ajenos a la tarea ni cambies dependencias sin necesidad.
4. **Verifica al terminar** (ver "Definition of Done").

## Versiones de referencia

Asume React 19, Vite (última estable), TypeScript 5.x en modo estricto y Tailwind CSS v4. **Comprueba la versión real en `package.json`** y adapta: si es Tailwind v3, usa `tailwind.config.ts` y las directivas `@tailwind`; si es React 18, usa `forwardRef`.

## Estructura de proyecto

Organiza por funcionalidad (feature-based), no solo por tipo de archivo:

```
src/
├── app/            # Providers, router, layout raíz
├── features/
│   └── auth/
│       ├── components/
│       ├── hooks/
│       ├── api.ts
│       ├── types.ts
│       └── index.ts      # API pública de la feature
├── components/ui/  # Primitivas reutilizables (Button, Input, Dialog…)
├── hooks/          # Hooks genéricos
├── lib/            # cn(), cliente HTTP, utils, constantes
├── assets/
├── index.css       # @import "tailwindcss" + @theme + capas
└── main.tsx
```

- Una feature no importa archivos internos de otra: solo desde su `index.ts`.
- Alias `@/` → `src/` (configurado en `vite.config.ts` **y** `tsconfig.app.json`).

## Componentes

- Componentes **funcionales** con nombre en `PascalCase`; un componente principal por archivo, archivo con el mismo nombre (`UserCard.tsx`).
- Exportaciones **nombradas** (`export function UserCard`), salvo páginas con `lazy`.
- Tipa las props con `interface` o `type` explícito. **No uses `React.FC`.** No uses `any`; usa `unknown` y estrecha el tipo.
- Extiende props nativas para primitivas: `React.ComponentProps<"button">`.
- En React 19, `ref` es una prop normal: no necesitas `forwardRef`.
- Composición > configuración: prefiere `children` y slots a decenas de props booleanas.
- Mantén componentes pequeños (guía: < ~150 líneas). Extrae lógica a hooks y UI repetida a componentes.
- Accesibilidad por defecto: HTML semántico (`button`, `nav`, `main`, `label`), `alt` en imágenes, foco visible, `aria-*` solo cuando el HTML nativo no basta. Nunca `div` con `onClick` en lugar de `button`.

```tsx
import { cn } from "@/lib/utils";

interface BadgeProps extends React.ComponentProps<"span"> {
  tone?: "neutral" | "success" | "danger";
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        tone === "neutral" && "bg-zinc-100 text-zinc-700",
        tone === "success" && "bg-emerald-100 text-emerald-700",
        tone === "danger" && "bg-red-100 text-red-700",
        className,
      )}
      {...props}
    />
  );
}
```

## Hooks y estado

- Reglas de hooks siempre; deja que `eslint-plugin-react-hooks` te guíe. No silencies `exhaustive-deps`: arregla la causa.
- **No uses `useEffect` para derivar estado.** Calcula durante el render (o `useMemo` si es costoso de verdad). Usa `useEffect` solo para sincronizar con sistemas externos (suscripciones, DOM, timers).
- Estado: local primero (`useState`/`useReducer`) → elevar → Context para datos poco cambiantes (tema, usuario) → librería (Zustand) solo si hay estado global complejo.
- **Datos del servidor con TanStack Query**, no con `useEffect` + `fetch`. Detalles en `references/state-and-data.md`.
- Formularios: React Hook Form + Zod (`z.infer` para los tipos). En React 19 también valen Actions (`useActionState`).
- No memorices por reflejo (`useMemo`/`useCallback`/`memo`): mide primero. Si el proyecto usa React Compiler, no los añadas manualmente.
- Claves de listas: ids estables, nunca el índice si la lista puede reordenarse.

## TypeScript

- `strict: true`, `noUncheckedIndexedAccess: true`, `verbatimModuleSyntax: true`.
- `import type { … }` para importaciones solo de tipos.
- Modela estados con **uniones discriminadas** en vez de varios booleanos:
  ```ts
  type State =
    | { status: "idle" }
    | { status: "loading" }
    | { status: "success"; data: User }
    | { status: "error"; error: Error };
  ```
- Usa `satisfies` para validar objetos de configuración sin perder el tipo literal; evita `as` salvo casos justificados (nunca `as any`).
- Valida con Zod los datos que cruzan la frontera (API, localStorage, formularios) e infiere los tipos.
- Eventos tipados: `React.ChangeEvent<HTMLInputElement>`, `React.FormEvent<HTMLFormElement>`.

## Tailwind CSS (v4) y CSS

Resumen; detalle completo en `references/tailwind-css.md`.

- Estilos con **clases utilitarias** en el JSX. CSS propio solo para lo que Tailwind no cubre (animaciones complejas, selectores avanzados, estilos de contenido Markdown).
- Configuración **CSS-first**: tokens de diseño en `@theme` dentro de `index.css`, no clases mágicas dispersas ni valores arbitrarios repetidos (`w-[137px]`).
- Combina clases con `cn()` (`clsx` + `tailwind-merge`); variantes complejas con `cva`.
- **Mobile-first**: base = móvil, escala con `sm:`, `md:`, `lg:`.
- Nunca construyas clases dinámicas con strings parciales (`` `text-${color}-500` ``): Tailwind no las detecta. Usa mapas de clases completas.
- Dark mode con variante `dark:` y tokens semánticos (`bg-background`, `text-foreground`).
- Respeta `prefers-reduced-motion` (`motion-reduce:`).

## Vite

- Variables de entorno: solo `import.meta.env.VITE_*` (se exponen al cliente: **nunca secretos**). Tipa `ImportMetaEnv` en `src/vite-env.d.ts`.
- Plugin de Tailwind: `@tailwindcss/vite` (no PostCSS salvo necesidad).
- Code splitting por ruta con `React.lazy` + `Suspense`; importa dinámicamente librerías pesadas.
- Assets: imports desde `src/assets` (con hash) o `public/` para URLs fijas.
- Proxy de desarrollo en `server.proxy` para evitar CORS en local.

## Rendimiento

- Divide por rutas; evita cargar toda la app al inicio.
- Listas largas: virtualización (`@tanstack/react-virtual`).
- Imágenes: dimensiones explícitas (evita CLS), `loading="lazy"`, formatos modernos (WebP/AVIF).
- Evita crear componentes dentro de otros componentes.
- Usa `useTransition`/`useDeferredValue` para actualizaciones costosas no urgentes.

## Seguridad

- React escapa por defecto: **evita `dangerouslySetInnerHTML`**; si es imprescindible, sanea con DOMPurify.
- No guardes tokens sensibles en `localStorage` si puedes usar cookies `HttpOnly`.
- Valida y sanea toda entrada externa; no confíes en validación solo de cliente.
- Revisa dependencias nuevas (mantenimiento, tamaño, licencia) antes de instalarlas.

## Testing

Vitest + React Testing Library + `@testing-library/user-event`. Prueba **comportamiento visible** (roles, textos), no detalles de implementación. Consulta `references/testing-and-quality.md`.

## Definition of Done

Antes de dar una tarea por terminada, ejecuta (con el gestor del proyecto):

1. `tsc -b --noEmit` (o el script `typecheck`) → sin errores.
2. `lint` → sin errores ni warnings nuevos.
3. `test` → en verde; añade tests para lógica y componentes nuevos relevantes.
4. `build` → compila correctamente.
5. Revisión manual: responsive, teclado/foco, estados de carga/vacío/error, modo oscuro si aplica.

Si no puedes ejecutar alguno, dilo explícitamente en tu resumen.

## Qué evitar (anti-patrones)

- `any`, `// @ts-ignore`, `eslint-disable` sin comentario justificado.
- `useEffect` para derivar estado o para fetch manual.
- Prop drilling de más de 2–3 niveles (usa composición o Context).
- Estilos en línea (`style={{}}`) para cosas que Tailwind resuelve.
- `@apply` masivo que reconstruye CSS tradicional.
- Archivos "dios" de más de 300 líneas.
- Copiar/pegar componentes en lugar de abstraer.
- Instalar una librería para algo que se resuelve en 5 líneas.

## Referencias (léelas cuando aplique)

- `references/tailwind-css.md` → configuración v4, `@theme`, `cn`, `cva`, dark mode, CSS personalizado.
- `references/state-and-data.md` → TanStack Query, formularios, routing, Context/Zustand.
- `references/testing-and-quality.md` → Vitest, Testing Library, ESLint, Prettier, tsconfig recomendado.