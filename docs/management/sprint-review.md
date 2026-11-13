# Acta de Revisión del Sprint

## 1. Información general

| Campo | Información |
|---|---|
| Código del documento | ACT-SR-002 |
| Proyecto | Arkane Zone |
| Sprint | Sprint 2 |
| Fecha de revisión | 2026-11-30 (prevista) |
| Hora de inicio | 21:00 |
| Hora de finalización |22:00 |
| Scrum Master | Cristian Camilo Cortés Ortiz |
| Project Owner | Miguel Ángel Herrera Luján |
| Repositorio | `https://github.com/miguel-lujan2032/arcakane-zone.git` |
| GitHub Project | `https://github.com/users/Cristianco9/projects/2` |

## 2. Objetivo de la reunión

Inspeccionar los resultados obtenidos durante el Sprint, revisar el
Incremento desarrollado, verificar el cumplimiento de los criterios de
aceptación y recopilar retroalimentación para orientar las siguientes
etapas del proyecto.

Esta acta se prepara al inicio del Sprint con los datos de la planificación
(ACT-SP-002). Las columnas de estado, resultado y evidencia se completan
durante la Sprint Review; hasta entonces permanecen como «Pendiente» o
«Por registrar».

## 3. Participantes

| Nombre completo | Rol | Asistencia |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | Remota |
| Cristian Camilo Cortés Ortiz | Scrum Master | Remota |
| Katherine Arboleda Ocoro | Developer | Remota |
| Luisa Maria Noreña Rueda | Developer | Remota |
| Juan José Pérez Arana | Developer | Remota |
| Interesado / Invitado | Interesado | Remota |

## 4. Objetivo del Sprint

**Sprint Goal establecido:**

Completar la auditoría del inventario mediante el libro mayor de movimientos,
garantizar la reproducibilidad del entorno con Docker Compose e iniciar la
modernización del frontend con Next.js + React + TypeScript, construyendo la
estructura visual global y los componentes reutilizables.

**Resultado general:**

[Se completa en la Sprint Review: indicar si se alcanzó el objetivo.]

## 5. Revisión de los elementos del Sprint Backlog

| ID | Elemento seleccionado | Estado | Story Points | Issue |
|---|---|---|---|---|
| US-201 | Libro mayor de movimientos de inventario | Pendiente | 3 | AZ-S1-14 |
| US-202 | Containerización con Docker Compose | Pendiente | 3 | AZ-S1-22 |
| US-203 | Inicialización de Next.js + TypeScript | Pendiente | 8 | AZ-S2-01 |
| US-204 | Estructura visual global y componentes reutilizables | Pendiente | 5 | AZ-S2-02 |

**Total de Story Points planificados:** 19

**Total de Story Points completados:** Por registrar

Nota: según RISK-201 y RISK-202 de la planificación, si falta capacidad la
primera historia en moverse al Sprint 3 es US-204.

## 6. Incremento desarrollado

Funcionalidades previstas para el Incremento (versión v0.2.0).

| ID | Funcionalidad | Descripción | Evidencia |
|---|---|---|---|
| INC-201 | Libro mayor de inventario | Modelo `MovimientoInventario` con integración en pagos y ajustes de stock | Por registrar |
| INC-202 | Docker Compose | `Dockerfile` y `docker-compose.yml` con servicios web y db | Por registrar |
| INC-203 | Proyecto Next.js | Inicialización con TypeScript, Tailwind CSS, ESLint y estructura de carpetas | Por registrar |
| INC-204 | Componentes React | Layout global, navbar, footer, `VideojuegoCard`, `Button`, `Input`, `Table`, `Badge` | Por registrar |
| INC-205 | Documentación | README actualizado con Docker y `frontend/README.md` | Por registrar |

## 7. Validación de criterios de aceptación

| ID | Criterio de aceptación | Resultado | Observaciones |
|---|---|---|---|
| CA-001 | US-201: modelo `MovimientoInventario` con tipo, cantidad, fecha y referencia | Pendiente | Por registrar |
| CA-002 | US-201: registro automático de movimientos al pagar y ajustar stock | Pendiente | Por registrar |
| CA-003 | US-201: pruebas unitarias e integración del libro mayor | Pendiente | Por registrar |
| CA-004 | US-201: admin permite filtrar por videojuego y fecha | Pendiente | Por registrar |
| CA-005 | US-202: `Dockerfile` funcional con Gunicorn y WhiteNoise | Pendiente | Por registrar |
| CA-006 | US-202: `docker-compose.yml` con web, db, volúmenes y red personalizada | Pendiente | Por registrar |
| CA-007 | US-202: la aplicación se levanta con `docker-compose up` desde base vacía | Pendiente | Por registrar |
| CA-008 | US-202: README documenta el entorno con Docker | Pendiente | Por registrar |
| CA-009 | US-203: Next.js inicializado con TypeScript en `frontend/` | Pendiente | Por registrar |
| CA-010 | US-203: Tailwind, ESLint y Prettier configurados | Pendiente | Por registrar |
| CA-011 | US-203: estructura de carpetas y capa de API funcional | Pendiente | Por registrar |
| CA-012 | US-204: layout global con navbar y footer | Pendiente | Por registrar |
| CA-013 | US-204: componentes tipados reutilizables | Pendiente | Por registrar |
| CA-014 | US-204: pruebas de componentes con Jest y Testing Library | Pendiente | Por registrar |
| CA-015 | General: demostración de Docker, libro mayor y estructura Next.js | Pendiente | Por registrar |

Los criterios completos de cada historia están en la sección 7 de ACT-SP-002.

## 8. Pull Requests y evidencias técnicas

| Pull Request | Descripción | Estado | Revisor |
|---|---|---|---|
| Por registrar | Libro mayor de inventario (US-201) | Pendiente | Por asignar |
| Por registrar | Docker Compose (US-202) | Pendiente | Por asignar |
| Por registrar | Inicialización Next.js (US-203) | Pendiente | Por asignar |
| Por registrar | Componentes visuales (US-204) | Pendiente | Por asignar |

**Otras evidencias:**

- Pruebas ejecutadas: Por registrar (`pytest` y `npm test` en frontend).
- Capturas de pantalla: Por registrar.
- Documentación técnica: README y `frontend/README.md` actualizados.
- Versión o demostración: Por registrar (v0.2.0).

## 9. Retroalimentación del Project Owner y los interesados

**Aspectos satisfactorios:**

[Se completa en la Sprint Review.]

**Observaciones y oportunidades de mejora:**

[Se completa en la Sprint Review.]

**Nuevas necesidades identificadas:**

[Se completa en la Sprint Review.]

## 10. Elementos pendientes

| ID | Elemento pendiente | Motivo | Acción propuesta |
|---|---|---|---|
| PEND-001 | Por registrar | Por registrar | Por registrar |

Los elementos no completados deberán regresar al Product Backlog para su
evaluación y priorización. No se consideran automáticamente comprometidos
para el siguiente Sprint.

## 11. Acuerdos y decisiones

| ID | Acuerdo o decisión | Responsable | Fecha límite |
|---|---|---|---|
| AC-001 | Registrar resultado de la demostración | Scrum Master | 2026-08-18 |
| AC-002 | Devolver pendientes al Product Backlog | Project Owner | 2026-08-18 |
| AC-003 | Continuar la migración de vistas a Next.js en el Sprint 3 | Equipo | 2026-08-25 |
| AC-004 | Publicar el release v0.2.0 en GitHub | Scrum Master | 2026-08-18 |
| AC-005 | Documentar la configuración de CORS y autenticación para futuras integraciones | Luisa Maria Noreña Rueda | 2026-08-25 |

## 12. Evidencias y referencias

- Repositorio: https://github.com/miguel-lujan2032/arcakane-zone.git.
- GitHub Project: https://github.com/users/Cristianco9/projects/2.
- Sprint Backlog: GitHub Project del equipo (US-201 a US-204).
- Pull Requests: Por registrar.
- Incremento presentado: Por registrar (v0.2.0).
- Documentación relacionada: ACT-SP-002, ACT-SP-001, ACT-PA-001, `README.md` y `pytest.ini`.

## 13. Observaciones

- El libro mayor de inventario cierra el pendiente del Sprint 1 (AZ-S1-14) y
  la containerización cierra el pendiente AZ-S1-22.
- La migración completa del frontend a Next.js continuará en el Sprint 3;
  en este Sprint solo se entrega la estructura inicial y los componentes
  reutilizables.
- La búsqueda avanzada y la paginación del catálogo (REQ-F-013) son una meta
  opcional del Sprint 4.
- Los campos «Por registrar», «Por confirmar» y «Por definir» se completan
  con la información real de la reunión antes de la aprobación del acta.

## 14. Validación y aprobación

| Participante | Rol | Usuario de GitHub | Fecha |
|---|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | [Por confirmar] | YYYY-MM-DD |
| Cristian Camilo Cortés Ortiz | Scrum Master | @Cristianco9 | YYYY-MM-DD |
| Katherine Arboleda Ocoro | Developer | [Por confirmar] | YYYY-MM-DD |
| Luisa Maria Noreña Rueda | Developer | [Por confirmar] | YYYY-MM-DD |
| Juan José Pérez Arana | Developer | [Por confirmar] | YYYY-MM-DD |

### Estado de la revisión

- [ ] Se presentó el Incremento desarrollado.
- [ ] Se revisaron los elementos del Sprint Backlog.
- [ ] Se verificaron los criterios de aceptación.
- [ ] Se registró la retroalimentación.
- [ ] Se identificaron elementos pendientes.
- [ ] Se documentaron los acuerdos y decisiones.

**Evidencia de aprobación:** [URL del Pull Request o discusión correspondiente]

---

**Fin del documento**

*La Sprint Review es una sesión de inspección y adaptación del producto. No
debe entenderse únicamente como una presentación de resultados ni como una
reunión exclusiva de aprobación del trabajo realizado.*