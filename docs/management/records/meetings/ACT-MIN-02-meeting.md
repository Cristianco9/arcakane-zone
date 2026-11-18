# ACT-MIN-002 — Acta de reunión de definición de requerimientos del Sprint 2

## 1. Información general

| Campo | Descripción |
|---|---|
| Código del acta | ACT-MIN-002 |
| Nombre de la reunión | Reunión de definición de requerimientos — Sprint 2 |
| Fecha de la reunión | 16 de noviembre de 2026 |
| Hora de inicio | 6:30 p. m. |
| Hora de finalización | 7:30 p. m. |
| Duración | 60 minutos |
| Proyecto | Arcakane Zone |
| Modalidad | Remota |
| Responsable de la reunión | Miguel Ángel Herrera Luján |
| Tipo de reunión | Definición de requerimientos y priorización del Sprint 2 |
| Periodo del Sprint | 16 de noviembre al 30 de noviembre de 2026 |

## 2. Participantes

| Nombre completo | Rol | Asistencia |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | Presente |
| Cristian Camilo Cortés Ortiz | Scrum Master / Developer | Presente |

**Total de participantes:** 2
**Asistentes:** 2
**Ausentes:** 3

## 3. Objetivo de la reunión

Presentar al Project Owner el resultado del Sprint 1 y el diagnóstico del estado 
actual del repositorio, y recibir de él los requerimientos y prioridades del Sprint 2. 
El Sprint 2 tiene dos frentes: integrar y fortalecer el backend (Django + DRF) 
y construir con React + TypeScript las diez primeras interfaces definidas en los 
wireframes (WF-01 a WF-10).

## 4. Agenda

1. Resultado del Sprint 1 y acciones de mejora de la retrospectiva.
2. Estado actual del backend y del frontend.
3. Requerimientos del Sprint 2 definidos por el Project Owner.
4. Priorización, dependencias y capacidad del equipo.
5. Acuerdos y compromisos.

## 5. Desarrollo de la reunión

### 5.1. Resultado del Sprint 1 y estado actual

El Scrum Master presentó el cumplimiento del Sprint 1 (27 de 30 SP) y el diagnóstico del repositorio:

- **Backend:** API REST versionada en `/api/v1/` con autenticación por token y sesión, catálogo, carrito, pedidos, pagos, ventas, reportes, soporte y usuarios/roles de solo lectura. La suite de 130 pruebas pasa. Faltan integración continua, inventario por API, límites de intentos, vencimiento de tokens y recuperación de contraseña.
- **Trabajo pendiente de integrar:** las ramas de normalización de la base de datos (AZ-S1-14 a AZ-S1-20: libro mayor de inventario, categorías y géneros M2M, estados como tablas, roles y catálogos maestros) están terminadas, pero no se han fusionado a `main`.
- **Frontend:** solo existe la plantilla de Vite + React + TypeScript + Tailwind. Los wireframes (30 pantallas) están en `docs/resources/wireframes/`.

### 5.2. Requerimientos definidos por el Project Owner

El Project Owner indicó que la prioridad es dejar una base de backend segura y consistente, y mostrar las primeras pantallas de la tienda funcionando contra la API real.

**Backend**

| N.º | Requerimiento | Prioridad | Referencia |
|---|---|---|---|
| RB-01 | Integrar a `main` la normalización de la base de datos y adaptar la API al nuevo modelo sin romper el contrato actual. | Alta | REQ-F-010, REQ-F-012 |
| RB-02 | Exponer el libro mayor de inventario por API (consulta de movimientos y ajustes manuales con trazabilidad). | Alta | REQ-F-011 |
| RB-03 | Autorización por roles de negocio: `administrador`, `gestor_inventario`, `soporte` y `cliente`, con una matriz rol × endpoint documentada y probada. | Alta | REQ-F-008, REQ-NF-001 |
| RB-04 | Pagos sin doble cobro: bloqueo concurrente e idempotencia en el procesamiento del pago. | Alta | REQ-F-006 |
| RB-05 | Integración continua con ejecución de pruebas, cobertura y lint en cada Pull Request. | Alta | REQ-NF-002 |
| RB-06 | Seguridad de autenticación: límite de intentos, tokens con vencimiento y recuperación de contraseña por API. | Media | REQ-F-001, REQ-F-002 |
| RB-07 | Configuración de producción, registro de eventos (logging) y verificación de salud con base de datos. | Media | REQ-NF-004 |
| RB-08 | Revalidar precios y disponibilidad del título en el carrito y el checkout. | Media | REQ-F-005, REQ-F-006 |
| RB-09 | Gestión de usuarios y roles por API, pasarela de pago abstraída, ciclo de vida del pedido y documentación OpenAPI. | Deseable | REQ-F-007, REQ-F-009 |

**Frontend**

| N.º | Requerimiento | Prioridad | Referencia |
|---|---|---|---|
| RF-01 | Base del frontend: rutas, estructura visual global (cabecera y pie), cliente de API, manejo de sesión y componentes reutilizables. | Alta | REQ-NF-005 |
| RF-02 | Pantallas de exploración: Home (WF-01), Catálogo con filtros y paginación (WF-02) y Detalle del videojuego (WF-03). | Alta | REQ-F-003, REQ-F-004 |
| RF-03 | Pantallas de acceso: Registro (WF-04) e Inicio de sesión (WF-05). | Alta | REQ-F-001 |
| RF-04 | Pantallas de cuenta: Perfil (WF-08) y Cambiar contraseña (WF-09). | Alta | REQ-F-002 |
| RF-05 | Carrito de compras (WF-10) conectado a la API. | Alta | REQ-F-005 |
| RF-06 | Recuperar contraseña (WF-06) y Nueva contraseña (WF-07), dependientes de la recuperación por API del backend. | Media | REQ-F-001 |

### 5.3. Decisiones del Project Owner

- Las pantallas deben seguir fielmente los wireframes (paleta oscura con azul primario) y funcionar en escritorio y móvil.
- El inicio de sesión del wireframe admite «usuario o correo»; se acepta ajustar el backend para soportarlo.
- La sección «Más vendidos» de Home puede usar un orden provisional en este Sprint; el criterio definitivo se define más adelante.
- Los filtros del catálogo pueden ser de selección única en este Sprint; la selección múltiple queda como mejora futura.
- Los issues de backend usan el prefijo `AZ-S2-BE-NN` y los de frontend `AZ-S2-FE-NN`.
- Las 20 pantallas restantes (WF-11 a WF-30) se planificarán en los Sprints 3 y 4.

### 5.4. Capacidad y dependencias

- Referencia de capacidad: el equipo completó 27 SP en el Sprint 1. Se compromete el trabajo de prioridad Alta y se toma el de prioridad Media según el avance; lo Deseable queda como reserva.
- Dependencias principales: la integración de la normalización (RB-01) habilita RB-02, RB-03 y la adaptación de la API; la recuperación de contraseña por API (RB-06) habilita las pantallas WF-06 y WF-07; la base del frontend (RF-01) habilita todas las pantallas.

### 5.5. Acuerdos y compromisos

| N.º | Acuerdo | Responsable | Fecha límite |
|---|---|---|---|
| 1 | Crear en GitHub Projects el milestone «Sprint 2» y los issues de backend (15) y frontend (11) con su ID y Story Points. | Cristian Camilo Cortés Ortiz | 2026-11-17 |
| 2 | Integrar la cadena de ramas de normalización a `main` mediante Pull Request revisado. | Equipo de backend | 2026-11-20 |
| 3 | Entregar la base del frontend (rutas, layout, cliente de API y sesión) para que las pantallas puedan avanzar en paralelo. | Equipo de frontend | 2026-11-20 |
| 4 | Mantener una rama por issue y Pull Requests revisados por otro integrante, con CI en verde. | Todo el equipo | Durante el Sprint |
| 5 | Documentar el proceso de migraciones y agregar pruebas de concurrencia a la integración continua (acciones ACT-002 y ACT-003 del Sprint 1). | Katherine Arboleda Ocoro / Cristian Camilo Cortés Ortiz | 2026-11-30 |
| 6 | Revisión de avance con el Project Owner a mitad del Sprint. | Cristian Camilo Cortés Ortiz | 2026-11-24 |
| 7 | Realizar la Sprint Review y la Retrospectiva del Sprint 2. | Todo el equipo | 2026-11-30 |

## 6. Evidencias y recursos

| Recurso | Ubicación |
|---|---|
| Repositorio | `https://github.com/Cristianco9/arcakane-zone` |
| GitHub Projects | `https://github.com/users/Cristianco9/projects/3/` |
| Wireframes | `docs/resources/wireframes/` |
| Contrato de la API | `docs/api/API.md` |
| Backlog de backend | `sprint-2-backend-backlog.md` |
| Backlog de frontend | `sprint-2-frontend-backlog.md` |
| Acta anterior | `ACT-MIN-01-meeting-kickoff.md` |

## 7. Aprobación

| Rol | Nombre completo | Asistencia |
|---|---|---|
| Project Owner | Miguel Ángel Herrera Luján | Presente |
| Scrum Master | Cristian Camilo Cortés Ortiz | Presente |