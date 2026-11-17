# Acta de Planificación del Sprint 2

**Código:** ACT-SP-002  
**Proyecto:** Arcakane Zone  
**Sprint:** 2  
**Fecha prevista:** 2026-11-16  
**Duración:** 2026-11-16 al 2026-11-30  
**Scrum Master:** Cristian Camilo Cortés Ortiz  
**Project Owner:** Miguel Ángel Herrera Luján  
**Repositorio:** `https://github.com/Cristianco9/arcakane-zone`  
**GitHub Project:** `https://github.com/users/Cristianco9/projects/3/`  
**Acta de requerimientos:** ACT-MIN-002

## 1. Objetivo del Sprint

**Sprint Goal:**  
Integrar la normalización de la base de datos en `main` y fortalecer el backend 
con inventario auditable por API, autorización por roles, pagos sin doble cobro 
e integración continua; y, en paralelo, construir la base del frontend en React + 
TypeScript con las diez primeras interfaces de los wireframes (Home, Catálogo, 
Detalle, Registro, Inicio de sesión, Recuperar contraseña, Nueva contraseña, 
Perfil, Cambiar contraseña y Carrito), conectadas a la API real. Al finalizar, 
el sistema debe contar con un backend consistente y protegido por CI, y con un 
frontend navegable que permita explorar el catálogo, autenticarse, gestionar la 
cuenta y armar el carrito.

## 2. Elementos seleccionados del Product Backlog

Los issues usan el prefijo `AZ-S2-BE-NN` (backend) y `AZ-S2-FE-NN` (frontend). 
El detalle de cada uno está en `sprint-2-backend-backlog.md` y `sprint-2-frontend-backlog.md`.

### 2.1. Compromiso del Sprint (prioridad Alta)

| ID | Historia / elemento | Origen (issue) | Prioridad | SP |
|---|---|---|---|---|
| US-201 | Como equipo, queremos integrar a `main` la normalización de la base de datos y adaptar la API al nuevo modelo, para trabajar sobre un esquema consistente sin romper el contrato actual. | AZ-S2-BE-01, AZ-S2-BE-02 | Alta | 10 |
| US-202 | Como administrador, quiero consultar y ajustar el inventario mediante un libro mayor de movimientos expuesto por API, para auditar cada cambio de stock. | AZ-S2-BE-03 | Alta | 5 |
| US-203 | Como administrador, quiero que cada endpoint valide el rol de negocio del usuario (administrador, gestor de inventario, soporte, cliente), para evitar accesos no autorizados. | AZ-S2-BE-07 | Alta | 5 |
| US-204 | Como cliente, quiero que un pago no pueda cobrarse dos veces aunque se repita la solicitud, para confiar en el proceso de compra. | AZ-S2-BE-10 | Alta | 5 |
| US-205 | Como equipo, queremos ejecutar pruebas, cobertura y lint automáticamente en cada Pull Request, para asegurar la calidad del código. | AZ-S2-BE-14 | Alta | 3 |
| US-206 | Como equipo, queremos una base de frontend con rutas, estructura visual global, cliente de API, sesión y componentes reutilizables, para construir todas las pantallas sobre los mismos cimientos. | AZ-S2-FE-00 | Alta | 5 |
| US-207 | Como visitante, quiero ver el Home, explorar el catálogo con filtros y paginación y consultar el detalle de un videojuego, para decidir mi compra. | AZ-S2-FE-01, AZ-S2-FE-02, AZ-S2-FE-03 | Alta | 13 |
| US-208 | Como visitante, quiero registrarme e iniciar sesión desde la interfaz, para comprar y consultar mis pedidos. | AZ-S2-FE-04, AZ-S2-FE-05 | Alta | 5 |
| US-209 | Como usuario, quiero editar mi perfil y cambiar mi contraseña, para mantener mis datos y mi cuenta seguros. | AZ-S2-FE-08, AZ-S2-FE-09 | Alta | 5 |
| US-210 | Como cliente, quiero ver y modificar mi carrito de compras, para revisar lo que voy a pagar antes de crear el pedido. | AZ-S2-FE-10 | Alta | 5 |

**Total comprometido:** 61 Story Points.

### 2.2. Según capacidad del equipo (prioridad Media)

| ID | Historia / elemento | Origen (issue) | Prioridad | SP |
|---|---|---|---|---|
| US-211 | Como usuario, quiero que mi cuenta esté protegida con límite de intentos, tokens con vencimiento y recuperación de contraseña por API. | AZ-S2-BE-04, AZ-S2-BE-05, AZ-S2-BE-06 | Media | 8 |
| US-212 | Como equipo, queremos endurecer la configuración de producción y contar con registro de eventos y verificación de salud con base de datos. | AZ-S2-BE-09 | Media | 3 |
| US-213 | Como cliente, quiero que el precio y la disponibilidad se revaliden antes de pagar, para no comprar con datos desactualizados. | AZ-S2-BE-11 | Media | 3 |
| US-214 | Como usuario, quiero recuperar mi contraseña desde la interfaz (solicitud y nueva contraseña). | AZ-S2-FE-06, AZ-S2-FE-07 | Media | 4 |

**Subtotal:** 18 Story Points.

### 2.3. Reserva (prioridad Deseable)

| ID | Historia / elemento | Origen (issue) | Prioridad | SP |
|---|---|---|---|---|
| US-215 | Como equipo, queremos gestión de usuarios y roles por API, pasarela de pago abstraída, ciclo de vida del pedido y documentación OpenAPI. | AZ-S2-BE-08, AZ-S2-BE-12, AZ-S2-BE-13, AZ-S2-BE-15 | Deseable | 16 |

**Total del backlog del Sprint:** 95 Story Points (61 comprometidos + 18 según capacidad + 16 de reserva).

## 3. Descomposición de actividades

Las estimaciones y responsables son la propuesta inicial del equipo; se confirman durante la reunión de planificación.

### 3.1. Backend

| ID | Actividad | Responsable | Estimación |
|---|---|---|---|
| TASK-201 | Integrar a `main` la cadena de ramas de normalización (AZ-S2-BE-01) | Katherine / Cristian | 10 h |
| TASK-202 | Adaptar la API REST v1 y los servicios al modelo normalizado (AZ-S2-BE-02) | Katherine | 10 h |
| TASK-203 | Exponer el libro mayor de inventario por API (AZ-S2-BE-03) | Katherine | 10 h |
| TASK-204 | Implementar RBAC granular y la matriz rol × endpoint (AZ-S2-BE-07) | Cristian | 10 h |
| TASK-205 | Pagos: concurrencia e idempotencia con pruebas de hilos (AZ-S2-BE-10) | Cristian | 10 h |
| TASK-206 | Configurar CI con GitHub Actions, cobertura y lint (AZ-S2-BE-14) | Cristian | 6 h |
| TASK-207 | Throttling y protección contra fuerza bruta (AZ-S2-BE-04) | Por asignar | 4 h |
| TASK-208 | Tokens de API con vencimiento y cierre de sesión global (AZ-S2-BE-05) | Por asignar | 6 h |
| TASK-209 | Recuperación de contraseña por API (AZ-S2-BE-06) | Por asignar | 6 h |
| TASK-210 | Endurecer configuración de producción y observabilidad (AZ-S2-BE-09) | Por asignar | 6 h |
| TASK-211 | Revalidar precio y disponibilidad en carrito y checkout (AZ-S2-BE-11) | Por asignar | 6 h |
| TASK-212 | Gestión de usuarios y roles por API (AZ-S2-BE-08) — reserva | Por asignar | 6 h |
| TASK-213 | Abstraer la pasarela de pago y webhook (AZ-S2-BE-12) — reserva | Por asignar | 10 h |
| TASK-214 | Ciclo de vida del pedido e historial de estados (AZ-S2-BE-13) — reserva | Por asignar | 10 h |
| TASK-215 | Documentación OpenAPI y colección de pruebas (AZ-S2-BE-15) — reserva | Por asignar | 6 h |

**Subtotal backend:** 116 h.

### 3.2. Frontend

| ID | Actividad | Responsable | Estimación |
|---|---|---|---|
| TASK-216 | Base del frontend: rutas, layout, cliente de API, sesión, componentes y Vitest (AZ-S2-FE-00) | Luisa | 10 h |
| TASK-217 | Interfaz Home — WF-01 (AZ-S2-FE-01) | Luisa | 6 h |
| TASK-218 | Interfaz Catálogo — WF-02 (AZ-S2-FE-02) | Juan José | 10 h |
| TASK-219 | Interfaz Detalle del videojuego — WF-03 (AZ-S2-FE-03) | Juan José | 10 h |
| TASK-220 | Interfaz Registro — WF-04 (AZ-S2-FE-04) | Juan José | 6 h |
| TASK-221 | Interfaz Inicio de sesión — WF-05 (AZ-S2-FE-05) | Juan José | 4 h |
| TASK-222 | Interfaz Recuperar contraseña — WF-06 (AZ-S2-FE-06) | Luisa | 4 h |
| TASK-223 | Interfaz Nueva contraseña — WF-07 (AZ-S2-FE-07) | Luisa | 4 h |
| TASK-224 | Interfaz Perfil de usuario — WF-08 (AZ-S2-FE-08) | Luisa | 6 h |
| TASK-225 | Interfaz Cambiar contraseña — WF-09 (AZ-S2-FE-09) | Luisa | 4 h |
| TASK-226 | Interfaz Carrito de compras — WF-10 (AZ-S2-FE-10) | Luisa / Juan José | 10 h |

**Subtotal frontend:** 74 h.

**Total estimado:** 190 horas (122 h del compromiso, 36 h según capacidad y 32 h de reserva).

## 4. Criterios de aceptación

**US-201**
- [ ] La cadena de normalización (AZ-S1-14 a AZ-S1-20) está en `main` mediante Pull Request revisado.
- [ ] `migrate` funciona desde una base vacía y desde una base con datos del esquema anterior; `makemigrations --check` no detecta cambios.
- [ ] Todos los endpoints de `docs/api/API.md` mantienen el sobre y los códigos HTTP; los cambios de contrato están documentados.
- [ ] Existe un documento con el procedimiento de migraciones y rollback.

**US-202**
- [ ] Endpoints de consulta de movimientos (con filtros y paginación) y de ajuste manual de stock.
- [ ] Cada cambio de stock (pago, cancelación, ajuste) genera exactamente un movimiento con el usuario responsable.
- [ ] Un ajuste no puede dejar el stock negativo (409).

**US-203**
- [ ] Clase de permiso reutilizable por rol aplicada a catálogo, inventario, soporte y reportes.
- [ ] Prueba parametrizada que recorre todas las rutas × rol × método y verifica 401/403/2xx.
- [ ] Matriz rol × endpoint publicada en `docs/api/API.md`.

**US-204**
- [ ] Dos pagos simultáneos del mismo pedido generan un único pago aprobado, una venta y un descuento de stock.
- [ ] Soporte de `Idempotency-Key`: repetir la clave no crea registros nuevos.
- [ ] Pruebas de concurrencia con hilos ejecutadas contra PostgreSQL.

**US-205**
- [ ] Workflow de GitHub Actions que ejecuta pruebas, cobertura, lint, `check --deploy` y `makemigrations --check`.
- [ ] Un Pull Request con una prueba rota o una migración pendiente falla en CI.
- [ ] Cobertura mínima acordada en módulos críticos y reporte como artefacto.

**US-206**
- [ ] Rutas para las diez pantallas y página 404, dentro del layout global (cabecera y pie según los wireframes).
- [ ] Cliente de API tipado para autenticación, catálogo y carrito, con manejo central de 401/403/409/429.
- [ ] Iniciar y cerrar sesión actualiza la cabecera y el contador del carrito.
- [ ] Vitest + Testing Library configurados; `npm run lint`, `build` y `test` pasan.

**US-207**
- [ ] Home, Catálogo y Detalle replican los wireframes WF-01, WF-02 y WF-03 en escritorio y móvil.
- [ ] El catálogo filtra, ordena y pagina contra la API, y refleja el estado en la URL.
- [ ] El detalle cambia precio y stock según la plataforma elegida; *Agregar al carrito* actualiza el contador.

**US-208**
- [ ] Registro e inicio de sesión replican WF-04 y WF-05 con validación y errores por campo devueltos por la API.
- [ ] Tras autenticarse, la sesión persiste y las rutas protegidas redirigen correctamente.

**US-209**
- [ ] Perfil y Cambiar contraseña replican WF-08 y WF-09; el perfil permite editar datos y cambiar la foto.
- [ ] La sesión continúa activa después de cambiar la contraseña.

**US-210**
- [ ] El carrito replica WF-10: líneas, cambio de cantidad, quitar ítem y resumen con totales de la API.
- [ ] Respeta el stock máximo y muestra los mensajes de conflicto del backend.

**US-211**
- [ ] Límite de intentos (429 con `Retry-After`), tokens con vencimiento y recuperación de contraseña con respuesta neutra.

**US-212**
- [ ] `check --deploy` sin advertencias, `LOGGING` por entorno y health check de preparación que consulta la base de datos.

**US-213**
- [ ] Cambios de precio y títulos inactivos se advierten o bloquean antes del pago, con detalle de ajustes.

**US-214**
- [ ] Pantallas WF-06 y WF-07 funcionando contra el backend (o con *mock* mientras US-211 no esté lista).

**US-215**
- [ ] Criterios definidos en cada issue de la reserva; solo se inician si el compromiso está cerrado.

## 5. Definición de Terminado

- [ ] Cumple criterios de aceptación.
- [ ] `pytest` (backend) y `npm test` (frontend) se ejecutan sin errores.
- [ ] El pipeline de CI pasa sin errores.
- [ ] Pull Request revisado por otro integrante.
- [ ] Probado manualmente contra el backend (Docker Compose).
- [ ] Documentación actualizada (`docs/api/API.md`, README).
- [ ] Issue movido a Done en GitHub Projects.

## 6. Plan de trabajo

| Fecha | Actividad |
|---|---|
| 2026-11-16 | Reunión con el Project Owner (ACT-MIN-002) y planificación |
| 2026-11-17 | Creación del milestone y los issues en GitHub Projects; asignación de responsables |
| 2026-11-17 al 2026-11-20 | Integración de la normalización (US-201), base del frontend (US-206), CI (US-205) y pagos (US-204); autenticación en frontend (US-208) |
| 2026-11-23 al 2026-11-27 | Libro mayor y roles (US-202, US-203), adaptación de la API (US-201), pantallas de exploración, cuenta y carrito (US-207, US-209, US-210) |
| 2026-11-24 | Revisión de avance con el Project Owner |
| 2026-11-25 al 2026-11-27 | Trabajo según capacidad: seguridad de autenticación, configuración de producción, revalidación del carrito y recuperación de contraseña (US-211 a US-214) |
| 2026-11-30 | Cierre de Pull Requests, Sprint Review y Retrospectiva |

## 7. Riesgos

| ID | Riesgo | Impacto | Acción |
|---|---|---|---|
| RISK-201 | El compromiso (61 SP, 122 h) supera lo completado en el Sprint 1 (27 SP). | Alto | Trabajar en el orden de prioridad, revisar el avance el 24-11 y mover al Sprint 3 lo que no entre, con aprobación del Project Owner. |
| RISK-202 | La integración de las ramas de normalización puede generar conflictos de migraciones con `main` y romper la API. | Alto | Probar sobre una copia de la base de datos, ejecutar la suite tras cada migración y documentar el rollback. |
| RISK-203 | Las pruebas de concurrencia de pagos son complejas y pueden requerir más tiempo. | Alto | Implementarlas desde el inicio con transacciones y hilos contra PostgreSQL; dejar el hallazgo documentado. |
| RISK-204 | El frontend depende del contrato de la API, que cambia con la adaptación al modelo normalizado. | Medio | Avisar los cambios de contrato en `docs/api/API.md` y usar *mocks* del cliente de API mientras tanto. |
| RISK-205 | Curva de aprendizaje de React + TypeScript (dificultad IMP-002 del Sprint 1). | Medio | Pair programming y construir primero la base y los componentes reutilizables. |
| RISK-206 | Las pantallas WF-06 y WF-07 dependen de la recuperación de contraseña por API (US-211). | Medio | Priorizar AZ-S2-BE-06 o trabajar con *mock* hasta que esté disponible. |

## 8. Acuerdos

- Una rama por issue (`feature/AZ-S2-BE-NN` o `feature/AZ-S2-FE-NN`).
- PR revisado por otro integrante y con CI en verde.
- Actualizar el tablero al mover cada issue.
- Consultar al Project Owner antes de agregar alcance.
- Documentar el proceso de migraciones y agregar pruebas de concurrencia al CI (acciones ACT-002 y ACT-003 de la retrospectiva del Sprint 1).

## 9. Aprobación

| Participante | Rol | Fecha |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | 2026-11-17 |
| Cristian Camilo Cortés Ortiz | Scrum Master | 2026-11-17 |
| Kathe005 | Developer | 2026-11-17 |
| luisanorena25 | Developer | 2026-11-17 |