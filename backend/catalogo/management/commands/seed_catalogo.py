from datetime import date

from django.core.management.base import BaseCommand

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
from cuentas.models import Rol
from pagos.models import EstadoIntentoPago
from pedidos.models import EstadoPedido

# AZ-S2-BE-16: mínimos del catálogo sembrado. Si hay más categorías que las
# seis base, el objetivo global crece con ellas (20 por categoría).
MINIMO_VIDEOJUEGOS = 100
MINIMO_POR_CATEGORIA = 20

GENERO_POR_CATEGORIA = {
    "Acción": "Shooter",
    "Aventura": "Mundo abierto",
    "Carreras": "Simulación",
    "Deportes": "Deportivo",
    "Estrategia": "Simulación",
    "RPG": "Rol",
}
CLASIFICACIONES_ROTACION = ("3", "7", "12", "16", "18")
PLATAFORMAS_ROTACION = ("PC", "PlayStation 5", "Xbox Series X", "Nintendo Switch")

# Títulos de prueba complementarios. Se consumen solo hasta completar 20 por
# categoría, por lo que los 15 juegos históricos se conservan sin duplicarlos.
TITULOS_COMPLEMENTARIOS = {
    "Acción": [
        "Asalto al amanecer",
        "Ataque en la cumbre",
        "Cazador de sombras",
        "Combate en la penumbra",
        "Duelo de titanes",
        "Escape de la fortaleza",
        "Furia de acero",
        "Golpe mortal",
        "Operación Relámpago",
        "Raid en la ciudad baja",
        "Rescate en la factoría",
        "Sendero de cenizas",
        "Tormenta de fuego",
        "Última línea de defensa",
        "Venganza del norte",
        "Zona de impacto",
        "Asedio en el puerto",
        "Contrataque final",
        "Punto de ruptura",
        "Sabotaje nocturno",
    ],
    "Aventura": [
        "Cartografía del vacío",
        "Cuevas de cristal",
        "Diario de una expedición",
        "El bosque susurrante",
        "El faro perdido",
        "El secreto del manantial",
        "En busca de la brújula",
        "Islas flotantes",
        "La ciudad sumergida",
        "La llave de los ecos",
        "Las ruinas de Aztlán",
        "Los restos del templo",
        "Memoria de arena",
        "Murmullos del valle",
        "Naufragio en el archipiélago",
        "Obsidiana y niebla",
        "Tras el rastro de las estrellas",
        "Viaje al fondo del cañón",
        "La puerta de sal",
        "El mapa de los vientos",
    ],
    "Carreras": [
        "Auto-x en la costa",
        "Carrera de resistencia",
        "Circuitos de cristal",
        "Clásico de montaña",
        "Contrarreloj nocturna",
        "Duna salvaje",
        "Escape en la autopista",
        "Fórmula de neón",
        "Gran premio de invierno",
        "Karting de precisión",
        "Las mil curvas",
        "Meta en la cumbre",
        "Nitro en el desierto",
        "Rally de cenizas",
        "Relevos de velocidad",
        "Ruta de los faros",
        "Sprint en la ciudad",
        "Turismo de élite",
        "Carrera de los récords",
        "Pista del volcán",
    ],
    "Deportes": [
        "Baloncesto callejero",
        "Campeonato de invierno",
        "Copa de las naciones",
        "Derbi de neón",
        "Entrenamiento de élite",
        "Estadio de cristal",
        "Fútbol de barrio",
        "Grand Slam nocturno",
        "Liga de acero",
        "Maratón urbana",
        "Partido de medianoche",
        "Pelota en llamas",
        "Renacimiento olímpico",
        "Rodeo de superficie",
        "Tenis en la azotea",
        "Torneo de gladiadores",
        "Victoria en la prórroga",
        "Voley playa extremo",
        "Ciclismo de montaña",
        "Boxeo en el ring",
    ],
    "Estrategia": [
        "Asedio a la muralla",
        "Batalla de los estados",
        "Campañas de invierno",
        "Ciudadela de cristal",
        "Conquista del delta",
        "Duque de las tierras altas",
        "El consejo de los diez",
        "El gran sitio",
        "Economía de guerra",
        "Ejércitos de papel",
        "Fronteras del imperio",
        "Guerra de los puertos",
        "Imperio de sal",
        "La línea de defensa",
        "Logística de campaña",
        "Reino de las llanuras",
        "Reforma tributaria",
        "Sitio de la capital",
        "Tratado de los ríos",
        "Alianza de los valles",
    ],
    "RPG": [
        "Aprendiz de hechicero",
        "Caballeros del crepúsculo",
        "Crónicas de Ardevia",
        "El pacto de los antiguos",
        "El último paladín",
        "La corona partida",
        "Los elegidos del caos",
        "Maestros del arcano",
        "Mercenarios del norte",
        "Oráculo de piedra",
        "Raíces del mal",
        "Reino de ceniza",
        "Sangre de dragón",
        "Secta del amanecer",
        "Templo de los deseos",
        "Vástagos de la luna",
        "Herencia de los dioses",
        "La espada errante",
        "Pacto de sangre",
        "Ruinas del destino",
    ],
}

# Para categorías creadas fuera de la semilla se generan títulos distintos,
# siempre prefijados con el nombre de la categoría para evitar colisiones.
ADJETIVOS_EXTRA = ("Nocturno", "Crómatico", "Silvestre", "Metálico", "Sereno")
SUSTANTIVOS_EXTRA = ("expedición", "duelo", "travesía", "asaltos", "leyenda")


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
        prefijo_sku="AZ",
    ):
        """Crea (o reutiliza) un título con sus relaciones y ofertas."""
        videojuego, nuevo = Videojuego.objects.get_or_create(
            titulo=titulo,
            defaults={
                "descripcion": descripcion,
                "fecha_lanzamiento": fecha_lanzamiento,
                "clasificacion_edad": clasificacion,
                "activo": True,
            },
        )
        juegos_creados = 1 if nuevo else 0

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

    @staticmethod
    def _fecha_generada(indice):
        """Fecha determinista y válida para los títulos complementarios."""
        return date(2014 + indice % 11, 1 + indice % 12, 1 + indice % 28)

    @staticmethod
    def _ofertas_generadas(indice):
        """Una o dos ofertas por título, con precios y stock variados."""
        total = len(PLATAFORMAS_ROTACION)
        primera = PLATAFORMAS_ROTACION[indice % total]
        segunda = PLATAFORMAS_ROTACION[(indice + 1) % total]
        ofertas = [
            {
                "plataforma": primera,
                "precio": 39900 + (indice % 12) * 5000,
                "stock": 4 + (indice % 10),
            }
        ]
        if indice % 3 == 0:
            ofertas.append(
                {
                    "plataforma": segunda,
                    "precio": 34900 + (indice % 8) * 4000,
                    "stock": 2 + (indice % 6),
                }
            )
        return ofertas

    @staticmethod
    def _titulos_para_categoria_extra(categoria):
        """Títulos únicos para categorías creadas fuera de la semilla base."""
        return [
            f"{categoria.nombre}: "
            f"{ADJETIVOS_EXTRA[i % len(ADJETIVOS_EXTRA)]} "
            f"{SUSTANTIVOS_EXTRA[(i // len(ADJETIVOS_EXTRA)) % len(SUSTANTIVOS_EXTRA)]}"
            for i in range(MINIMO_POR_CATEGORIA)
        ]

    def _completar_categoria(self, categoria, titulos, plt, gen, clas):
        """Llena hasta 20 juegos una categoría, sin repetir títulos."""
        existentes = set(
            Videojuego.objects.filter(vinculos_categoria__categoria=categoria)
            .values_list("titulo", flat=True)
        )
        faltan = MINIMO_POR_CATEGORIA - len(existentes)
        if faltan <= 0:
            return 0, 0

        genero = gen[GENERO_POR_CATEGORIA.get(categoria.nombre, "Simulación")]
        juegos_creados = 0
        ofertas_creadas = 0
        for indice, titulo in enumerate(titulos):
            if titulo in existentes:
                continue
            codigo = CLASIFICACIONES_ROTACION[
                indice % len(CLASIFICACIONES_ROTACION)
            ]
            creados, ofertas = self._crear_videojuego(
                titulo=titulo,
                descripcion=(
                    f"{titulo}. Título de prueba de {categoria.nombre.lower()} "
                    f"con mecánicas de {genero.nombre.lower()} "
                    "para el catálogo de Arcakane Zone."
                ),
                fecha_lanzamiento=self._fecha_generada(indice),
                categoria=categoria,
                genero=genero,
                ofertas=self._ofertas_generadas(indice),
                plt=plt,
                clasificacion=clas[codigo],
                prefijo_sku="AZ-SEED",
            )
            juegos_creados += creados
            ofertas_creadas += ofertas
            existentes.add(titulo)
            faltan -= 1
            if faltan == 0:
                break
        return juegos_creados, ofertas_creadas

    def _completar_total_global(self, plt, gen, clas):
        """Garantiza el mínimo global aunque falten categorías sembradas."""
        objetivo = max(
            MINIMO_VIDEOJUEGOS,
            MINIMO_POR_CATEGORIA * Categoria.objects.count(),
        )
        categorias = list(Categoria.objects.order_by("nombre"))
        if not categorias:
            return 0, 0

        juegos_creados = 0
        ofertas_creadas = 0
        indice = 0
        while Videojuego.objects.count() < objetivo and indice < objetivo * 2:
            categoria = categorias[indice % len(categorias)]
            genero = gen[GENERO_POR_CATEGORIA.get(categoria.nombre, "Simulación")]
            codigo = CLASIFICACIONES_ROTACION[
                indice % len(CLASIFICACIONES_ROTACION)
            ]
            creados, ofertas = self._crear_videojuego(
                titulo=f"Catálogo de prueba {indice + 1:04d} · {categoria.nombre}",
                descripcion=(
                    f"Título de prueba {indice + 1} de {categoria.nombre.lower()} "
                    "para validar el catálogo de Arcakane Zone."
                ),
                fecha_lanzamiento=self._fecha_generada(indice + 100),
                categoria=categoria,
                genero=genero,
                ofertas=self._ofertas_generadas(indice + 100),
                plt=plt,
                clasificacion=clas[codigo],
                prefijo_sku="AZ-SEED",
            )
            juegos_creados += creados
            ofertas_creadas += ofertas
            indice += 1
        return juegos_creados, ofertas_creadas

    def _seed_catalogo_comercial(self):
        """
        Pobla la identidad de los videojuegos y sus ofertas por plataforma.
        Un mismo título puede venderse en varias plataformas con precio,
        SKU y stock propios.
        """
        cat = {c.nombre: c for c in Categoria.objects.all()}
        plt = {p.nombre: p for p in Plataforma.objects.all()}
        gen = {g.nombre: g for g in Genero.objects.all()}

        juegos = [
            {
                "titulo": "God of War Ragnarök",
                "descripcion": "Kratos y Atreus enfrentan el Ragnarök nórdico en una épica aventura de acción.",
                "fecha_lanzamiento": date(2022, 11, 9),
                "categoria": cat["Acción"],
                "genero": gen["Mundo abierto"],
                "ofertas": [
                    {"plataforma": "PlayStation 5", "precio": 219900, "stock": 10},
                    {"plataforma": "PC", "precio": 199900, "stock": 6},
                ],
            },
            {
                "titulo": "The Legend of Zelda: Tears of the Kingdom",
                "descripcion": "Link explora Hyrule y los cielos en una nueva aventura de mundo abierto.",
                "fecha_lanzamiento": date(2023, 5, 12),
                "categoria": cat["Aventura"],
                "genero": gen["Mundo abierto"],
                "ofertas": [
                    {"plataforma": "Nintendo Switch", "precio": 249900, "stock": 8},
                ],
            },
            {
                "titulo": "Elden Ring",
                "descripcion": "RPG de acción oscura en el vasto mundo entre-tierras, creado con George R.R. Martin.",
                "fecha_lanzamiento": date(2022, 2, 25),
                "categoria": cat["RPG"],
                "genero": gen["Rol"],
                "ofertas": [
                    {"plataforma": "PC", "precio": 199900, "stock": 15},
                    {"plataforma": "PlayStation 5", "precio": 209900, "stock": 7},
                    {"plataforma": "Xbox Series X", "precio": 209900, "stock": 4},
                ],
            },
            {
                "titulo": "FIFA 24",
                "descripcion": "La entrega anual de fútbol con licencias oficiales de ligas y selecciones.",
                "fecha_lanzamiento": date(2023, 9, 29),
                "categoria": cat["Deportes"],
                "genero": gen["Deportivo"],
                "ofertas": [
                    {"plataforma": "PlayStation 5", "precio": 189900, "stock": 20},
                    {"plataforma": "Xbox Series X", "precio": 189900, "stock": 12},
                    {"plataforma": "PC", "precio": 149900, "stock": 9},
                ],
            },
            {
                "titulo": "Forza Horizon 5",
                "descripcion": "Carreras en mundo abierto ambientadas en los coloridos paisajes de México.",
                "fecha_lanzamiento": date(2021, 11, 9),
                "categoria": cat["Carreras"],
                "genero": gen["Mundo abierto"],
                "ofertas": [
                    {"plataforma": "Xbox Series X", "precio": 179900, "stock": 12},
                    {"plataforma": "PC", "precio": 169900, "stock": 5},
                ],
            },
            {
                "titulo": "Halo Infinite",
                "descripcion": "El Jefe Maestro regresa en un shooter de ciencia ficción épico y multijugador.",
                "fecha_lanzamiento": date(2021, 12, 8),
                "categoria": cat["Acción"],
                "genero": gen["Shooter"],
                "ofertas": [
                    {"plataforma": "Xbox Series X", "precio": 159900, "stock": 9},
                ],
            },
            {
                "titulo": "Hogwarts Legacy",
                "descripcion": "Vive tu propia historia en el mundo mágico del siglo XIX del universo Harry Potter.",
                "fecha_lanzamiento": date(2023, 2, 10),
                "categoria": cat["RPG"],
                "genero": gen["Rol"],
                "ofertas": [
                    {"plataforma": "PlayStation 5", "precio": 209900, "stock": 7},
                    {"plataforma": "PC", "precio": 189900, "stock": 0},
                ],
            },
            {
                "titulo": "Super Mario Bros. Wonder",
                "descripcion": "Mario y sus amigos exploran el Reino de las Flores con nuevas mecánicas Wonder.",
                "fecha_lanzamiento": date(2023, 10, 20),
                "categoria": cat["Acción"],
                "genero": gen["Plataformas"],
                "ofertas": [
                    {"plataforma": "Nintendo Switch", "precio": 229900, "stock": 14},
                ],
            },
            {
                "titulo": "Cyberpunk 2077",
                "descripcion": "RPG de mundo abierto en Night City, una megalópolis del futuro obsesionada con el poder.",
                "fecha_lanzamiento": date(2020, 12, 10),
                "categoria": cat["RPG"],
                "genero": gen["Mundo abierto"],
                "ofertas": [
                    {"plataforma": "PC", "precio": 149900, "stock": 18},
                    {"plataforma": "PlayStation 5", "precio": 159900, "stock": 5},
                ],
            },
            {
                "titulo": "NBA 2K24",
                "descripcion": "La simulación de baloncesto más completa con modos carrera, MyTeam y online.",
                "fecha_lanzamiento": date(2023, 9, 8),
                "categoria": cat["Deportes"],
                "genero": gen["Deportivo"],
                "ofertas": [
                    {"plataforma": "Xbox Series X", "precio": 189900, "stock": 11},
                ],
            },
            {
                "titulo": "Age of Empires IV",
                "descripcion": "Estrategia en tiempo real con civilizaciones históricas de la Edad Media.",
                "fecha_lanzamiento": date(2021, 10, 28),
                "categoria": cat["Estrategia"],
                "genero": gen["Simulación"],
                "ofertas": [
                    {"plataforma": "PC", "precio": 139900, "stock": 6},
                ],
            },
            {
                "titulo": "Gran Turismo 7",
                "descripcion": "Simulador de carreras con más de 400 autos licenciados y físicas ultra realistas.",
                "fecha_lanzamiento": date(2022, 3, 4),
                "categoria": cat["Carreras"],
                "genero": gen["Simulación"],
                "ofertas": [
                    {"plataforma": "PlayStation 5", "precio": 219900, "stock": 0},
                ],
            },
            {
                "titulo": "Baldur's Gate 3",
                "descripcion": "RPG por turnos basado en D&D con decisiones que moldean cada aspecto de la historia.",
                "fecha_lanzamiento": date(2023, 8, 3),
                "categoria": cat["RPG"],
                "genero": gen["Rol"],
                "ofertas": [
                    {"plataforma": "PC", "precio": 199900, "stock": 5},
                    {"plataforma": "PlayStation 5", "precio": 219900, "stock": 2},
                ],
            },
            {
                "titulo": "Mortal Kombat 1",
                "descripcion": "Reinicio de la saga con nuevos Kameos, historia épica y brutal combate en HD.",
                "fecha_lanzamiento": date(2023, 9, 19),
                "categoria": cat["Acción"],
                "genero": gen["Shooter"],
                "ofertas": [
                    {"plataforma": "PlayStation 5", "precio": 209900, "stock": 0},
                ],
            },
            {
                "titulo": "Starfield",
                "descripcion": "RPG espacial de Bethesda con más de 1000 planetas explorables y libertad total.",
                "fecha_lanzamiento": date(2023, 9, 6),
                "categoria": cat["Aventura"],
                "genero": gen["Mundo abierto"],
                "ofertas": [
                    {"plataforma": "Xbox Series X", "precio": 219900, "stock": 13},
                    {"plataforma": "PC", "precio": 209900, "stock": 3},
                ],
            },
        ]

        juegos_creados = 0
        ofertas_creadas = 0
        clas = {c.codigo: c for c in ClasificacionEdad.objects.all()}

        # Títulos históricos: se conservan con su descripción, fecha y ofertas.
        for indice, datos in enumerate(juegos):
            codigo = CLASIFICACIONES_ROTACION[
                indice % len(CLASIFICACIONES_ROTACION)
            ]
            creados, ofertas = self._crear_videojuego(
                titulo=datos["titulo"],
                descripcion=datos["descripcion"],
                fecha_lanzamiento=datos["fecha_lanzamiento"],
                categoria=datos["categoria"],
                genero=datos["genero"],
                ofertas=datos["ofertas"],
                plt=plt,
                clasificacion=clas[codigo],
            )
            juegos_creados += creados
            ofertas_creadas += ofertas

        # Complemento hasta 20 por categoría. También cubre categorías que el
        # usuario haya creado fuera de las seis base (AZ-S2-BE-16).
        for categoria in Categoria.objects.order_by("nombre"):
            titulos = TITULOS_COMPLEMENTARIOS.get(
                categoria.nombre,
                self._titulos_para_categoria_extra(categoria),
            )
            creados, ofertas = self._completar_categoria(
                categoria, titulos, plt, gen, clas
            )
            juegos_creados += creados
            ofertas_creadas += ofertas

        creados, ofertas = self._completar_total_global(plt, gen, clas)
        juegos_creados += creados
        ofertas_creadas += ofertas
        return juegos_creados, ofertas_creadas
