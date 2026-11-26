"""Actualiza descripción y género con las fichas en español del fixture."""

from django.db import migrations


def backfill_fichas(apps, schema_editor):
    from catalogo.catalogo_real import juegos_reales

    Videojuego = apps.get_model("catalogo", "Videojuego")
    VideojuegoGenero = apps.get_model("catalogo", "VideojuegoGenero")
    Genero = apps.get_model("catalogo", "Genero")
    generos = {genero.nombre: genero.pk for genero in Genero.objects.all()}
    fichas = {juego["titulo"]: juego for juego in juegos_reales()}

    descripciones = []
    vinculos = []
    for videojuego in Videojuego.objects.only("id", "titulo", "descripcion").iterator():
        ficha = fichas.get(videojuego.titulo)
        if not ficha:
            continue
        if ficha["descripcion"] != videojuego.descripcion:
            videojuego.descripcion = ficha["descripcion"]
            descripciones.append(videojuego)

        genero_id = generos.get(ficha.get("genero"))
        if genero_id:
            actuales = set(
                VideojuegoGenero.objects.filter(
                    videojuego_id=videojuego.pk
                ).values_list("genero_id", flat=True)
            )
            if actuales != {genero_id}:
                vinculos.append((videojuego.pk, genero_id))

    if descripciones:
        Videojuego.objects.bulk_update(descripciones, ["descripcion"], batch_size=500)

    for videojuego_id, genero_id in vinculos:
        VideojuegoGenero.objects.filter(videojuego_id=videojuego_id).delete()
        VideojuegoGenero.objects.create(
            videojuego_id=videojuego_id, genero_id=genero_id
        )


def no_op(apps, schema_editor):
    """No se restauran las fichas anteriores."""
    return None


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0018_videojuego_desarrollador"),
    ]

    operations = [
        migrations.RunPython(backfill_fichas, no_op),
    ]
