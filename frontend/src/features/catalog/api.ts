import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import catalogCover from "../../assets/covers/catalog-placeholder.svg";
import type {
  CatalogCategory,
  Product,
  ProductOffer,
} from "./types";

const BASE_URL = "/api/v1/catalogo";
const PAGE_SIZE = 100;

// La API devuelve `pagination: {}` cuando no hay resultados. Lo normalizamos
// para que el catálogo vacío muestre el estado vacío, no un error de contrato.
const PaginationSchema = z.preprocess(
  (valor) => {
    if (valor && typeof valor === "object" && !Object.keys(valor).length) {
      return {
        count: 0,
        page: 1,
        page_size: PAGE_SIZE,
        total_pages: 1,
        next: null,
        previous: null,
      };
    }
    return valor;
  },
  z.object({
    count: z.number(),
    page: z.number(),
    page_size: z.number(),
    total_pages: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
  }),
);

function envelope<T>(data: z.ZodType<T>) {
  return z.object({
    success: z.boolean(),
    data,
    message: z.string().optional(),
    pagination: PaginationSchema.optional(),
  });
}

const OfertaApiSchema = z.object({
  id: z.number(),
  plataforma: z.number(),
  plataforma_nombre: z.string(),
  sku: z.string(),
  precio_vigente: z.union([z.string(), z.number()]),
  stock: z.number(),
  estado_publicacion: z.enum(["publicado", "borrador", "retirado"]),
  disponible: z.boolean(),
});

const VideojuegoApiSchema = z.object({
  id: z.number(),
  titulo: z.string(),
  desarrollador: z.string(),
  descripcion: z.string(),
  portada: z.string().nullable(),
  imagen_url: z.string(),
  fecha_lanzamiento: z.string().nullable(),
  categoria: z.number().nullable(),
  categoria_nombre: z.string().nullable(),
  categorias: z.array(z.number()),
  genero: z.number().nullable(),
  genero_nombre: z.string().nullable(),
  generos: z.array(z.number()),
  activo: z.boolean(),
  disponible: z.boolean(),
  ofertas: z.array(OfertaApiSchema),
});

const CatalogoMaestroApiSchema = z.object({
  id: z.number(),
  nombre: z.string(),
  descripcion: z.string(),
  activo: z.boolean(),
});

type VideojuegoApi = z.infer<typeof VideojuegoApiSchema>;
type CatalogoMaestroApi = z.infer<typeof CatalogoMaestroApiSchema>;

async function fetchEnvelope<T>(
  url: string,
  schema: z.ZodType<T>,
): Promise<T> {
  const respuesta = await fetch(url, { headers: { Accept: "application/json" } });
  if (!respuesta.ok) {
    throw new Error(`No se pudo cargar ${url} (HTTP ${respuesta.status}).`);
  }

  const cuerpo: unknown = await respuesta.json();
  const resultado = schema.safeParse(cuerpo);
  if (!resultado.success) {
    throw new Error(`La respuesta de ${url} no tiene el formato esperado.`);
  }
  return resultado.data;
}

async function fetchPaginas<T>(
  path: string,
  schema: z.ZodType<T>,
): Promise<T[]> {
  const resultados: T[] = [];
  let pagina = 1;

  for (;;) {
    const separador = path.includes("?") ? "&" : "?";
    const url = `${path}${separador}page=${pagina}&page_size=${PAGE_SIZE}`;
    const respuesta = await fetchEnvelope(url, envelope(z.array(schema)));
    resultados.push(...respuesta.data);
    const totalPaginas = respuesta.pagination?.total_pages ?? 1;
    pagina += 1;
    if (pagina > totalPaginas) break;
  }

  return resultados;
}

function aCategoria(item: CatalogoMaestroApi): CatalogCategory {
  return {
    id: String(item.id),
    name: item.nombre,
    description: item.descripcion,
  };
}

function aProducto(
  item: VideojuegoApi,
  categorias: readonly CatalogCategory[],
): Product {
  const idCategoria = item.categoria ?? item.categorias[0] ?? null;
  const categoria = categorias.find(
    (candidata) => candidata.id === String(idCategoria),
  );
  const nombreCategoria =
    item.categoria_nombre ?? categoria?.name ?? "Sin categoría";
  const idGenero = item.genero ?? item.generos[0] ?? null;

  const ofertas: ProductOffer[] = item.ofertas.map((oferta) => ({
    id: `o-${oferta.id}`,
    platform: oferta.plataforma_nombre,
    sku: oferta.sku,
    price: Number(oferta.precio_vigente),
    stock: oferta.stock,
    status: oferta.estado_publicacion,
  }));

  return {
    id: String(item.id),
    title: item.titulo,
    description: item.descripcion,
    longDescription: item.descripcion || "Sin descripción disponible.",
    cover: item.imagen_url || item.portada || catalogCover,
    gallery: [],
    releaseDate: item.fecha_lanzamiento ?? "",
    category: {
      id: idCategoria === null ? "0" : String(idCategoria),
      name: nombreCategoria,
      description: categoria?.description ?? "",
    },
    genre: {
      id: idGenero === null ? "0" : String(idGenero),
      name: item.genero_nombre ?? "Sin género",
    },
    developer: item.desarrollador || "Arcakane Zone",
    featured: false,
    tags: [nombreCategoria, item.genero_nombre].filter(
      (valor): valor is string => Boolean(valor),
    ),
    features: [
      { label: "Estado", value: item.disponible ? "Disponible" : "Sin stock" },
      {
        label: "Ediciones",
        value: `${ofertas.filter((oferta) => oferta.status === "publicado").length} publicadas`,
      },
    ],
    offers: ofertas,
  };
}

export function useCatalogCategories() {
  return useQuery({
    queryKey: ["catalogo", "categorias"],
    queryFn: async () =>
      (await fetchPaginas(`${BASE_URL}/categorias/`, CatalogoMaestroApiSchema)).map(
        aCategoria,
      ),
  });
}

export function useCatalogPlatforms() {
  return useQuery({
    queryKey: ["catalogo", "plataformas"],
    queryFn: async () =>
      (
        await fetchPaginas(`${BASE_URL}/plataformas/`, CatalogoMaestroApiSchema)
      ).map((plataforma) => plataforma.nombre),
  });
}

export function useCatalogProducts() {
  const categorias = useCatalogCategories();
  return useQuery({
    queryKey: ["catalogo", "videojuegos", categorias.data],
    queryFn: async () =>
      (
        await fetchPaginas(`${BASE_URL}/videojuegos/`, VideojuegoApiSchema)
      ).map((videojuego) => aProducto(videojuego, categorias.data ?? [])),
    enabled: categorias.isSuccess,
  });
}

export function useCatalogProduct(productId: string | undefined) {
  return useQuery({
    queryKey: ["catalogo", "videojuego", productId],
    queryFn: async () => {
      if (!productId) return null;
      const url = `${BASE_URL}/videojuegos/${encodeURIComponent(productId)}/`;
      const respuesta = await fetch(url, {
        headers: { Accept: "application/json" },
      });
      if (respuesta.status === 404) return null;
      if (!respuesta.ok) {
        throw new Error(`No se pudo cargar ${url} (HTTP ${respuesta.status}).`);
      }
      const cuerpo: unknown = await respuesta.json();
      const resultado = envelope(VideojuegoApiSchema).safeParse(cuerpo);
      if (!resultado.success) {
        throw new Error(`La respuesta de ${url} no tiene el formato esperado.`);
      }
      return aProducto(resultado.data.data, []);
    },
    enabled: Boolean(productId),
  });
}
