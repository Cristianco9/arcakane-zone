# Acta de Retrospectiva del Sprint 1

**Código:** ACT-RET-001  
**Proyecto:** Arcakane Zone  
**Sprint:** 1  
**Fecha:** 2026-11-16  
**Scrum Master:** Cristian Camilo Cortés Ortiz  

## 1. Participantes

| Nombre | Rol | Asistencia |
|---|---|---|
| Cristian Camilo Cortés Ortiz | Scrum Master | Presente |
| Katherine Arboleda Ocoro | Developer | Presente |
| Luisa Maria Noreña Rueda | Developer | Presente |
| Juan José Pérez Arana | Developer | Presente |

## 2. Evaluación general del Sprint

**Sprint Goal:** Documentar, normalizar, asegurar y containerizar.

**Percepción general:** El equipo logró completar la mayoría de los objetivos. 
La normalización y la seguridad fueron los mayores logros. La inicialización de
la nueva aplicación Front-end junto con la contenerización de los servicios de la
aplicación.

**Nivel de cumplimiento:** 90% (27 de 30 SP).

## 3. ¿Qué funcionó bien?

| ID | Aspecto positivo | Impacto |
|---|---|---|
| POS-001 | La documentación colaborativa permitió un entendimiento común. | Alto |
| POS-002 | Las pruebas automatizadas detectaron errores en la normalización. | Alto |
| POS-003 | La comunicación diaria y el uso de PR facilitaron la integración. | Medio |

## 4. ¿Qué dificultades encontramos?

| ID | Dificultad | Causa | Impacto |
|---|---|---|---|
| IMP-001 | La normalización de la base de datos generó conflictos con migraciones existentes. | Falta de experiencia en migraciones complejas. | Medio |
| IMP-002 | Curva de aprendizaje de React.js | Subestimación de la tarea. | Medio |
| IMP-003 | La idempotencia en pagos requirió más pruebas de las previstas. | Complejidad de concurrencia. | Alto |

## 5. ¿Qué podemos mejorar?

| ID | Oportunidad de mejora | Beneficio |
|---|---|---|
| MEJ-001 | Estimar con mayor precisión las tareas de infraestructura. | Mejor planificación. |
| MEJ-002 | Realizar pruebas de concurrencia desde el inicio. | Evitar retrabajos. |
| MEJ-003 | Asignar un responsable fijo para el libro mayor de inventario. | Cerrar la tarea en el sprint. |

## 6. Acciones de mejora

| ID | Acción | Responsable | Fecha límite |
|---|---|---|---|
| ACT-001 | Incluir el desarrollo del front-end en el Sprint 2 con prioridad alta. | Luisa | 2026-11-30 |
| ACT-002 | Documentar el proceso de migraciones para futuras normalizaciones. | Kathe005 | 2026-11-30 |
| ACT-003 | Agregar pruebas de concurrencia al pipeline de CI. | cristian | 2026-11-30 |

## 7. Acuerdos

- Las acciones de mejora se registrarán como issues en GitHub Projects.
- Se realizará seguimiento en la retrospectiva del Sprint 2.