# Siembra idempotente de los roles de negocio añadidos en el RBAC (AZ-S2-BE-07).
# Solo datos: no cambia modelos ni esquema. La reversión aborta si algún rol
# tiene usuarios asignados para no dejar asignaciones huérfanas.
from django.db import migrations


ROLES_NUEVOS = (
    (
        "gestor_inventario",
        "Gestor de inventario",
        "Gestiona el catálogo y el libro mayor de inventario.",
    ),
    (
        "soporte",
        "Soporte",
        "Atiende y gestiona los mensajes de contacto.",
    ),
)


def poblar_roles_rbac(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    for codigo, nombre, descripcion in ROLES_NUEVOS:
        rol = Rol.objects.filter(codigo=codigo).first()
        if rol is None:
            Rol.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                activo=True,
            )
        else:
            # Idempotente: completa nombre/descripción sin borrar nada.
            cambios = []
            if rol.nombre != nombre:
                rol.nombre = nombre
                cambios.append("nombre")
            if rol.descripcion != descripcion:
                rol.descripcion = descripcion
                cambios.append("descripcion")
            if not rol.activo:
                rol.activo = True
                cambios.append("activo")
            if cambios:
                rol.save(update_fields=cambios)


def revertir_roles_rbac(apps, schema_editor):
    Rol = apps.get_model("cuentas", "Rol")
    UsuarioRol = apps.get_model("cuentas", "UsuarioRol")
    for codigo, nombre, _descripcion in ROLES_NUEVOS:
        rol = Rol.objects.filter(codigo=codigo).first()
        if rol is None:
            continue
        if UsuarioRol.objects.filter(rol=rol).exists():
            raise RuntimeError(
                "No se puede revertir la migración de roles RBAC: el rol "
                f"'{nombre}' (código '{codigo}') tiene usuarios asignados. "
                "Retira esas asignaciones antes de revertir."
            )
        rol.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cuentas", "0007_usuario_roles_m2m"),
    ]

    operations = [
        migrations.RunPython(poblar_roles_rbac, revertir_roles_rbac),
    ]
