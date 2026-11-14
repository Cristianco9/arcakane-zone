from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Plataforma(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plataforma"
        verbose_name_plural = "Plataformas"

    def __str__(self):
        return self.nombre


class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"

    def __str__(self):
        return self.nombre


class Videojuego(models.Model):
    """
    Identidad e información común de un título.

    El videojuego NO conoce precio, stock ni plataforma: esos atributos
    dependen de la presentación comercial vendible (``OfertaVideojuego``),
    que combina este título con una plataforma concreta.
    """

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    portada = models.ImageField(upload_to="portadas/", null=True, blank=True)
    fecha_lanzamiento = models.DateField(null=True, blank=True)
    # Un título puede pertenecer a varias categorías y géneros. El vínculo se
    # materializa en las tablas puente VideojuegoCategoria / VideojuegoGenero.
    categorias = models.ManyToManyField(
        Categoria,
        through="VideojuegoCategoria",
        related_name="videojuegos",
        blank=True,
    )
    generos = models.ManyToManyField(
        Genero,
        through="VideojuegoGenero",
        related_name="videojuegos",
        blank=True,
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Videojuego"
        verbose_name_plural = "Videojuegos"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo

    @property
    def disponible(self) -> bool:
        """Un título es vendible si alguna de sus ofertas está publicada y con stock."""
        return self.ofertas.vendibles().exists()


class VideojuegoCategoria(models.Model):
    """
    Asociación explícita entre un videojuego y una categoría del catálogo.

    Regla de negocio: un videojuego puede tener varias categorías y una
    categoría agrupa varios videojuegos, pero la pareja
    (videojuego, categoría) no puede repetirse. La base de datos lo garantiza
    con un UniqueConstraint, no solo la aplicación.
    """

    videojuego = models.ForeignKey(
        Videojuego, on_delete=models.CASCADE, related_name="vinculos_categoria"
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="vinculos_videojuego"
    )

    class Meta:
        verbose_name = "Categoría del videojuego"
        verbose_name_plural = "Categorías del videojuego"
        constraints = [
            models.UniqueConstraint(
                fields=["videojuego", "categoria"],
                name="catalogo_videojuegocategoria_videojuego_categoria_unicos",
            ),
        ]
        indexes = [
            # Listado de videojuegos por categoría (consulta inversa del M2M).
            models.Index(
                fields=["categoria", "videojuego"],
                name="catalogo_vjc_categoria_idx",
            ),
        ]

    def __str__(self):
        return f"{self.videojuego.titulo} · {self.categoria.nombre}"


class VideojuegoGenero(models.Model):
    """
    Asociación explícita entre un videojuego y un género del catálogo.

    Regla de negocio: un videojuego puede tener varios géneros y un género
    agrupa varios videojuegos, pero la pareja (videojuego, género) no puede
    repetirse. La base de datos lo garantiza con un UniqueConstraint.
    """

    videojuego = models.ForeignKey(
        Videojuego, on_delete=models.CASCADE, related_name="vinculos_genero"
    )
    genero = models.ForeignKey(
        Genero, on_delete=models.PROTECT, related_name="vinculos_videojuego"
    )

    class Meta:
        verbose_name = "Género del videojuego"
        verbose_name_plural = "Géneros del videojuego"
        constraints = [
            models.UniqueConstraint(
                fields=["videojuego", "genero"],
                name="catalogo_videojuegogenero_videojuego_genero_unicos",
            ),
        ]
        indexes = [
            # Listado de videojuegos por género (consulta inversa del M2M).
            models.Index(
                fields=["genero", "videojuego"],
                name="catalogo_vjg_genero_idx",
            ),
        ]

    def __str__(self):
        return f"{self.videojuego.titulo} · {self.genero.nombre}"


class OfertaVideojuegoQuerySet(models.QuerySet):
    """Consultas de dominio sobre el catálogo comercial."""

    def publicadas(self):
        """Ofertas visibles en la tienda (estado de publicación = publicado)."""
        return self.filter(
            estado_publicacion=OfertaVideojuego.EstadoPublicacion.PUBLICADO
        )

    def vendibles(self):
        """Ofertas publicadas, de títulos activos y con stock disponible."""
        return self.publicadas().filter(stock__gt=0, videojuego__activo=True)


class OfertaVideojuego(models.Model):
    """
    Unidad comercial vendible: la combinación videojuego + plataforma.

    Concentra los atributos que dependen de la edición/plataforma:
    precio vigente, SKU, estado de publicación y stock (residencia
    provisional del inventario hasta AZ-S1-14).
    """

    class EstadoPublicacion(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        PUBLICADO = "publicado", "Publicado"
        RETIRADO = "retirado", "Retirado"

    videojuego = models.ForeignKey(
        Videojuego, on_delete=models.PROTECT, related_name="ofertas"
    )
    plataforma = models.ForeignKey(
        Plataforma, on_delete=models.PROTECT, related_name="ofertas"
    )
    precio_vigente = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.PositiveIntegerField(default=0)
    estado_publicacion = models.CharField(
        max_length=20,
        choices=EstadoPublicacion.choices,
        default=EstadoPublicacion.PUBLICADO,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    objects = OfertaVideojuegoQuerySet.as_manager()

    class Meta:
        verbose_name = "Oferta de videojuego"
        verbose_name_plural = "Ofertas de videojuegos"
        ordering = ["videojuego__titulo", "plataforma__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["videojuego", "plataforma"],
                name="%(app_label)s_%(class)s_videojuego_plataforma_unicos",
            ),
            models.CheckConstraint(
                condition=models.Q(precio_vigente__gte=0),
                name="%(app_label)s_%(class)s_precio_vigente_no_negativo",
            ),
        ]
        indexes = [
            # Storefront: ofertas publicadas con stock disponible. Sustituye
            # al índice de una sola columna, que exigía leer la tabla para
            # resolver el filtro de stock.
            models.Index(
                fields=["estado_publicacion", "stock"],
                name="catalogo_oferta_est_stock_idx",
            ),
            # Catálogo por plataforma: ofertas publicadas de cada plataforma.
            models.Index(
                fields=["plataforma", "estado_publicacion"],
                name="catalogo_oferta_plat_est_idx",
            ),
        ]

    def __str__(self):
        return f"{self.videojuego.titulo} — {self.plataforma.nombre} [{self.sku}]"

    @property
    def esta_publicada(self) -> bool:
        return self.estado_publicacion == self.EstadoPublicacion.PUBLICADO

    @property
    def disponible(self) -> bool:
        """La oferta es vendible: está publicada y tiene stock."""
        return self.esta_publicada and self.stock > 0
