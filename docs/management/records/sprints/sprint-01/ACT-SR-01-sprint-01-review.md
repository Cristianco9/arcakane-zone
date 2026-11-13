# Acta de Revisión del Sprint 1

**Código:** ACT-SR-001  
**Proyecto:** Arcakane Zone  
**Sprint:** 1  
**Fecha de revisión:** 2026-11-16  
**Scrum Master:** Cristian Camilo Cortés Ortiz  
**Project Owner:** Miguel Ángel Herrera Luján  

## 1. Participantes

| Nombre | Rol | Asistencia |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | Remota |
| Cristian Camilo Cortés Ortiz | Scrum Master | Remota |
| Katherine Arboleda Ocoro | Developer | Remota |
| Luisa Maria Noreña Rueda | Developer | Remota |
| Juan José Pérez Arana | Developer | Remota |

## 2. Objetivo del Sprint (evaluado)

Documentar el estado actual, normalizar la base de datos, endurecer seguridad y 
autorización, asegurar integridad del carrito y pagos, y containerizar la aplicación.

**Resultado general:**  
El objetivo se alcanzó parcialmente. Se completaron US-101, US-102, US-103 y US-104. 
US-105 (libro mayor de inventario) quedó en progreso. US-106 (testing y CI) se completó. 
US-107 (Docker) quedó en progreso.

## 3. Revisión de elementos del Sprint Backlog

| ID | Elemento | Estado | SP planificados | SP completados |
|---|---|---|---|---|
| US-101 | Documentación y análisis | Done | 5 | 5 |
| US-102 | Seguridad y autorización | Done | 3 | 3 |
| US-103 | Integridad de carrito y pagos | Done | 5 | 5 |
| US-104 | Normalización de base de datos | Done | 8 | 8 |
| US-105 | Libro mayor de inventario | In Progress | 3 | 0 |
| US-106 | Testing y CI | Done | 3 | 3 |
| US-107 | Dockerización | In Progress | 3 | 0 |

**Total SP completados:** 25 de 30.

## 4. Incremento desarrollado

| ID | Funcionalidad | Evidencia |
|---|---|---|
| INC-001 | Documentación completa del proyecto (contexto, funcionalidades, modelo, arquitectura, riesgos). | Pull Request #12 |
| INC-002 | Vistas administrativas protegidas con `staff_member_required` y configuración de seguridad para producción. | Pull Request #15 |
| INC-003 | Validación de entradas, manejo de errores HTTP y pago idempotente. | Pull Request #18 |
| INC-004 | Modelos normalizados: categorías y géneros M2M, tablas catálogo para estados, roles y permisos. | Pull Request #20 |
| INC-005 | Dependencias de testing y CI con GitHub Actions. | Pull Request #22 |

## 5. Validación de criterios de aceptación

| Criterio | Resultado |
|---|---|
| US-101: documentos entregados | Cumplido |
| US-102: vistas protegidas y pruebas | Cumplido |
| US-103: validación, errores, idempotencia, concurrencia | Cumplido |
| US-104: normalización completa | Cumplido |
| US-105: libro mayor | Parcial (modelo creado, sin integración completa) |
| US-106: testing y CI | Cumplido |
| US-107: Docker | Parcial (Dockerfile creado, falta compose) |

## 6. Retroalimentación del Project Owner

- **Aspectos satisfactorios:** La normalización de la base de datos y las mejoras 
de seguridad son sólidas. Las pruebas automatizadas brindan confianza.
- **Observaciones:** El libro mayor de inventario debe completarse en el Sprint 2. 
La dockerización debe finalizarse para garantizar reproducibilidad.
- **Nuevas necesidades:** Iniciar la migración del frontend a React.js en el Sprint 2.

## 7. Pendientes

| ID | Pendiente | Acción |
|---|---|---|
| PEND-001 | Completar libro mayor de inventario (AZ-S1-14). | Mover al Sprint 2. |
| PEND-002 | Completar Docker Compose (AZ-S1-22). | Mover al Sprint 2. |

## 8. Acuerdos

- Los pendientes se incluyen en el Sprint 2.
- Se publica la versión v0.1.0 con los avances.

## 9. Aprobación

| Participante | Rol | Fecha |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | 2026-11-16 |
| Cristian Camilo Cortés Ortiz | Scrum Master | 2026-11-16 |
| Katherine Arboleda Ocoro | Developer | 2026-11-16 |
| Luisa Maria Noreña Rueda | Developer | 2026-11-16 |
| Juan José Pérez Arana | Developer | 2026-11-16 |