from django.shortcuts import get_object_or_404, render

from .models import Categoria, Genero, Plataforma, Videojuego


def lista_videojuegos(request):
    videojuegos = Videojuego.objects.filter(activo=True).select_related(
        "categoria", "plataforma", "genero"
    )
    categorias = Categoria.objects.filter(activo=True)
    plataformas = Plataforma.objects.filter(activo=True)
    generos = Genero.objects.filter(activo=True)

    # Filtros opcionales
    categoria_id = request.GET.get("categoria")
    plataforma_id = request.GET.get("plataforma")
    genero_id = request.GET.get("genero")
    busqueda = request.GET.get("q", "").strip()

    if categoria_id:
        videojuegos = videojuegos.filter(categoria_id=categoria_id)
    if plataforma_id:
        videojuegos = videojuegos.filter(plataforma_id=plataforma_id)
    if genero_id:
        videojuegos = videojuegos.filter(genero_id=genero_id)
    if busqueda:
        videojuegos = videojuegos.filter(titulo__icontains=busqueda)

    contexto = {
        "videojuegos": videojuegos,
        "categorias": categorias,
        "plataformas": plataformas,
        "generos": generos,
    }
    return render(request, "catalogo/lista.html", contexto)


def detalle_videojuego(request, pk):
    videojuego = get_object_or_404(Videojuego, pk=pk, activo=True)
    return render(request, "catalogo/detalle.html", {"videojuego": videojuego})
