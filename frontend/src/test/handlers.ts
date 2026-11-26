import { http, HttpResponse } from "msw";
import {
  categories,
  platforms,
  products,
} from "../features/catalog/data/mockData";
import type { ProductOffer } from "../features/catalog/types";

const categoriasApi = categories.map((categoria) => ({
  id: Number(categoria.id),
  nombre: categoria.name,
  descripcion: categoria.description,
  activo: true,
}));

const plataformasApi = platforms.map((nombre, indice) => ({
  id: indice + 1,
  nombre,
  descripcion: "",
  activo: true,
}));

let siguienteOfertaId = 1;

function ofertaApi(oferta: ProductOffer) {
  return {
    id: siguienteOfertaId++,
    plataforma: plataformasApi.find((item) => item.nombre === oferta.platform)?.id ?? 0,
    plataforma_nombre: oferta.platform,
    sku: oferta.sku,
    precio_vigente: String(oferta.price),
    stock: oferta.stock,
    estado_publicacion: oferta.status,
    disponible: oferta.stock > 0,
  };
}

const videojuegosApi = products.map((producto) => {
  const ofertas = producto.offers.map(ofertaApi);
  return {
    id: Number(producto.id),
    titulo: producto.title,
    descripcion: producto.description,
    portada: producto.cover,
    fecha_lanzamiento: producto.releaseDate,
    categoria: Number(producto.category.id),
    categoria_nombre: producto.category.name,
    categorias: [Number(producto.category.id)],
    genero: Number(producto.genre.id),
    genero_nombre: producto.genre.name,
    generos: [Number(producto.genre.id)],
    activo: true,
    disponible: ofertas.some((oferta) => oferta.disponible),
    ofertas,
  };
});

function paginado<T>(datos: readonly T[], solicitud: Request) {
  const url = new URL(solicitud.url);
  const pagina = Number(url.searchParams.get("page") ?? "1");
  const tamano = Number(url.searchParams.get("page_size") ?? "20");
  const inicio = (pagina - 1) * tamano;
  const totalPaginas = Math.max(1, Math.ceil(datos.length / tamano));

  return {
    success: true,
    data: datos.slice(inicio, inicio + tamano),
    pagination: {
      count: datos.length,
      page: pagina,
      page_size: tamano,
      total_pages: totalPaginas,
      next: pagina < totalPaginas ? `?page=${pagina + 1}` : null,
      previous: pagina > 1 ? `?page=${pagina - 1}` : null,
    },
  };
}

export const handlers = [
  http.get("/api/v1/catalogo/categorias", ({ request }) =>
    HttpResponse.json(paginado(categoriasApi, request)),
  ),
  http.get("/api/v1/catalogo/plataformas", ({ request }) =>
    HttpResponse.json(paginado(plataformasApi, request)),
  ),
  http.get("/api/v1/catalogo/videojuegos", ({ request }) =>
    HttpResponse.json(paginado(videojuegosApi, request)),
  ),
  http.get("/api/v1/catalogo/videojuegos/:id/", ({ params }) => {
    const videojuego = videojuegosApi.find(
      (item) => item.id === Number(params.id),
    );
    if (!videojuego) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json({ success: true, data: videojuego });
  }),
];
