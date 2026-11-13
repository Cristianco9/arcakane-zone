# Acta de Aceptación y Cierre del Proyecto

## 1. Información general

| Campo | Información |
|---|---|
| Código del documento | ACT-PA-001 |
| Nombre del proyecto | Arcakane Zone |
| Fecha de evaluación | 2026-12-28 (prevista) |
| Fecha de cierre | 2026-12-28 (prevista) |
| Project Owner | Miguel Ángel Herrera Luján |
| Scrum Master | Cristian Camilo Cortés Ortiz |
| Equipo de desarrollo | Katherine Arboleda Ocoro, Luisa Maria Noreña Rueda y Juan José Pérez Arana |
| Repositorio | `https://github.com/miguel-lujan2032/arcakane-zone.git` |
| GitHub Project | `https://github.com/users/Cristianco9/projects/2` |
| Versión entregada | v1.0.0 (prevista) |

## 2. Objetivo del documento

Registrar la evaluación final de los entregables del proyecto, verificar el
cumplimiento de los requerimientos establecidos y documentar la aceptación formal
de la solución desarrollada por parte del Project Owner.

Esta acta se prepara al inicio del proyecto con los criterios de aceptación
acordados con el equipo. Las columnas de estado, resultado y evidencia se completan
en la evaluación final; hasta entonces permanecen como «Pendiente» o «Por registrar».

## 3. Descripción general del proyecto

**Nombre del proyecto:**

Arcakane Zone.

**Descripción:**

Arcakane Zone es una aplicación web de comercio electrónico de videojuegos. Las
personas registradas pueden explorar un catálogo con filtros por categoría,
plataforma y género, ver el detalle de cada videojuego, agregar productos al
carrito, confirmar pedidos con pago simulado, consultar su historial y contactar
a soporte. Los usuarios con rol de staff disponen de reportes de ventas,
inventario y videojuegos.

La solución está construida sobre Django 5.2, PostgreSQL, Tailwind CSS (vía CDN),
HTMX y django-unfold para la administración. El frontend se está migrando a
Next.js + React + TypeScript. Incluye pruebas automatizadas con pytest,
containerización con Docker Compose y configuración de seguridad para producción
en Render.

**Objetivo general:**

Desarrollar una aplicación web de comercio electrónico de videojuegos que permita
a los usuarios registrarse, explorar el catálogo, gestionar un carrito, realizar
pedidos con pago simulado y consultar su historial, con control de acceso,
integridad de datos y validaciones en el servidor.

## 4. Alcance del proyecto

Describir las funcionalidades y componentes que fueron incluidos dentro del alcance aprobado.

- Registro, inicio y cierre de sesión, perfil propio y cambio de contraseña.
- Catálogo de videojuegos con filtros por categoría, plataforma y género, y búsqueda por título.
- Detalle de videojuego con información completa y disponibilidad de stock.
- Carrito con agregar, actualizar cantidades, eliminar y validación de stock.
- Checkout y pago simulado (aprobado/rechazado), con generación de venta y descuento de stock.
- Historial de pedidos del cliente y cancelación de pedidos pendientes.
- Panel de reportes para staff: dashboard, ventas, inventario y videojuegos.
- Soporte: contacto, mayor información y ayuda.
- Administración con django-unfold.
- Normalización de la base de datos (M2M, tablas catálogo, integridad referencial, roles y permisos).
- Libro mayor de movimientos de inventario.
- Pruebas automatizadas de los flujos principales.
- Entorno reproducible con Docker Compose.
- Migración del frontend React + TypeScript + TailwindCSS.

**Limitaciones conocidas:**

Las siguientes funcionalidades están fuera del alcance acordado y no se consideran
parte de la entrega, salvo aprobación expresa del Project Owner: integración de
pasarela de pago real, recuperación de contraseña por correo en producción,
almacenamiento externo de imágenes con CDN, pruebas de extremo a extremo en
navegador y aplicación móvil nativa.

Limitaciones técnicas previstas: el pago es simulado y no procesa transacciones
reales; la recuperación de contraseña solo funciona en modo desarrollo (consola);
las imágenes se almacenan en disco local o S3 sin CDN; y la migración del frontend
a React.js queda en un estado parcial al cierre del proyecto. Esta sección se
actualiza en la evaluación final con las limitaciones reales.

## 5. Evaluación de requerimientos

Verificar el cumplimiento de los requerimientos definidos y aprobados durante la
etapa inicial del proyecto.

**Criterio mínimo de aceptación:** el proyecto puede aceptarse cuando todos los
requerimientos marcados como Obligatorio están cumplidos y el equipo ejecuta sin
fallos, ante el Project Owner, el escenario manual de nueve pasos: registrar un
usuario e iniciar sesión; explorar el catálogo y aplicar filtros; abrir el detalle
de un videojuego; agregar productos al carrito y modificar cantidades; proceder al
checkout y pagar (simulado); consultar el historial de pedidos; cancelar un pedido
pendiente; acceder a los reportes como staff; y cerrar sesión comprobando que las
acciones restringidas exigen autenticación.

**Criterio de carga:** el alcance obligatorio se dimensionó para unos 10 Story
Points por semana de sprint, equivalentes a unas 13 horas semanales por desarrollador.
Los requerimientos Deseables no condicionan la aceptación.

| ID | Requerimiento | Estado | Evidencia |
|---|---|---|---|
| REQ-F-001 | Registro, inicio y cierre de sesión con contraseñas cifradas y sesión por cookie. Obligatorio. Sprint 1. | Pendiente | Por registrar |
| REQ-F-002 | Edición del perfil propio y cambio de contraseña. Obligatorio. Sprint 1. | Pendiente | Por registrar |
| REQ-F-003 | Catálogo de videojuegos con filtros por categoría, plataforma y género, y búsqueda por título. Obligatorio. Sprints 1 y 2. | Pendiente | Por registrar |
| REQ-F-004 | Detalle de videojuego con información completa y disponibilidad de stock. Obligatorio. Sprint 2. | Pendiente | Por registrar |
| REQ-F-005 | Carrito con agregar, actualizar cantidades, eliminar y validación de stock. Obligatorio. Sprints 1 y 2. | Pendiente | Por registrar |
| REQ-F-006 | Checkout y pago simulado con estados aprobado/rechazado, generación de venta y descuento de stock. Obligatorio. Sprints 1 y 2. | Pendiente | Por registrar |
| REQ-F-007 | Historial de pedidos del cliente y cancelación de pedidos pendientes. Obligatorio. Sprints 1 y 2. | Pendiente | Por registrar |
| REQ-F-008 | Panel de reportes para staff: dashboard, ventas, inventario y videojuegos. Obligatorio. Sprints 1 y 3. | Pendiente | Por registrar |
| REQ-F-009 | Soporte: contacto, mayor información y ayuda. Obligatorio. Sprint 3. | Pendiente | Por registrar |
| REQ-F-010 | Normalización de la base de datos (M2M, tablas catálogo, integridad referencial, roles y permisos). Obligatorio. Sprint 1. | Pendiente | Por registrar |
| REQ-F-011 | Libro mayor de movimientos de inventario. Obligatorio. Sprint 2. | Pendiente | Por registrar |
| REQ-F-012 | Seeders idempotentes de catálogo, roles y permisos. Obligatorio. Sprint 1. | Pendiente | Por registrar |
| REQ-F-013 | Búsqueda avanzada y paginación en el catálogo. Deseable: solo si el equipo termina antes el compromiso del Sprint 4. | Pendiente | Por registrar |
| REQ-NF-001 | Protección CSRF en los formularios que modifican datos. Obligatorio. Sprints 1 a 4. | Pendiente | Por registrar |
| REQ-NF-002 | Pruebas automatizadas con pytest de los flujos principales. Obligatorio. Sprints 1 a 4. | Pendiente | Por registrar |
| REQ-NF-003 | Validación de entradas con formularios de Django, manejo centralizado de errores e interfaz adaptable a escritorio y móvil. Obligatorio. Sprints 1 a 4. | Pendiente | Por registrar |
| REQ-NF-004 | Entorno reproducible con Docker Compose y documentación actualizada (README y HANDOFF). Obligatorio. Sprints 1 y 4. | Pendiente | Por registrar |
| REQ-NF-005 | Migración del frontend a Next.js + React + TypeScript. Obligatorio. Sprints 2, 3 y 4. | Pendiente | Por registrar |

## 6. Entregables finales

Registrar los productos, componentes y documentos entregados como resultado del desarrollo.

| ID | Entregable | Descripción | Evidencia |
|---|---|---|---|
| DEL-001 | Código fuente | Código fuente del sistema en la rama `main` del repositorio, con la etiqueta v1.0.0 | https://github.com/miguel-lujan2032/arcakane-zone.git |
| DEL-002 | Documentación técnica | README y HANDOFF actualizados al estado real, y el informe de verificación del repositorio del Sprint 1 | Por registrar |
| DEL-003 | Pruebas | Resultado de `pytest` y del pipeline de CI sin errores, registrado en el Pull Request final | Por registrar |
| DEL-004 | Aplicación funcional | Versión v1.0.0 del sistema, demostrada con el escenario manual de nueve pasos en la Sprint Review del Sprint 4 | Por registrar |
| DEL-005 | Actas del proyecto | Actas de reunión, de planificación de cada sprint y de aceptación y cierre | Por registrar |

## 7. Evaluación de calidad y validación

Registrar las verificaciones realizadas antes de aceptar el proyecto.

Cada fila indica el criterio de aprobación acordado; el resultado y las
observaciones se registran en la evaluación final.

| Aspecto evaluado | Resultado | Observaciones |
|---|---|---|
| Cumplimiento de requerimientos | Pendiente | Criterio de aprobación: todos los requerimientos obligatorios (REQ-F-001 a REQ-F-012 y REQ-NF-001 a REQ-NF-005) en estado Cumplido. Los deseables pueden quedar Parcial o No cumplido. |
| Funcionamiento de las funcionalidades principales | Pendiente | Criterio de aprobación: el escenario manual de nueve pasos se ejecuta sin fallos, ante el Project Owner, sobre una instalación limpia. |
| Pruebas funcionales | Pendiente | Criterio de aprobación: `pytest` pasa sin fallos y existe al menos una prueba de caso exitoso y una de caso de error por cada módulo: autenticación y perfil, catálogo, carrito, pagos, pedidos, reportes y soporte. |
| Calidad del código | Pendiente | Criterio de aprobación: sin errores de linting; sin secretos ni archivo `.env` versionados; una rama por issue con Pull Request revisado por otro integrante; validación con formularios de Django en cada entrada; verificación de propiedad en el servidor. |
| Documentación técnica | Pendiente | Criterio de aprobación: README y HANDOFF reflejan el estado real, y otra persona logra instalar el proyecto desde cero siguiendo el README y `docker-compose.yml`. |
| Integración de los componentes | Pendiente | Criterio de aprobación: la aplicación arranca desde una base vacía con Docker Compose, migraciones y seeders, y los flujos funcionan de punta a punta sobre la rama `main` sin conflictos pendientes. |

## 8. Historial de entregas

Registrar los principales entregables y versiones generadas durante el desarrollo.

Las fechas corresponden al cierre previsto de cada sprint; se confirman con la
fecha real al publicar cada versión.

| Versión | Descripción | Fecha | Referencia |
|---|---|---|---|
| v0.1.0 | Documentación, normalización de la base de datos, seguridad, integridad del carrito y pagos, pruebas y CI (Sprint 1) | 2026-08-03 | Por registrar |
| v0.2.0 | Libro mayor de inventario, Docker Compose y estructura inicial de Next.js con componentes visuales (Sprint 2) | 2026-08-18 | Por registrar |
| v0.3.0 | Migración de vistas restantes a Next.js, integración completa con la API y pruebas E2E (Sprint 3) | 2026-09-02 | Por registrar |
| v1.0.0 | Cierre, calidad, pruebas finales, documentación y entrega definitiva (Sprint 4) | 2026-09-16 | Por registrar |

## 9. Requerimientos pendientes y limitaciones

Registrar los elementos que no fueron completados o que requieren trabajo adicional.

La siguiente lista contiene los elementos que se prevé que queden fuera de la entrega.
Se actualiza en la evaluación final con los pendientes reales.

| ID | Descripción | Justificación | Estado |
|---|---|---|---|
| PEND-001 | Búsqueda avanzada y paginación del catálogo (REQ-F-013). | Meta opcional: se desarrolla solo si el equipo termina antes el compromiso del Sprint 4. | Opcional |
| PEND-002 | Integración de pasarela de pago real (Stripe, Mercado Pago, etc.). | Fuera del alcance académico del curso. | Pendiente |
| PEND-003 | Recuperación de contraseña por correo en producción (SMTP). | Requiere configuración externa de correo. | Pendiente |
| PEND-004 | Almacenamiento externo de imágenes con CDN y optimización de medios. | Mejora operativa fuera del alcance académico del curso. | Pendiente |
| PEND-005 | Pruebas de extremo a extremo en navegador (Playwright/Cypress). | Mejora de calidad futura. | Pendiente |

Estos elementos deberán ser identificados y documentados para evitar que se
interpreten como funcionalidades entregadas y aceptadas.

## 10. Observaciones del Project Owner

**Aspectos satisfactorios:**

[Se completa en la evaluación final.]

**Observaciones generales:**

[Se completa en la evaluación final.]

**Recomendaciones futuras:**

[Se completa en la evaluación final.]

## 11. Declaración de aceptación

Mediante esta acta se deja constancia de que el Project Owner ha revisado los
entregables presentados, evaluado el cumplimiento de los requerimientos establecidos
y registrado las observaciones correspondientes.

**Estado de aceptación:**

- [ ] Proyecto aceptado.
- [ ] Proyecto aceptado con observaciones menores.
- [ ] Proyecto no aceptado; requiere correcciones.

**Criterio de decisión acordado:**

- Aceptado: todos los requerimientos obligatorios están cumplidos y todos los aspectos de la sección 7 están aprobados.
- Aceptado con observaciones menores: el escenario manual se ejecuta sin fallos y los requerimientos obligatorios están cumplidos, pero quedan observaciones que no lo impiden (por ejemplo, documentación parcial o un requerimiento obligatorio secundario en estado Parcial con justificación).
- No aceptado: el escenario manual falla o no se cumple alguno de los requerimientos obligatorios principales (REQ-F-001 a REQ-F-008).

**Justificación de la decisión:**

[Se completa en la evaluación final.]

## 12. Acuerdos de cierre

| ID | Acuerdo | Responsable | Fecha límite |
|---|---|---|---|
| AC-001 | Congelar el código el 2026-09-14: del 14 al 16 de septiembre solo se corrigen errores y se prepara la demostración. | Cristian Camilo Cortés Ortiz | 2026-09-14 |
| AC-002 | Realizar la demostración del escenario manual ante el Project Owner en la Sprint Review del Sprint 4 y registrar la decisión de aceptación. | Miguel Ángel Herrera Luján | 2026-09-16 |
| AC-003 | Publicar el release v1.0.0 en GitHub con los entregables finales. | Cristian Camilo Cortés Ortiz | 2026-09-16 |
| AC-004 | Registrar como issues los pendientes y las mejoras futuras (PEND-001 a PEND-005) para que no se interpreten como funcionalidades entregadas. | Cristian Camilo Cortés Ortiz | 2026-09-16 |

## 13. Evidencias y referencias

- Repositorio: https://github.com/miguel-lujan2032/arcakane-zone.git.
- GitHub Project: https://github.com/users/Cristianco9/projects/2.
- Documentación final: `README.md` y `HANDOFF.md` (URL por registrar).
- Release final: Por registrar (v1.0.0).
- Pull Requests principales: Por registrar.
- Evidencias de pruebas: Por registrar (resultado de `pytest` y del pipeline de CI).
- Actas de revisiones anteriores: ACT-MIN-001 (reunión de inicio), ACT-SP-001 (planificación del Sprint 1), ACT-SR-001, ACT-RET-001, ACT-SP-002, ACT-SR-002 y ACT-RET-002.

## 14. Aprobación y cierre

Los participantes dejan constancia de que participaron en el proceso de revisión final y reconocen el estado de los entregables documentados en esta acta.

| Participante | Rol | Usuario de GitHub | Fecha |
|---|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | miguel-lujan2032 | 2026-12-28 |
| Cristian Camilo Cortés Ortiz | Scrum Master | @Cristianco9 | 2026-12-28 |
| Katherine Arboleda Ocoro | Developer | Kathe005 | 2026-12-28 |
| Luisa Maria Noreña Rueda | Developer | luisanorena25 | 2026-12-28 |
| Juan José Pérez Arana | Developer | juanperezarana | 2026-12-28 |

### Estado final del proyecto

- [ ] Requerimientos evaluados.
- [ ] Entregables revisados.
- [ ] Pruebas verificadas.
- [ ] Documentación final entregada.
- [ ] Pendientes identificados.
- [ ] Decisión de aceptación registrada.
- [ ] Acta de cierre aprobada.

**Evidencia de aprobación:** [URL del Pull Request o discusión correspondiente]

---

**Fin del documento**

*Esta acta constituye el registro documental de la evaluación final y aceptación
del proyecto. La aceptación debe corresponder a los entregables realmente verificados
y no implica que las funcionalidades pendientes se consideren completadas.*