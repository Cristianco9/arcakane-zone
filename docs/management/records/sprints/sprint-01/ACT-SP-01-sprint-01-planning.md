# Acta de Planificación del Sprint 1

**Código:** ACT-SP-001  
**Proyecto:** Arcakane Zone  
**Sprint:** 1  
**Fecha prevista:** 2026-11-02  
**Duración:** 2026-11-02 al 2026-11-16  
**Scrum Master:** Cristian Camilo Cortés Ortiz  
**Project Owner:** Miguel Ángel Herrera Luján  
**Repositorio:** `https://github.com/miguel-lujan2032/arcakane-zone.git`  
**GitHub Project:** `https://github.com/users/Cristianco9/projects/2`

## 1. Objetivo del Sprint

**Sprint Goal:**  
Documentar el estado actual del proyecto, normalizar la base de datos para eliminar 
redundancias y mejorar la integridad, endurecer la seguridad y la autorización, 
y asegurar la integridad y concurrencia del carrito y los pagos. Al finalizar, 
el sistema debe contar con una base de datos normalizada, pruebas automatizadas 
para los flujos críticos, y un entorno reproducible con Docker Compose.

## 2. Elementos seleccionados del Product Backlog

| ID | Historia / elemento | Origen (issue) | Prioridad | SP |
|---|---|---|---|---|
| US-101 | Como equipo, queremos documentar el contexto de negocio, actores, funcionalidades, modelo de dominio y arquitectura, para tener una base común de entendimiento. | AZ-S1-01, AZ-S1-02, AZ-S1-03, AZ-S1-04, AZ-S1-05, AZ-S1-06 | Alta | 5 |
| US-102 | Como administrador, quiero que las vistas administrativas y de reportes estén protegidas por roles y permisos unificados, para evitar accesos no autorizados. | AZ-S1-09, AZ-S1-12 | Alta | 3 |
| US-103 | Como usuario, quiero que el carrito y los pagos sean íntegros y seguros, validando entradas, manejando errores HTTP y evitando condiciones de carrera. | AZ-S1-07, AZ-S1-08, AZ-S1-10 | Alta | 5 |
| US-104 | Como equipo, queremos normalizar el catálogo comercial (categorías y géneros M2M, eliminación de enumerados, integridad referencial, roles y permisos) para mejorar la calidad de los datos. | AZ-S1-13, AZ-S1-15, AZ-S1-16, AZ-S1-17, AZ-S1-18 | Alta | 8 |
| US-105 | Como administrador, quiero un libro mayor de movimientos de inventario para auditar entradas y salidas de stock. | AZ-S1-14 | Media | 3 |
| US-106 | Como equipo, queremos completar las dependencias de testing y automatizar las validaciones en CI, para asegurar la calidad del código. | AZ-S1-11 | Alta | 3 |
| US-107 | Como equipo, queremos containerizar la aplicación con Docker Compose, para garantizar un entorno reproducible. | AZ-S1-22 | Alta | 3 |

**Total:** 30 Story Points.

## 3. Descomposición de actividades

| ID | Actividad | Responsable | Estimación |
|---|---|---|---|
| TASK-101 | Redactar documento de contexto, actores y alcance (AZ-S1-01) | Kathe005 / Cristian | 2 h |
| TASK-102 | Inventariar funcionalidades y flujos de usuario (AZ-S1-02) | luisanorena25 | 2 h |
| TASK-103 | Documentar modelo de dominio y diagramas UML/ER (AZ-S1-03) | Kathe005 / Cristian | 10m |
| TASK-104 | Auditar arquitectura, configuración (AZ-S1-04) | Cristian / Kathe005 | 2 h |
| TASK-105 | Revisar pruebas, defectos y riesgos técnicos (AZ-S1-05) | luisanorena25 | 2 h |
| TASK-106 | Consolidar documentación y backlog del Sprint 2 (AZ-S1-06) | Cristian / Kathe005 | 1 h |
| TASK-107 | Validar entradas del carrito y manejo de errores HTTP (AZ-S1-07) | Cristian | 1 h |
| TASK-108 | Corregir ciclo de reintentos de pago e idempotencia (AZ-S1-08) | Cristian | 1 h |
| TASK-109 | Unificar autorización de roles y proteger vistas administrativas (AZ-S1-09) | Cristian | 1 h |
| TASK-110 | Garantizar integridad y concurrencia del carrito (AZ-S1-10) | Cristian | 1 h |
| TASK-111 | Completar dependencias de testing y CI (AZ-S1-11) | luisanorena25 | 1 h |
| TASK-112 | Endurecer configuración de seguridad para producción (AZ-S1-12) | Kathe005 | 1 h |
| TASK-113 | Normalizar catálogo comercial: videojuegos, plataformas y ofertas (AZ-S1-13) | Kathe005 | 2 h |
| TASK-114 | Diseñar libro mayor de movimientos de inventario (AZ-S1-14) | Kathe005 | 1 h |
| TASK-115 | Aplicar integridad referencial y restricciones SQL (AZ-S1-15) | Kathe005 | 1 h |
| TASK-116 | Normalizar categorías y géneros con M2M (AZ-S1-16) | Kathe005 | 1 h |
| TASK-117 | Eliminar enumerados y normalizar estados (AZ-S1-17) | Kathe005 | 1 h |
| TASK-118 | Normalizar asignación de roles y catálogo de permisos (AZ-S1-18) | Kathe005 | 1 h |
| TASK-119 | Containerizar con Docker Compose (AZ-S1-22) | Cristian | 1 h |

**Total estimado:** 23 horas.

## 4. Criterios de aceptación

**US-101**
- [ ] Existe un documento con el contexto de negocio, actores y alcance.
- [ ] Inventario de funcionalidades y flujos de usuario.
- [ ] Diagramas UML/ER del modelo de dominio.
- [ ] Informe de auditoría de arquitectura y despliegue.
- [ ] Informe de revisión de pruebas, defectos y riesgos.
- [ ] Documentación consolidada y backlog del Sprint 2.

**US-102**
- [ ] Todas las vistas de reportes y administración requieren `is_staff` o permiso equivalente.
- [ ] Pruebas que verifiquen que un usuario no autorizado recibe 302 o 403.
- [ ] Configuración de seguridad para producción (DEBUG=False, ALLOWED_HOSTS, CSRF, HSTS, cookies seguras).

**US-103**
- [ ] Validación de entradas en carrito y checkout.
- [ ] Manejo de errores HTTP (400, 404, 409) en endpoints del carrito.
- [ ] Pago idempotente: no se procesa dos veces el mismo pedido.
- [ ] Control de concurrencia con `select_for_update` en stock y pedidos.
- [ ] Pruebas de integración para los casos anteriores.

**US-104**
- [ ] Categorías y géneros con relación M2M con videojuegos.
- [ ] Eliminación de campos enumerados reemplazados por tablas catálogo.
- [ ] Restricciones de integridad referencial aplicadas en base de datos.
- [ ] Catálogo de permisos y asignación de roles normalizada.
- [ ] Migraciones y seeders actualizados.

**US-105**
- [ ] Modelo `MovimientoInventario` con tipo (entrada/salida), cantidad, fecha y referencia.
- [ ] Registro automático de movimientos al pagar un pedido y al ajustar stock manualmente.
- [ ] Pruebas de creación de movimientos.

**US-106**
- [ ] `pytest`, `pytest-django`, `coverage` en `requirements.txt`.
- [ ] Configuración de CI (GitHub Actions) que ejecute tests y lint.
- [ ] Cobertura mínima del 60% en módulos críticos.

**US-107**
- [ ] `Dockerfile` para la aplicación.
- [ ] `docker-compose.yml` con servicios web, db y volúmenes.
- [ ] README actualizado con instrucciones para levantar el entorno.

## 5. Definición de Terminado

- [ ] Cumple criterios de aceptación.
- [ ] `pytest` pasa sin errores.
- [ ] Pull Request revisado por otro integrante.
- [ ] Documentación actualizada.
- [ ] Issue movido a Done en GitHub Projects.

## 6. Plan de trabajo

| Fecha | Actividad |
|---|---|
| 2026-07-20 | Planificación y asignación de tareas |
| 2026-07-21 al 2026-07-24 | Documentación y análisis (US-101) |
| 2026-07-25 al 2026-07-28 | Normalización de base de datos (US-104) |
| 2026-07-28 al 2026-07-30 | Seguridad y autorización (US-102) |
| 2026-07-30 al 2026-08-01 | Integridad de carrito y pagos (US-103) |
| 2026-08-01 al 2026-08-02 | Libro mayor de inventario (US-105) |
| 2026-08-02 | Testing y CI (US-106) |
| 2026-08-03 | Dockerización (US-107) y Sprint Review |

## 7. Riesgos

| ID | Riesgo | Impacto | Acción |
|---|---|---|---|
| RISK-101 | La normalización de la base de datos puede romper funcionalidades existentes. | Alto | Ejecutar pruebas después de cada migración y mantener respaldos. |
| RISK-102 | Falta de experiencia del equipo en Docker. | Medio | Pair programming y documentación oficial. |
| RISK-103 | La idempotencia en pagos requiere pruebas con concurrencia. | Alto | Implementar con transacciones y pruebas con hilos. |
| RISK-104 | El tiempo del sprint es limitado para 30 SP. | Medio | Priorizar US-101, US-102, US-103 y US-104; US-105 y US-107 pueden moverse. |

## 8. Acuerdos

- Una rama por issue (`feature/AZ-S1-XX`).
- PR revisado por otro integrante.
- Actualizar el tablero al mover cada issue.
- Consultar al Project Owner antes de agregar alcance.

## 9. Aprobación

| Participante | Rol | Fecha |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | 2026-11-03 |
| Cristian Camilo Cortés Ortiz | Scrum Master | 2026-11-03 |
| Kathe005 | Developer | 2026-11-03 |
| luisanorena25 | Developer | 2026-11-03 |
| Juan José Pérez Arana | Developer | YYYY-MM-DD |