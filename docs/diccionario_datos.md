# Diccionario de datos — modelo normalizado

**Issue:** #17 · AZ-S1-15 «Aplicar integridad referencial y restricciones SQL
al modelo normalizado» · **Alcance:** capa de datos.

Este documento describe el esquema final del backend Django 5.2: tablas,
columnas, reglas de integridad, restricciones SQL e índices. Las restricciones
se implementan en la base de datos (no solo en formularios o servicios) y se
prueban provocando `IntegrityError` sin llamar a `full_clean()`.

Motor de desarrollo/producción: PostgreSQL. Motor de pruebas: SQLite en
memoria (`arkane_zone.settings_test`). Todas las restricciones documentadas se
verifican en ambos motores.

## Convenciones

- **PK:** `BigAutoField` (`bigint` autoincremental) salvo las tablas de Django.
- **FK:** `PROTECT` salvo que se indique otra política. Las referencias
  históricas nunca se borran en cascada.
- **`unique=True`:** índice único de una columna generado por Django.
- **Constraints nombrados explícitamente** para que el error de base de datos
  identifique la regla violada. Los nombres nuevos usan sufijos claros; los
  preexistentes conservan su nombre original.
- **Índices:** nombre explícito de hasta 30 caracteres (límite portable de
  Django).

## Resumen de tablas

| App | Tabla | Propósito |
|---|---|---|
| `cuentas` | `cuentas_rol` | Roles de acceso (cliente, administrador…). |
| `cuentas` | `cuentas_usuario` | Usuario autenticable (`AbstractUser` + datos de contacto). |
| `catalogo` | `catalogo_categoria` | Categoría del título (acción, deportes…). |
| `catalogo` | `catalogo_genero` | Género del título (RPG, shooter…). |
| `catalogo` | `catalogo_plataforma` | Plataforma de la oferta (PC, PS5…). |
| `catalogo` | `catalogo_videojuego` | Identidad e información común de un título. |
| `catalogo` | `catalogo_ofertavideojuego` | Unidad comercial vendible: videojuego + plataforma. |
| `pedidos` | `pedidos_pedido` | Pedido (carrito o compra) de un cliente. |
| `pedidos` | `pedidos_detallepedido` | Línea del pedido con precio y snapshots congelados. |
| `pagos` | `pagos_pago` | Intento de pago simulado de un pedido. |
| `pagos` | `pagos_venta` | Venta consolidada de un pedido aprobado. |
| `inventario` | `inventario_tipomovimientoinventario` | Catálogo de tipos de movimiento. |
| `inventario` | `inventario_motivomovimientoinventario` | Catálogo de motivos de movimiento. |
| `inventario` | `inventario_movimientoinventarioofertavideojuego` | Libro mayor inmutable de inventario. |
| `soporte` | `soporte_contacto` | Mensajes del formulario de contacto. |

---

## `cuentas`

### `cuentas_rol`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `nombre` | varchar(50) | no | — | **único** |
| `descripcion` | text | no | `""` | — |
| `activo` | boolean | no | `true` | — |

### `cuentas_usuario`

Hereda de `AbstractUser`. Se documentan los campos propios y los heredados
relevantes.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `username` | varchar(150) | no | — | único (Django) |
| `password` | varchar(128) | no | — | hash |
| `email` | varchar(254) | no | `""` | **no único** (deuda técnica) |
| `first_name`, `last_name` | varchar(150) | no | `""` | — |
| `is_staff`, `is_active`, `is_superuser` | boolean | no | según Django | — |
| `last_login`, `date_joined` | timestamp | sí / no | — / auto | — |
| `rol_id` | bigint → `cuentas_rol` | sí | `null` | `PROTECT` |
| `telefono` | varchar(20) | no | `""` | — |
| `direccion` | text | no | `""` | — |
| `foto` | varchar(100) | sí | `null` | ruta de archivo |

Relaciones heredadas: `groups` (M2M), `user_permissions` (M2M).

---

## `catalogo`

### `catalogo_categoria`, `catalogo_genero`, `catalogo_plataforma`

Las tres tablas comparten estructura:

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `nombre` | varchar(100) | no | — | **único** |
| `descripcion` | text | no | `""` | — |
| `activo` | boolean | no | `true` | — |

### `catalogo_videojuego`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `titulo` | varchar(200) | no | — | — |
| `descripcion` | text | no | `""` | — |
| `portada` | varchar(100) | sí | `null` | ruta de archivo |
| `fecha_lanzamiento` | date | sí | `null` | — |
| `categoria_id` | bigint → `catalogo_categoria` | no | — | `PROTECT` |
| `genero_id` | bigint → `catalogo_genero` | no | — | `PROTECT` |
| `activo` | boolean | no | `true` | — |
| `creado_en`, `actualizado_en` | timestamp | no | auto | — |

Índices:

| Índice | Columnas | Uso |
|---|---|---|
| `catalogo_vj_cat_activo_idx` | `(categoria, activo)` | Listado por categoría vigente. |
| `catalogo_vj_gen_activo_idx` | `(genero, activo)` | Listado por género vigente. |

### `catalogo_ofertavideojuego`

Unidad comercial vendible. Concentra precio, SKU, stock y publicación.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `videojuego_id` | bigint → `catalogo_videojuego` | no | — | `PROTECT` |
| `plataforma_id` | bigint → `catalogo_plataforma` | no | — | `PROTECT` |
| `precio_vigente` | numeric(10,2) | no | — | `>= 0` |
| `sku` | varchar(50) | no | — | **único** |
| `stock` | integer | no | `0` | `>= 0` (implícito de `PositiveIntegerField`) |
| `estado_publicacion` | varchar(20) | no | `publicado` | `borrador`/`publicado`/`retirado` (check de enum diferido) |
| `creado_en`, `actualizado_en` | timestamp | no | auto | — |

Restricciones:

| Constraint | Regla |
|---|---|
| `catalogo_ofertavideojuego_videojuego_plataforma_unicos` | `(videojuego, plataforma)` único. |
| `catalogo_ofertavideojuego_precio_vigente_no_negativo` | `precio_vigente >= 0`. |
| `sku` (`unique=True`) | SKU interno único. |

Índices:

| Índice | Columnas | Uso |
|---|---|---|
| `catalogo_oferta_est_stock_idx` | `(estado_publicacion, stock)` | Storefront: publicadas con stock. Sustituye al índice de una columna. |
| `catalogo_oferta_plat_est_idx` | `(plataforma, estado_publicacion)` | Catálogo por plataforma. |

---

## `pedidos`

### `pedidos_pedido`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `cliente_id` | bigint → `cuentas_usuario` | no | — | `PROTECT` |
| `estado` | varchar(20) | no | `pendiente` | `pendiente`/`pagado`/`cancelado` (check de enum diferido) |
| `creado_en` | timestamp | no | auto | — |
| `actualizado_en` | timestamp | no | auto | — |

Índice:

| Índice | Columnas | Uso |
|---|---|---|
| `pedidos_pedido_cli_fecha_idx` | `(cliente, -creado_en)` | Historial de compras del cliente, más reciente primero. |

> **Deuda técnica:** no existe una restricción que garantice un único pedido
> `pendiente` por cliente. `get_or_create_carrito()` mitiga el caso normal,
> pero dos peticiones concurrentes podrían crear dos carritos y luego
> provocar `MultipleObjectsReturned`. Se recomienda un `UniqueConstraint`
> parcial sobre `(cliente)` con `estado = 'pendiente'` (issue de carrito).

### `pedidos_detallepedido`

Línea histórica del pedido. Congela precio unitario y snapshots de título y
plataforma; no cambia si el catálogo se modifica después.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `pedido_id` | bigint → `pedidos_pedido` | no | — | `CASCADE` (el pedido es dueño de sus líneas) |
| `oferta_id` | bigint → `catalogo_ofertavideojuego` | no | — | `PROTECT` |
| `cantidad` | integer | no | `1` | `>= 1` |
| `precio_unitario` | numeric(10,2) | no | — | `>= 0` |
| `titulo_snapshot` | varchar(200) | no | — | congelado al crear |
| `plataforma_snapshot` | varchar(100) | no | — | congelado al crear |

Restricciones:

| Constraint | Regla |
|---|---|
| `pedidos_detallepedido_pedido_oferta_unicos` | `(pedido, oferta)` único: una sola línea por oferta en el pedido. |
| `pedidos_detallepedido_cantidad_positiva` | `cantidad >= 1`: no existen líneas de cantidad cero o negativa. |
| `pedidos_detallepedido_precio_unitario_no_negativo` | `precio_unitario >= 0`. |

---

## `pagos`

### `pagos_pago`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `pedido_id` | bigint → `pedidos_pedido` | no | — | `PROTECT`, **único** (`OneToOne`) |
| `monto` | numeric(10,2) | no | — | `>= 0` |
| `estado` | varchar(20) | no | `pendiente` | `aprobado`/`rechazado`/`pendiente` (check de enum diferido) |
| `referencia` | varchar(100) | no | `""` | sin unicidad (deuda técnica) |
| `creado_en` | timestamp | no | auto | — |

Restricciones:

| Constraint | Regla |
|---|---|
| `pagos_pago_pedido_id_key` (`OneToOne`) | Un pedido tiene como máximo un pago. |
| `pagos_pago_monto_no_negativo` | `monto >= 0`. |

> **Deudas técnicas:**
> - `referencia` debería ser única cuando no está vacía (idempotencia de la
>   pasarela). Hoy puede repetirse o quedar vacía.
> - Al ser `pedido` un `OneToOne`, un pago rechazado ocupa la única fila y un
>   reintento de pago del mismo pedido chocaría con la unicidad. El modelo de
>   reintentos requiere pasar a `ForeignKey` o reutilizar la fila existente
>   (issue de pagos).

### `pagos_venta`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `pedido_id` | bigint → `pedidos_pedido` | no | — | `PROTECT`, **único** (`OneToOne`) |
| `total` | numeric(10,2) | no | — | `>= 0` |
| `registrada_en` | timestamp | no | auto | — |

Restricciones e índices:

| Nombre | Tipo | Regla / uso |
|---|---|---|
| `pagos_venta_pedido_id_key` | unique (OneToOne) | Una venta por pedido. |
| `pagos_venta_total_no_negativo` | check | `total >= 0`. |
| `pagos_venta_registrada_idx` | index `(registrada_en)` | Reportes de ventas por fecha. |

---

## `inventario`

### `inventario_tipomovimientoinventario`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `codigo` | varchar(50) | no | — | **único** |
| `nombre` | varchar(100) | no | — | — |
| `descripcion` | text | no | `""` | — |
| `naturaleza` | varchar(10) | no | — | `entrada`/`salida`/`ajuste` (check de enum diferido) |
| `activo` | boolean | no | `true` | — |

Constraint: `inventario_tipomovimiento_codigo_unico` (`codigo` único).

### `inventario_motivomovimientoinventario`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `codigo` | varchar(50) | no | — | **único** |
| `nombre` | varchar(100) | no | — | — |
| `descripcion` | text | no | `""` | — |
| `activo` | boolean | no | `true` | — |

Constraint: `inventario_motivomovimiento_codigo_unico` (`codigo` único).

### `inventario_movimientoinventarioofertavideojuego`

Libro mayor inmutable (solo-apéndice) con saldos corridos congelados. Ver
`docs/adr_az-s1-14-libro-mayor-inventario.md`.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `oferta_id` | bigint → `catalogo_ofertavideojuego` | no | — | `PROTECT` |
| `tipo_movimiento_id` | bigint → `inventario_tipomovimientoinventario` | no | — | `PROTECT` |
| `motivo_id` | bigint → `inventario_motivomovimientoinventario` | sí | `null` | `PROTECT` |
| `observacion` | text | no | `""` | — |
| `cantidad` | integer | no | — | `> 0` |
| `unidad` | varchar(50) | no | `unidad` | — |
| `saldo_anterior` | integer | no | — | `>= 0` |
| `saldo_posterior` | integer | no | — | `>= 0` |
| `fecha_hora` | timestamp | no | `now` | no editable |
| `usuario_responsable_id` | bigint → `cuentas_usuario` | sí | `null` | `PROTECT` |
| `detalle_pedido_id` | bigint → `pedidos_detallepedido` | sí | `null` | `PROTECT`, único condicional |
| `clave_idempotencia` | varchar(200) | no | — | **único** |
| `movimiento_compensado_id` | bigint → self | sí | `null` | `PROTECT` |

Restricciones:

| Constraint | Regla |
|---|---|
| `inventario_movimiento_clave_idempotencia_unica` | `clave_idempotencia` única. |
| `inventario_movimiento_detalle_pedido_unico` | `detalle_pedido` único solo cuando no es `null`. |
| `inventario_movimiento_cantidad_positiva` | `cantidad > 0`. |
| `inventario_movimiento_saldo_anterior_no_negativo` | `saldo_anterior >= 0`. |
| `inventario_movimiento_saldo_posterior_no_negativo` | `saldo_posterior >= 0`. |

Índices:

| Índice | Columnas | Uso |
|---|---|---|
| `inventario_oferta_fecha_idx` | `(oferta, -fecha_hora)` | Historial de una oferta. |
| `inventario_mov_tipo_fecha_idx` | `(tipo_movimiento, -fecha_hora)` | Movimientos recientes por tipo. |

> **Riesgo de consistencia:** `catalogo_ofertavideojuego.stock` es un contador
> y el ledger es la fuente auditable. Hoy `pagos.services` descuenta `stock`
> sin escribir un movimiento. Mientras el servicio no escriba ambos en la
> misma transacción, el stock puede divergir del último `saldo_posterior`.
> La BD no puede imponer esa relación porque el signo depende de
> `tipo_movimiento.naturaleza`.

---

## `soporte`

### `soporte_contacto`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `nombre` | varchar(150) | no | — | — |
| `email` | varchar(254) | no | — | — |
| `telefono` | varchar(20) | no | `""` | — |
| `asunto` | varchar(200) | no | — | — |
| `mensaje` | text | no | `""` | — |
| `usuario_id` | bigint → `cuentas_usuario` | sí | `null` | `SET_NULL` |
| `creado_en` | timestamp | no | auto | — |
| `atendido` | boolean | no | `false` | — |

---

## Restricciones diferidas a AZ-S1-17

Los siguientes campos usan `TextChoices` en Python, pero **no** tienen
`CheckConstraint` de base de datos. Se dejan explícitamente fuera de este
issue para no duplicar el trabajo de AZ-S1-17 (enums):

- `pedidos_pedido.estado`
- `pagos_pago.estado`
- `catalogo_ofertavideojuego.estado_publicacion`
- `inventario_tipomovimientoinventario.naturaleza`

Consecuencia actual: un `UPDATE` directo por SQL puede escribir un valor fuera
del dominio. La validación de `choices` solo ocurre en formularios y en
`full_clean()`, que el ORM no invoca automáticamente.

## Migraciones que materializan este esquema

| Migración | Contenido |
|---|---|
| `catalogo.0003_indices_catalogo` | Reemplaza `catalogo_oferta_estado_idx` por `catalogo_oferta_est_stock_idx`; agrega `catalogo_oferta_plat_est_idx`, `catalogo_vj_cat_activo_idx`, `catalogo_vj_gen_activo_idx`. |
| `pedidos.0003_integridad_detallepedido` | Índice de cliente/fecha; **valida datos** y luego agrega los checks de `cantidad` y `precio_unitario`. |
| `pagos.0002_integridad_pagos` | Índice de ventas por fecha; **valida datos** y luego agrega los checks de `monto` y `total`. |

Las migraciones de datos no normalizan nada: si encuentran filas inválidas
abortan con un `RuntimeError` que indica tabla, campo y cantidad de filas
afectadas. El operador debe corregir los datos y reintentar. La validación se
ejecuta antes de agregar los `CheckConstraint`, de modo que nunca se aplica un
check sobre datos que lo violan.

## Deudas técnicas y brechas conocidas

1. **`Usuario.email` no es único** (`cuentas`, fuera de alcance). Un mismo
   correo puede asociarse a varias cuentas. Requiere limpieza previa y una
   restricción única en la app `cuentas`.
2. **`Pago.referencia` sin unicidad ni obligatoriedad.** No hay idempotencia
   a nivel de base de datos para la referencia de la pasarela.
3. **`Pago.pedido` es `OneToOne`.** Un pago rechazado bloquea estructuralmente
   un reintento de pago del mismo pedido.
4. **Múltiples pedidos `pendiente` por cliente.** No hay restricción parcial
   que garantice un único carrito activo.
5. **Stock vs. libro mayor.** `pagos.services` modifica `stock` sin registrar
   un movimiento de inventario; la conciliación queda pendiente del issue de
   servicios de inventario.
6. **Checks de enums diferidos a AZ-S1-17** (ver sección anterior).
