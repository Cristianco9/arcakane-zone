"""Sustituye las URLs genéricas por portadas reales guardadas en la SPA."""

from django.db import migrations


def aplicar_portadas_reales(apps, schema_editor):
    from catalogo.portadas import url_portada_videojuego

    Videojuego = apps.get_model("catalogo", "Videojuego")
    actualizados = []
    for videojuego in Videojuego.objects.only("id", "titulo", "imagen_url").iterator():
        url = url_portada_videojuego(videojuego.pk, videojuego.titulo)
        if videojuego.imagen_url != url:
            videojuego.imagen_url = url
            actualizados.append(videojuego)
    if actualizados:
        Videojuego.objects.bulk_update(actualizados, ["imagen_url"], batch_size=500)


def no_op(apps, schema_editor):
    """No se restauran las URLs genéricas anteriores."""
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0015_videojuego_imagen_url'),
    ]

    operations = [
        migrations.RunPython(aplicar_portadas_reales, no_op),
    ]
