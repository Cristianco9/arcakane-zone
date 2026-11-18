# AGENTS.md

Instrucciones para agentes de código en este repositorio.
Stack: **React + TypeScript (strict) + Vite + Tailwind CSS v4 + CSS**.

> Para reglas detalladas usa la skill `react-vite-ts-tailwind` (`.claude/skills/react-vite-ts-tailwind/`).
> Este archivo contiene solo lo imprescindible y los comandos del proyecto.

## Comandos

Usa el gestor indicado por el lockfile (por defecto `npm`).

| Tarea | Comando |
|---|---|
| Instalar | `npm install` |
| Desarrollo | `npm run dev` |
| Tipos | `npm run typecheck` |
| Lint | `npm run lint` |
| Tests | `npm run test` |
| Build | `npm run build` |
| Formato | `npm run format` |

## Flujo de trabajo

1. Lee el código existente y reutiliza componentes, hooks y utilidades antes de crear nuevos.
2. Haz cambios pequeños y enfocados en la tarea; no refactorices código ajeno.
3. Antes de terminar ejecuta: `typecheck` → `lint` → `test` → `build`. Todo debe pasar.
4. Resume qué cambiaste y menciona cualquier comprobación que no pudiste ejecutar.

## Convenciones de código

- TypeScript estricto: **prohibido** `any`, `@ts-ignore` y `as any`. Usa `unknown`, genéricos y uniones discriminadas.
- Componentes funcionales, `PascalCase`, exportación nombrada, props tipadas. No usar `React.FC`.
- Alias `@/` para importar desde `src/`. `import type` para tipos.
- Estructura por features en `src/features/<nombre>/`; primitivas UI en `src/components/ui/`.
- No uses `useEffect` para derivar estado ni para pedir datos: usa TanStack Query.
- Formularios: React Hook Form + Zod.
- Estilos: utilidades de Tailwind + `cn()` (`clsx` + `tailwind-merge`); variantes con `cva`. Tokens en `@theme` (`src/index.css`).
- Mobile-first; clases dinámicas siempre completas (nunca `` `bg-${x}-500` ``).
- CSS propio solo si Tailwind no alcanza, dentro de `@layer`.
- Accesibilidad: HTML semántico, labels, foco visible, `alt` en imágenes.

## Seguridad

- Variables de entorno del cliente: solo `VITE_*` y **nunca secretos**.
- No usar `dangerouslySetInnerHTML` sin sanear. No commitear `.env*` con credenciales.
- Valida con Zod los datos externos (API, storage).

## Dependencias

- No añadas ni actualices dependencias sin necesidad clara; prefiere soluciones con lo que ya existe.
- Si añades una, justifícalo en el resumen (qué problema resuelve, tamaño, mantenimiento).

## Testing

- Vitest + Testing Library. Pruebas junto al código (`*.test.tsx`).
- Consulta por rol/label; usa `userEvent`; mockea red con MSW.
- Toda lógica nueva o bug corregido debe llevar test.

## Límites (pregunta antes de)

- Cambiar `vite.config.ts`, `tsconfig*.json` o la configuración de lint/CI.
- Eliminar archivos, migrar versiones mayores o cambiar la estructura de carpetas.
- Tocar autenticación, pagos o datos sensibles.