# Acta de Planificación del Sprint

## 1. Información general

| Campo | Información |
|---|---|
| Código del documento | ACT-SP-002 |
| Proyecto | Arkane Zone |
| Sprint | Sprint 2 |
| Fecha | 2026-11-16 (prevista) |
| Hora de inicio | 21:00 |
| Hora de finalización | 22:00 |
| Duración del Sprint | 15 días (2026-11-16 al 2026-11-30) |
| Scrum Master | Cristian Camilo Cortés Ortiz |
| Project Owner | Miguel Ángel Herrera Luján |
| Repositorio | `https://github.com/miguel-lujan2032/arcakane-zone.git` |
| GitHub Project | `https://github.com/users/Cristianco9/projects/2` |

## 2. Objetivo de la reunión

Definir el objetivo del Sprint, seleccionar los elementos del Product Backlog que
serán abordados y establecer el plan de trabajo necesario para alcanzar los resultados esperados.

## 3. Participantes

| Nombre completo | Rol | Asistencia |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | Presente |
| Cristian Camilo Cortés Ortiz | Scrum Master | Presente |
| Katherine Arboleda Ocoro | Developer | Presente |
| Luisa Maria Noreña Rueda | Developer | Presente |
| Juan José Pérez Arana | Developer | Presente |

## 4. Objetivo del Sprint (Sprint Goal)

**Objetivo:**

Completar la auditoría del inventario mediante el libro mayor de movimientos,
garantizar la reproducibilidad del entorno con Docker Compose e iniciar la
modernización del frontend con Next.js + React + TypeScript, construyendo la
estructura visual global y los componentes reutilizables. Al finalizar, el sistema
debe tener un entorno reproducible, auditoría de inventario y un frontend moderno
en desarrollo integrado con la API existente.

## 5. Elementos seleccionados del Product Backlog

Las referencias AZ corresponden a los issues del GitHub Project del equipo.
Las historias continúan la numeración del Sprint 1 (ACT-SP-001).

| ID | Historia de usuario / Requerimiento | Prioridad | Story Points | Issue |
|---|---|---|---|---|
| US-201 | Como administrador, quiero un libro mayor de movimientos de inventario para auditar entradas y salidas de stock y conocer la trazabilidad de cada cambio. | Alta | 3 | AZ-S1-14 |
| US-202 | Como equipo, quiero containerizar la aplicación (Django + PostgreSQL) con Docker Compose para garantizar un entorno reproducible en cualquier máquina. | Alta | 3 | AZ-S1-22 |
| US-203 | Como equipo, quiero inicializar la aplicación React.js con TypeScript en `frontend/`, configurando Tailwind CSS, ESLint y la estructura de carpetas, para iniciar la migración del frontend. | Alta | 8 | AZ-S2-01 |
| US-204 | Como equipo, quiero construir la estructura visual global (layout, navbar, footer) y los componentes reutilizables (tarjetas, botones, inputs, tablas) para reutilizarlos en todas las vistas migradas. | Alta | 5 | AZ-S2-02 |

**Total de Story Points seleccionados:** 19

## 6. Descomposición de actividades

La asignación de responsables la define el equipo junto con el Scrum Master durante el Sprint.

| ID | Actividad | Responsable | Issue relacionado | Estimación |
|---|---|---|---|---|
| TASK-201 | Diseñar el modelo `MovimientoInventario` con tipo (entrada/salida), cantidad, fecha, referencia y usuario; crear la migración correspondiente (US-201). | Katherine Arboleda Ocoro | AZ-S1-14 | 4 h |
| TASK-202 | Integrar el registro automático de movimientos al procesar un pago y al ajustar stock manualmente desde el admin (US-201). | Katherine Arboleda Ocoro | AZ-S1-14 | 3 h |
| TASK-203 | Escribir pruebas unitarias e integración del libro mayor: creación, consulta por juego y trazabilidad de un pedido (US-201). | Luisa Maria Noreña Rueda | AZ-S1-14 | 2 h |
| TASK-204 | Crear `Dockerfile` multi-etapa para la aplicación Django con Gunicorn y WhiteNoise (US-202). | Cristian Camilo Cortés Ortiz | AZ-S1-22 | 3 h |
| TASK-205 | Crear `docker-compose.yml` con servicios `web` y `db`, volúmenes persistentes, red personalizada y variables de entorno (US-202). | Cristian Camilo Cortés Ortiz | AZ-S1-22 | 3 h |
| TASK-206 | Actualizar README con instrucciones para levantar el proyecto con `docker-compose up` y ejecutar migraciones y seeders (US-202). | Cristian Camilo Cortés Ortiz | AZ-S1-22 | 2 h |
| TASK-207 | Inicializar el proyecto Next.js con TypeScript en `frontend/` usando `create-next-app` (US-203). | Luisa Maria Noreña Rueda | AZ-S2-01 | 4 h |
| TASK-208 | Configurar Tailwind CSS, ESLint, Prettier y estructura de carpetas (`components`, `app`/`pages`, `lib`, `styles`) (US-203). | Luisa Maria Noreña Rueda | AZ-S2-01 | 3 h |
| TASK-209 | Configurar variables de entorno y capa de acceso a la API de Django (fetch/axios) con manejo de errores (US-203). | Luisa Maria Noreña Rueda | AZ-S2-01 | 4 h |
| TASK-210 | Crear el layout global, navbar y footer en React, replicando la paleta azul de Arkane Zone (US-204). | Juan José Pérez Arana | AZ-S2-02 | 5 h |
| TASK-211 | Crear componentes reutilizables: `VideojuegoCard`, `Button`, `Input`, `Table`, `Badge` con TypeScript y props tipadas (US-204). | Juan José Pérez Arana | AZ-S2-02 | 6 h |
| TASK-212 | Configurar Jest + Testing Library y escribir pruebas de los componentes reutilizables (US-204). | Juan José Pérez Arana | AZ-S2-02 | 3 h |
| TASK-213 | Documentar el frontend en `frontend/README.md` y guía de contribución (US-204). | Cristian Camilo Cortés Ortiz | AZ-S2-02 | 2 h |
| TASK-214 | Preparar la demostración: levantar con Docker, mostrar el libro mayor en admin y la estructura del frontend Next.js. | Cristian Camilo Cortés Ortiz | — | 1 h |

**Total de horas estimadas:** 45 h

## 7. Criterios de aceptación

**US-201**

- [ ] El modelo `MovimientoInventario` contiene tipo (entrada/salida), cantidad, fecha, referencia al videojuego, referencia opcional al pedido y usuario responsable.
- [ ] Al procesar un pago aprobado se registra automáticamente un movimiento de salida por cada ítem del pedido.
- [ ] Al ajustar el stock manualmente desde el admin se registra un movimiento con el usuario que lo realizó.
- [ ] Existe al menos una prueba unitaria y una de integración para el libro mayor.
- [ ] El admin permite consultar los movimientos filtrados por videojuego y por fecha.

**US-202**

- [ ] El `Dockerfile` construye una imagen funcional de Django con Gunicorn y WhiteNoise.
- [ ] `docker-compose.yml` define los servicios `web` y `db` con volúmenes persistentes y red personalizada.
- [ ] La aplicación se levanta con `docker-compose up` desde una base vacía, ejecuta migraciones y seeders, y responde correctamente.
- [ ] El README documenta los pasos para levantar el entorno con Docker.

**US-203**

- [ ] Proyecto Next.js inicializado con TypeScript en `frontend/`.
- [ ] Tailwind CSS configurado con la paleta azul de Arkane Zone.
- [ ] ESLint y Prettier configurados y funcionando.
- [ ] Estructura de carpetas definida (`components`, `app`/`pages`, `lib`, `styles`).
- [ ] Variables de entorno configuradas y capa de API funcional contra Django.

**US-204**

- [ ] Layout global con navbar (según sesión) y footer.
- [ ] Componentes reutilizables tipados: `VideojuegoCard`, `Button`, `Input`, `Table`, `Badge`.
- [ ] Pruebas de componentes con Jest y Testing Library.
- [ ] Documentación del frontend en `frontend/README.md`.

**Criterio general del Sprint**

- [ ] El equipo demuestra: levantar el entorno con Docker, mostrar el libro mayor en el admin, y presentar la estructura del frontend React.js con los componentes visuales.

## 8. Definición de terminado (Definition of Done)

- [ ] La funcionalidad cumple los criterios de aceptación.
- [ ] El código cumple los estándares establecidos.
- [ ] Se realizaron las pruebas correspondientes.
- [ ] `pytest` (backend) y `npm test` (frontend) se ejecutan sin errores.
- [ ] El pipeline de CI pasa sin errores.
- [ ] La documentación fue actualizada cuando corresponde.
- [ ] Se creó el Pull Request correspondiente.
- [ ] El código fue revisado y aprobado.
- [ ] Los cambios fueron integrados según el flujo de trabajo establecido.

## 9. Plan de trabajo

| Actividad | Fecha de inicio | Fecha estimada de finalización | Responsable |
|---|---|---|---|
| Cierre de pendientes del Sprint 1 (si los hay) | 2026-08-04 | 2026-08-05 | Equipo de desarrollo |
| US-201: Libro mayor de inventario | 2026-08-05 | 2026-08-07 | Katherine Arboleda Ocoro / Luisa Maria Noreña Rueda |
| US-202: Docker Compose | 2026-08-06 | 2026-08-08 | Cristian Camilo Cortés Ortiz |
| US-203: Inicialización Next.js | 2026-08-09 | 2026-08-12 | Luisa Maria Noreña Rueda |
| US-204: Componentes visuales | 2026-08-11 | 2026-08-16 | Juan José Pérez Arana |
| Revisión de avance con el Project Owner | 2026-08-12 | 2026-08-12 | Scrum Master y Project Owner |
| Documentación y preparación de la demostración | 2026-08-16 | 2026-08-17 | Equipo de desarrollo |
| Sprint Review y Retrospectiva | 2026-08-18 | 2026-08-18 | Todo el equipo Scrum |

## 10. Riesgos, dependencias e impedimentos

| ID | Descripción | Impacto | Acción preventiva o correctiva | Responsable |
|---|---|---|---|---|
| RISK-201 | Pendientes del Sprint 1 sin cerrar (libro mayor y Docker) consumen capacidad de este Sprint. | Alto | Revisarlos al iniciar y cerrarlos primero; si ocupan más de dos días, el Project Owner decide mover US-204 al Sprint 3. | Cristian Camilo Cortés Ortiz |
| RISK-202 | La migración a Next.js requiere tiempo de aprendizaje del equipo. | Medio | Pair programming y documentación oficial; asignar a la persona con más experiencia en React. | Cristian Camilo Cortés Ortiz |
| RISK-203 | Docker Compose puede presentar problemas de red entre contenedores o de variables de entorno. | Medio | Configurar red personalizada, archivo `.env` documentado y pruebas de integración. | Cristian Camilo Cortés Ortiz |
| RISK-204 | La integración de la API de Django con el frontend puede presentar problemas de CORS o autenticación. | Medio | Configurar CORS correctamente y documentar la autenticación por sesión/cookie. | Luisa Maria Noreña Rueda |
| RISK-205 | La integración del libro mayor con pagos puede romper flujos existentes. | Alto | Pruebas de regresión sobre pagos y cancelaciones. | Katherine Arboleda Ocoro |
| DEP-001 | US-201 depende del modelo `Videojuego` y del servicio de pagos del Sprint 1. | Alto | Confirmar que el Sprint 1 está cerrado y que los tests de pagos pasan. | Cristian Camilo Cortés Ortiz |
| DEP-002 | US-204 depende de US-203 (estructura de Next.js y Tailwind). | Medio | Priorizar US-203 en la primera mitad del Sprint. | Luisa Maria Noreña Rueda |

## 11. Acuerdos y compromisos

| ID | Acuerdo o compromiso | Responsable | Fecha límite |
|---|---|---|---|
| AC-001 | Revisar el resultado del Sprint 1 al inicio de este Sprint y priorizar el cierre de sus pendientes. | Cristian Camilo Cortés Ortiz | 2026-08-04 |
| AC-002 | Crear en el GitHub Project los issues de las historias y tareas del Sprint 2, con su ID y sus Story Points. | Cristian Camilo Cortés Ortiz | 2026-08-04 |
| AC-003 | Implementar el libro mayor de inventario con integración automática en pagos y ajustes de stock. | Katherine Arboleda Ocoro | 2026-08-07 |
| AC-004 | Documentar la configuración de CORS y autenticación para futuras integraciones frontend-backend. | Luisa Maria Noreña Rueda | 2026-08-16 |
| AC-005 | Realizar una revisión de avance con el Project Owner a mitad del Sprint. | Cristian Camilo Cortés Ortiz | 2026-08-12 |

## 12. Evidencias y referencias

- Repositorio: https://github.com/miguel-lujan2032/arcakane-zone.git
- GitHub Project: https://github.com/users/Cristianco9/projects/2
- Product Backlog: GitHub Project del equipo (https://github.com/users/Cristianco9/projects/2)
- Issues seleccionados: AZ-S1-14, AZ-S1-22, AZ-S2-01, AZ-S2-02
- Documentación relacionada: `README.md`, `pytest.ini`, `requirements.txt`, `settings.py` y ACT-SP-001

## 13. Observaciones

- Este Sprint se dimensiona para unos 19 Story Points, equivalentes a unas 11 horas por desarrollador durante las dos semanas de trabajo.
- El libro mayor de inventario es el pendiente del Sprint 1 que se cierra en este Sprint, junto con la containerización con Docker Compose.
- La migración completa del frontend a Next.js continuará en el Sprint 3; en este Sprint solo se entrega la estructura inicial y los componentes reutilizables.
- La búsqueda avanzada y la paginación del catálogo (REQ-F-013) no forman parte de este Sprint y son una meta opcional del Sprint 4.
- Los campos marcados como «Por definir» o «Por confirmar» (hora, asistencia, responsables de las tareas e issues) se completan con la información real de la reunión antes de la aprobación del acta.

## 14. Aprobación y validación

| Participante | Rol | Usuario de GitHub | Fecha |
|---|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | miguel-lujan2032 | 2026-12-28 |
| Cristian Camilo Cortés Ortiz | Scrum Master | @Cristianco9 | 2026-12-28 |
| Katherine Arboleda Ocoro | Developer | Kathe005 | 2026-12-28 |
| Luisa Maria Noreña Rueda | Developer | luisanorena25 | 2026-12-28 |
| Juan José Pérez Arana | Developer | juanperezarana | 2026-12-28 |

### Estado de la planificación

- [ ] Objetivo del Sprint definido.
- [ ] Elementos del Product Backlog seleccionados.
- [ ] Criterios de aceptación revisados.
- [ ] Plan de trabajo establecido.
- [ ] Compromisos registrados.

**Evidencia de aprobación:** [URL del Pull Request o discusión correspondiente]