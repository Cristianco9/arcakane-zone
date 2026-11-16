# Diccionario de datos — modelo normalizado

**Issue:** #19 · AZ-S1-17 «Eliminar enumerados de dominio y normalizar estados mediante tablas catálogo» · **Alcance:** capa de datos.

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
- **Catálogos de estado (AZ-S1-17):** `codigo` es el identificador estable
  referenciado por las FKs (`to_field="codigo"`); `nombre` es la etiqueta
  visible y editable; `descripcion` es opcional.

## Resumen de tablas

| App | Tabla | Propósito |
|---|---|---|
| `cuentas` | `cuentas_rol` | Roles de acceso (cliente, administrador…). |
| `cuentas` | `cuentas_usuario` | Usuario autenticable (`AbstractUser` + datos de contacto). |
| `catalogo` | `catalogo_categoria` | Categoría del título (acción, deportes…). |
| `catalogo` | `catalogo_genero` | Género del título (RPG, shooter…). |
| `catalogo` | `catalogo_plataforma` | Plataforma de la oferta (PC, PS5…). |
| `catalogo` | `catalogo_videojuego` | Identidad e información común de un título. |
| `catalogo` | `catalogo_videojuegocategoria` | Tabla puente: categorías de un videojuego. |
| `catalogo` | `catalogo_videojuegogenero` | Tabla puente: géneros de un videojuego. |
| `catalogo` | `catalogo_estadopublicacion` | Catálogo de estados editoriales de una oferta. |
| `catalogo` | `catalogo_ofertavideojuego` | Unidad comercial vendible: videojuego + plataforma. |
| `pedidos` | `pedidos_estadopedido` | Catálogo de estados de un pedido. |
| `pedidos` | `pedidos_pedido` | Pedido (carrito o compra) de un cliente. |
| `pedidos` | `pedidos_detallepedido` | Línea del pedido con precio y snapshots congelados. |
| `pagos` | `pagos_estadointentopago` | Catálogo de estados de un intento de pago. |
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
| `activo` | boolean | no | `true` | — |
| `creado_en`, `actualizado_en` | timestamp | no | auto | — |

Las columnas `categoria_id` y `genero_id` **ya no existen**: la clasificación
se expresa con las tablas puente `catalogo_videojuegocategoria` y
`catalogo_videojuegogenero`. En el ORM se accede con los M2M
`Videojuego.categorias` y `Videojuego.generos` (con `through` explícito).

### `catalogo_videojuegocategoria`

Tabla puente explícita entre un título y una categoría del catálogo.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `videojuego_id` | bigint → `catalogo_videojuego` | no | — | `CASCADE` (el vínculo no sobrevive al título) |
| `categoria_id` | bigint → `catalogo_categoria` | no | — | `PROTECT` (categoría en uso no se borra) |

Restricciones e índices:

| Nombre | Tipo | Regla |
|---|---|---|
| `catalogo_videojuegocategoria_videojuego_categoria_unicos` | `UniqueConstraint` | La pareja `(videojuego, categoria)` no se repite. |
| `catalogo_vjc_categoria_idx` | índice `(categoria, videojuego)` | Listado de títulos por categoría. |
| `(videojuego, categoria)` | índice único implícito | Cubre el JOIN desde el videojuego hacia sus categorías. |

### `catalogo_videojuegogenero`

Tabla puente explícita entre un título y un género del catálogo.

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `videojuego_id` | bigint → `catalogo_videojuego` | no | — | `CASCADE` (el vínculo no sobrevive al título) |
| `genero_id` | bigint → `catalogo_genero` | no | — | `PROTECT` (género en uso no se borra) |

Restricciones e índices:

| Nombre | Tipo | Regla |
|---|---|---|
| `catalogo_videojuegogenero_videojuego_genero_unicos` | `UniqueConstraint` | La pareja `(videojuego, genero)` no se repite. |
| `catalogo_vjg_genero_idx` | índice `(genero, videojuego)` | Listado de títulos por género. |
| `(videojuego, genero)` | índice único implícito | Cubre el JOIN desde el videojuego hacia sus géneros. |

Un videojuego puede tener **cero, una o varias** categorías y géneros
(`blank=True`); no hay campos adicionales en las tablas puente porque la pareja
no tiene atributos propios de dominio.

### `catalogo_estadopublicacion`

Catálogo relacional de estados editoriales (AZ-S1-17).

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `codigo` | varchar(50) | no | — | **único**, identificador estable |
| `nombre` | varchar(100) | no | — | etiqueta visible editable |
| `descripcion` | text | no | `""` | — |

Constraint: `catalogo_estadopublicacion_codigo_unico` (`codigo` único).

Valores sembrados: `borrador` (Borrador), `publicado` (Publicado),
`retirado` (Retirado).

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
| `estado_publicacion` | varchar(50) → `catalogo_estadopublicacion.codigo` | no | `publicado` | FK `PROTECT`, `to_field="codigo"`, `db_index=False` |
| `creado_en`, `actualizado_en` | timestamp | no | auto | — |

Restricciones:

| Constraint | Regla |
|---|---|
| `catalogo_ofertavideojuego_videojuego_plataforma_unicos` | `(videojuego, plataforma)` único. |
| `catalogo_ofertavideojuego_precio_vigente_no_negativo` | `precio_vigente >= 0`. |
| `sku` (`unique=True`) | SKU interno único. |
| FK `estado_publicacion` | Solo códigos existentes en `catalogo_estadopublicacion`. |

Índices:

| Índice | Columnas | Uso |
|---|---|---|
| `catalogo_oferta_est_stock_idx` | `(estado_publicacion, stock)` | Storefront: publicadas con stock. |
| `catalogo_oferta_plat_est_idx` | `(plataforma, estado_publicacion)` | Catálogo por plataforma. |

---

## `pedidos`

### `pedidos_estadopedido`

Catálogo relacional de estados de pedido (AZ-S1-17).

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `codigo` | varchar(50) | no | — | **único**, identificador estable |
| `nombre` | varchar(100) | no | — | etiqueta visible editable |
| `descripcion` | text | no | `""` | — |

Constraint: `pedidos_estadopedido_codigo_unico` (`codigo` único).

Valores sembrados: `pendiente` (Pendiente), `pagado` (Pagado),
`cancelado` (Cancelado).

### `pedidos_pedido`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `cliente_id` | bigint → `cuentas_usuario` | no | — | `PROTECT` |
| `estado` | varchar(50) → `pedidos_estadopedido.codigo` | no | `pendiente` | FK `PROTECT`, `to_field="codigo"`, `db_index=False` |
| `creado_en` | timestamp | no | auto | — |
| `actualizado_en` | timestamp | no | auto | — |

Índice:

| Índice | Columnas | Uso |
|---|---|---|
| `pedidos_pedido_cli_fecha_idx` | `(cliente, -creado_en)` | Historial de compras del cliente, más reciente primero. |

> **Deuda técnica:** no existe una restricción que garantice un único pedido
> `pendiente` por cliente. `get_or_create_carrito()` mitiga el caso normal,
> pero dos peticiones concurrentes podrían crear dos carritos.

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

### `pagos_estadointentopago`

Catálogo relacional de estados de intento de pago (AZ-S1-17).

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `codigo` | varchar(50) | no | — | **único**, identificador estable |
| `nombre` | varchar(100) | no | — | etiqueta visible editable |
| `descripcion` | text | no | `""` | — |

Constraint: `pagos_estadointentopago_codigo_unico` (`codigo` único).

Valores sembrados: `aprobado` (Aprobado), `rechazado` (Rechazado),
`pendiente` (Pendiente).

### `pagos_pago`

| Campo | Tipo | Nulo | Default | Regla |
|---|---|---|---|---|
| `id` | bigint | no | auto | PK |
| `pedido_id` | bigint → `pedidos_pedido` | no | — | `PROTECT`, **único** (`OneToOne`) |
| `monto` | numeric(10,2) | no | — | `>= 0` |
| `estado` | varchar(50) → `pagos_estadointentopago.codigo` | no | `pendiente` | FK `PROTECT`, `to_field="codigo"`, `db_index=False` |
| `referencia` | varchar(100) | no | `""` | sin unicidad (deuda técnica) |
| `creado_en` | timestamp | no | auto | — |

Restricciones:

| Constraint | Regla |
|---|---|
| `pagos_pago_pedido_id_key` (`OneToOne`) | Un pedido tiene como máximo un pago. |
| `pagos_pago_monto_no_negativo` | `monto >= 0`. |
| FK `estado` | Solo códigos existentes en `pagos_estadointentopago`. |

> **Deudas técnicas:**
> - `referencia` debería ser única cuando no está vacía (idempotencia de la
>   pasarela). Hoy puede repetirse o quedar vacía.
> - Al ser `pedido` un `OneToOne`, un pago rechazado ocupa la única fila y un
>   reintento de pago del mismo pedido chocaría con la unicidad.

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
| `naturaleza` | varchar(10) | no | — | `entrada`/`salida`/`ajuste` (`TextChoices`, sin `CheckConstraint`; decisión de alcance AZ-S1-17) |
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

## Estados y decisiones de alcance (AZ-S1-17)

Los estados de `Pedido`, `Pago` (intento de pago) y `OfertaVideojuego` se
normalizaron como catálogos relacionales con FKs por `to_field="codigo"` y
`PROTECT`. Las etiquetas (`nombre`) son editables sin alterar los datos
transaccionales; los códigos son estables. No se implementa lógica de transición
(ver `docs/adr_az-s1-17-estados-catalogo.md`).

**Excepción documentada:** `inventario_tipomovimientoinventario.naturaleza`
permanece como `TextChoices` (`entrada`/`salida`/`ajuste`) sin
`CheckConstraint`. Es un dominio cerrado que determina la aritmética del ledger
(AZ-S1-14); no se convierte ni se duplica.

Consecuencia actual de `naturaleza`: un `UPDATE` directo por SQL puede escribir
un valor fuera del dominio. La validación de `choices` solo ocurre en
formularios y en `full_clean()`, que el ORM no invoca automáticamente.

## Migraciones que materializan este esquema

| Migración | Contenido |
|---|---|
| `catalogo.0003_indices_catalogo` | Reemplaza `catalogo_oferta_estado_idx` por `catalogo_oferta_est_stock_idx`; agrega índices compuestos de catálogo. |
| `catalogo.0004_tablas_puente_categoria_genero` | Crea tablas puente M2M. Solo esquema. |
| `catalogo.0005_videojuego_categoria_genero_opcionales` | Relaja FKs directas a `NULL`. Solo esquema. |
| `catalogo.0006_copiar_asociaciones_catalogo` | Copia asociaciones a las tablas puente (idempotente). Solo datos. |
| `catalogo.0007_retirar_fks_categoria_genero` | Retira FKs directas y añade M2M. Solo esquema. |
| `pedidos.0003_integridad_detallepedido` | Índice de cliente/fecha; valida datos y agrega checks de `cantidad` y `precio_unitario`. |
| `pagos.0002_integridad_pagos` | Índice de ventas por fecha; valida datos y agrega checks de `monto` y `total`. |
| `pedidos.0004_estado_pedido` | Crea `pedidos_estadopedido`. Solo esquema. |
| `pedidos.0005_semilla_estados_pedido` | Siembra estados de pedido (idempotente). Solo datos. |
| `pedidos.0006_pedido_estado_fk` | Renombra `estado` a `estado_legacy`, lo relaja y agrega FK nullable. Solo esquema. |
| `pedidos.0007_copiar_estado_pedido` | Copia/valida estados de pedido a la FK; aborta con tabla/campo/valor/cantidad si hay desconocidos. Solo datos. |
| `pedidos.0008_pedido_estado_definitivo` | Elimina `estado_legacy` y deja la FK `NOT NULL` con default. Solo esquema. |
| `pagos.0003_estado_intento_pago` | Crea `pagos_estadointentopago`. Solo esquema. |
| `pagos.0004_semilla_estados_pago` | Siembra estados de intento de pago. Solo datos. |
| `pagos.0005_pago_estado_fk` | Prepara la FK de estado en pago. Solo esquema. |
| `pagos.0006_copiar_estado_pago` | Copia/valida estados de pago a la FK. Solo datos. |
| `pagos.0007_pago_estado_definitivo` | Consolida la FK de estado en pago. Solo esquema. |
| `catalogo.0008_estado_publicacion` | Crea `catalogo_estadopublicacion`. Solo esquema. |
| `catalogo.0009_semilla_estados_publicacion` | Siembra estados de publicación. Solo datos. |
| `catalogo.0010_oferta_estado_fk` | Retira índices de oferta, prepara la FK de publicación. Solo esquema. |
| `catalogo.0011_copiar_estado_publicacion` | Copia/valida estados de publicación a la FK. Solo datos. |
| `catalogo.0012_oferta_estado_definitivo` | Consolida la FK de publicación y recrea índices. Solo esquema. |

Las migraciones de datos no normalizan nada: si encuentran filas inválidas
abortan con un `RuntimeError` que indica tabla, campo y cantidad de filas
afectadas. El operador debe corregir los datos y reintentar. La validación se
ejecuta antes de agregar los `CheckConstraint`, de modo que nunca se aplica un
check sobre datos que lo violan.

`catalogo.0006_copiar_asociaciones_catalogo` es reversible con una limitación
documentada: la reversión restaura la asociación de **menor PK** y descarta las
adicionales. Si algún videojuego no tiene categoría o género, aborta con un
`RuntimeError` descriptivo.

Las migraciones de estados (AZ-S1-17) son reversibles con datos: la restauración
del valor al campo antiguo ocurre antes de volver a `NOT NULL`. Si hay códigos
nuevos usados que no existen en el esquema anterior, la reversión aborta con un
mensaje claro. El reverso de la siembra falla si hay filas que referencian los
catálogos (`PROTECT`).

## Deudas técnicas y brechas conocidas

1. **`Usuario.email` no es único** (`cuentas`, fuera de alcance). Un mismo
   correo puede asociarse a varias cuentas.
2. **`Pago.referencia` sin unicidad ni obligatoriedad.** No hay idempotencia a
   nivel de base de datos para la referencia de la pasarela.
3. **`Pago.pedido` es `OneToOne`.** Un pago rechazado bloquea estructuralmente
   un reintento de pago del mismo pedido.
4. **Múltiples pedidos `pendiente` por cliente.** No hay restricción parcial
   que garantice un único carrito activo.
5. **Stock vs. libro mayor.** `pagos.services` modifica `stock` sin registrar
   un movimiento de inventario.
6. **`naturaleza` sin `CheckConstraint`.** `TipoMovimientoInventario.naturaleza`
   sigue siendo `TextChoices` (decisión AZ-S1-17).
7. **Sin validación de transiciones.** Los catálogos de estado garantizan
   integridad referencial, no flujos de transición (ver ADR AZ-S1-17).
8. **`flush` y catálogos.** Tras un `flush`, los catálogos de estado quedan
   vacíos; `seed_catalogo` los repone de forma idempotente.
