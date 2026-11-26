from datetime import date

from django.core.management.base import BaseCommand, CommandError

from api.rbac import ROLES_NUEVOS
from catalogo.models import (
    Categoria,
    ClasificacionEdad,
    EstadoPublicacion,
    Genero,
    Idioma,
    OfertaVideojuego,
    Plataforma,
    Videojuego,
    VideojuegoCategoria,
    VideojuegoGenero,
    normalizar_nombre_catalogo,
)
from catalogo.catalogo_real import juegos_reales
from catalogo.portadas import url_portada_videojuego
from cuentas.models import Rol
from pagos.models import EstadoIntentoPago
from pedidos.models import EstadoPedido

# AZ-S2-BE-16: mínimos del catálogo sembrado. Si hay más categorías que las
# seis base, el objetivo global crece con ellas (20 por categoría).
MINIMO_VIDEOJUEGOS = 100
MINIMO_POR_CATEGORIA = 20


class Command(BaseCommand):
    help = "Pobla la base de datos con datos de prueba para Arcakane Zone."

    def handle(self, *args, **kwargs):
        estados_creados = self._seed_estados()
        roles_creados = self._seed_roles()
        cats_creadas = self._seed_categorias()
        plats_creadas = self._seed_plataformas()
        gens_creados = self._seed_generos()
        clas_creadas = self._seed_clasificaciones_edad()
        idiomas_creados = self._seed_idiomas()
        juegos_creados, ofertas_creadas = self._seed_catalogo_comercial()

        self.stdout.write(self.style.SUCCESS("\n=== Seed completado ==="))
        self.stdout.write(f"  Estados:        {estados_creados} creados")
        self.stdout.write(f"  Roles:          {roles_creados} creados")
        self.stdout.write(f"  Categorías:     {cats_creadas} creadas")
        self.stdout.write(f"  Plataformas:    {plats_creadas} creadas")
        self.stdout.write(f"  Géneros:        {gens_creados} creados")
        self.stdout.write(f"  Clasificaciones: {clas_creadas} creadas")
        self.stdout.write(f"  Idiomas:        {idiomas_creados} creados")
        self.stdout.write(f"  Videojuegos:    {juegos_creados} creados")
        self.stdout.write(f"  Ofertas:        {ofertas_creadas} creadas")

        # Evidencia de validación (AZ-S2-BE-16): total global y distribución.
        total = Videojuego.objects.count()
        objetivo = max(
            MINIMO_VIDEOJUEGOS,
            MINIMO_POR_CATEGORIA * Categoria.objects.count(),
        )
        self.stdout.write(f"  Total videojuegos: {total} (mínimo {objetivo})")
        for categoria in Categoria.objects.order_by("nombre"):
            self.stdout.write(
                f"    - {categoria.nombre}: {categoria.videojuegos.count()}"
            )

    # ------------------------------------------------------------------
    def _seed_estados(self):
        """Siembra idempotente de los catálogos de estado (AZ-S1-17)."""
        creados = 0
        for codigo, nombre in [
            ("pendiente", "Pendiente"),
            ("pagado", "Pagado"),
            ("cancelado", "Cancelado"),
        ]:
            _, nuevo = EstadoPedido.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre}
            )
            if nuevo:
                creados += 1
        for codigo, nombre in [
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
            ("pendiente", "Pendiente"),
        ]:
            _, nuevo = EstadoIntentoPago.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre}
            )
            if nuevo:
                creados += 1
        for codigo, nombre in [
            ("borrador", "Borrador"),
            ("publicado", "Publicado"),
            ("retirado", "Retirado"),
        ]:
            _, nuevo = EstadoPublicacion.objects.get_or_create(
                codigo=codigo, defaults={"nombre": nombre}
            )
            if nuevo:
                creados += 1
        return creados

    # ------------------------------------------------------------------
    def _seed_roles(self):
        """Siembra idempotente de roles base y de negocio (AZ-S1-18, AZ-S2-BE-07)."""
        creados = 0
        base = [("cliente", "Cliente", ""), ("administrador", "Administrador", "")]
        filas = base + [
            (rol["codigo"], rol["nombre"], rol["descripcion"]) for rol in ROLES_NUEVOS
        ]
        for codigo, nombre, descripcion in filas:
            _, nuevo = Rol.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "descripcion": descripcion},
            )
            if nuevo:
                creados += 1
        return creados

    def _seed_categorias(self):
        datos = [
            ("Acción", "Juegos de ritmo rápido con combate y reflejos."),
            ("Deportes", "Simulaciones de deportes reales o fantásticos."),
            ("Aventura", "Exploración, narrativa y resolución de acertijos."),
            ("Carreras", "Competencias de velocidad en circuitos y mundo abierto."),
            ("Estrategia", "Planificación táctica y gestión de recursos."),
            ("RPG", "Desarrollo de personaje y narrativa profunda."),
        ]
        creados = 0
        for nombre, desc in datos:
            _, nuevo = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            if nuevo:
                creados += 1
        return creados

    def _seed_plataformas(self):
        datos = [
            ("PC", "Computadores personales con Windows/Linux/Mac."),
            ("PlayStation 5", "Consola de Sony de novena generación."),
            ("Xbox Series X", "Consola de Microsoft de novena generación."),
            ("Nintendo Switch", "Consola híbrida portátil/sobremesa de Nintendo."),
        ]
        creados = 0
        for nombre, desc in datos:
            _, nuevo = Plataforma.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            if nuevo:
                creados += 1
        return creados

    def _seed_generos(self):
        datos = [
            ("Shooter", "Juegos de disparos en primera o tercera persona."),
            ("Mundo abierto", "Exploración libre en mapas extensos."),
            ("Deportivo", "Mecánicas basadas en deportes reales."),
            ("Plataformas", "Saltos y obstáculos en escenarios variados."),
            ("Rol", "Progresión de personaje con habilidades y equipo."),
            ("Simulación", "Recreación realista de actividades o entornos."),
        ]
        creados = 0
        for nombre, desc in datos:
            _, nuevo = Genero.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            if nuevo:
                creados += 1
        return creados

    def _seed_clasificaciones_edad(self):
        """Siembra idempotente del sistema PEGI (AZ-S1-20)."""
        datos = [
            ("3", "PEGI 3", 3),
            ("7", "PEGI 7", 7),
            ("12", "PEGI 12", 12),
            ("16", "PEGI 16", 16),
            ("18", "PEGI 18", 18),
        ]
        creados = 0
        for codigo, nombre, orden in datos:
            _, nuevo = ClasificacionEdad.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": normalizar_nombre_catalogo(nombre),
                    "orden": orden,
                },
            )
            if nuevo:
                creados += 1
        return creados

    def _seed_idiomas(self):
        """Siembra idempotente de idiomas comunes con código ISO 639-1 (AZ-S1-20)."""
        datos = [
            ("es", "Español"),
            ("en", "Inglés"),
            ("fr", "Francés"),
            ("de", "Alemán"),
            ("it", "Italiano"),
            ("pt", "Portugués"),
            ("ja", "Japonés"),
            ("ko", "Coreano"),
            ("zh", "Chino"),
            ("ru", "Ruso"),
        ]
        creados = 0
        for codigo, nombre in datos:
            _, nuevo = Idioma.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": normalizar_nombre_catalogo(nombre)},
            )
            if nuevo:
                creados += 1
        return creados

    # ------------------------------------------------------------------
    def _crear_videojuego(
        self,
        *,
        titulo,
        descripcion,
        fecha_lanzamiento,
        categoria,
        genero,
        ofertas,
        plt,
        clasificacion=None,
        desarrollador=None,
        prefijo_sku="AZ",
    ):
        """Crea (o reutiliza) un título con sus relaciones y ofertas."""
        videojuego, nuevo = Videojuego.objects.get_or_create(
            titulo=titulo,
            defaults={
                "descripcion": descripcion,
                "fecha_lanzamiento": fecha_lanzamiento,
                "clasificacion_edad": clasificacion,
                "desarrollador": desarrollador or "",
                "activo": True,
            },
        )
        juegos_creados = 1 if nuevo else 0

        # La URL y el desarrollador se calculan con la PK ya asignada, así que
        # se rellenan también en títulos creados antes de que existieran.
        url_portada = url_portada_videojuego(videojuego.pk, titulo)
        if (
            videojuego.imagen_url != url_portada
            or desarrollador
            and videojuego.desarrollador != desarrollador
        ):
            videojuego.imagen_url = url_portada
            if desarrollador:
                videojuego.desarrollador = desarrollador
            videojuego.save(update_fields=["imagen_url", "desarrollador"])

        VideojuegoCategoria.objects.get_or_create(
            videojuego=videojuego, categoria=categoria
        )
        VideojuegoGenero.objects.get_or_create(videojuego=videojuego, genero=genero)

        ofertas_creadas = 0
        for oferta in ofertas:
            plataforma = plt[oferta["plataforma"]]
            _, nueva = OfertaVideojuego.objects.get_or_create(
                videojuego=videojuego,
                plataforma=plataforma,
                defaults={
                    "sku": f"{prefijo_sku}-{videojuego.pk:04d}-{plataforma.pk:03d}",
                    "precio_vigente": oferta["precio"],
                    "stock": oferta["stock"],
                },
            )
            if nueva:
                ofertas_creadas += 1
        return juegos_creados, ofertas_creadas

    def _seed_catalogo_comercial(self):
        """Crea los 140 juegos reales del fixture y sus ofertas."""
        cat = {c.nombre: c for c in Categoria.objects.all()}
        plt = {p.nombre: p for p in Plataforma.objects.all()}
        gen = {g.nombre: g for g in Genero.objects.all()}
        clas = {c.codigo: c for c in ClasificacionEdad.objects.all()}

        juegos_creados = 0
        ofertas_creadas = 0
        titulos_extra: list[str] = []

        for datos in juegos_reales():
            es_extra = bool(datos.get("es_extra"))
            if es_extra:
                titulos_extra.append(datos["titulo"])
            # Los títulos de relleno también son juegos reales; mientras no
            # exista una categoría adicional se agrupan en Aventura.
            categoria = (
                "Aventura" if datos["categoria"] == "Extra" else datos["categoria"]
            )
            creados, ofertas = self._crear_videojuego(
                titulo=datos["titulo"],
                descripcion=datos["descripcion"],
                fecha_lanzamiento=date.fromisoformat(datos["fecha_lanzamiento"]),
                categoria=cat[categoria],
                genero=gen[datos["genero"]],
                ofertas=datos["ofertas"],
                plt=plt,
                clasificacion=clas[datos["clasificacion"]],
                desarrollador=datos["desarrollador"],
            )
            juegos_creados += creados
            ofertas_creadas += ofertas

        # Si el usuario creó categorías fuera de las seis base, les asignamos
        # los 20 títulos reales de relleno para mantener 20 por categoría.
        nombres_base = {
            juego["categoria"]
            for juego in juegos_reales()
            if not juego.get("es_extra")
        }
        juegos_extra = Videojuego.objects.filter(titulo__in=titulos_extra)
        for categoria in Categoria.objects.exclude(nombre__in=nombres_base):
            for juego in juegos_extra:
                VideojuegoCategoria.objects.get_or_create(
                    videojuego=juego, categoria=categoria
                )

        objetivo = max(
            MINIMO_VIDEOJUEGOS,
            MINIMO_POR_CATEGORIA * Categoria.objects.count(),
        )
        total = Videojuego.objects.count()
        if total < objetivo:
            raise CommandError(
                f"El catálogo realista tiene {total} juegos; se esperaban {objetivo}."
            )
        return juegos_creados, ofertas_creadas
