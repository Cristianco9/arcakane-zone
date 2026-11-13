# ACT-MIN-001 — Acta de reunión de inicio y entrega del contexto del proyecto

## 1. Información general

| Campo | Descripción |
|---|---|
| Código del acta | ACT-MIN-001 |
| Nombre de la reunión | Reunión inicial — Entrega del contexto de Arcakane Zone |
| Fecha de la reunión | 1 Noviembre de 2026 |
| Hora de inicio | 6:30 p. m. |
| Hora de finalización | 7:00 p. m. |
| Duración | 30 minutos |
| Proyecto | Arcakane Zone |
| Modalidad | Remota |
| Responsable de la entrega | Miguel Ángel Herrera Luján |
| Tipo de reunión | Inicio del proyecto y transferencia de contexto |

## 2. Participantes

| Nombre completo | Rol | Asistencia |
|---|---|---|
| Miguel Ángel Herrera Luján | Project Owner | Presente |
| Cristian Camilo Cortes Ortiz | Scrum Master / Developer | Presente |
| katherine Arboleda Ocoro | Developer | Presente |
| Luisa Maria Noreña Rueda | Developer | Presente |
| Juan José Pérez Arana | Developer | Ausente |

**Total de participantes:** 5  
**Asistentes:** 5  
**Ausentes:** 0

## 3. Objetivo de la reunión

Presentar al equipo de desarrollo el estado actual del proyecto **Arcakane Zone**, 
una aplicación web de comercio electrónico de videojuegos desarrollada en Django. 
Se entregó el repositorio con el código fuente y se expusieron las necesidades de 
mejora: normalización de la base de datos, endurecimiento de la seguridad, 
integridad del carrito y pagos, pruebas automatizadas, containerización con 
Docker y migración del frontend a React.js.

## 4. Agenda

1. Presentación del proyecto y su propósito.
2. Estado actual del repositorio y arquitectura.
3. Funcionalidades implementadas y limitaciones.
4. Problemas identificados y backlog inicial.
5. Entrega del repositorio y acceso al GitHub Projects.
6. Acuerdos y compromisos.

## 5. Desarrollo de la reunión

### 5.1. Presentación del proyecto

Arcakane Zone es una tienda en línea de videojuegos. Los usuarios pueden registrarse, 
explorar un catálogo, agregar juegos al carrito, realizar pedidos con pago simulado, 
consultar su historial y contactar a soporte. Los administradores gestionan el catálogo, 
roles y reportes de ventas e inventario.

Tecnologías identificadas: Django 5.2, PostgreSQL, Tailwind CSS (vía CDN), HTMX, 
django-unfold para el admin, WhiteNoise, almacenamiento local para medios, pruebas 
con pytest. La aplicación está desplegada en Render.

### 5.2. Estado inicial del repositorio

Se entregó el repositorio: `https://github.com/miguel-lujan2032/arcakane-zone.git`  
El equipo receptor deberá trabajar sobre este código. El repositorio contiene las apps: `catalogo`, `cuentas`, `pedidos`, `pagos`, `reportes`, `soporte`, y plantillas HTML con Tailwind.

Se identificaron las siguientes necesidades de mejora:

- Documentación y análisis del estado actual (contexto, funcionalidades, modelo, arquitectura, pruebas).
- Normalización de la base de datos: categorías y géneros muchos-a-muchos, eliminación de enumerados, integridad referencial, catálogo de permisos y roles, libro mayor de inventario.
- Seguridad: validación de entradas, autorización unificada, protección de vistas administrativas, configuración de producción (CSRF, HSTS, cookies seguras).
- Integridad y concurrencia del carrito y de los pagos: idempotencia, manejo de reintentos, control de stock.
- Pruebas automatizadas y CI.
- Containerización con Docker Compose.
- Migración del frontend a Next.js + React + TypeScript.

### 5.3. Funcionalidades existentes

- Registro, login, logout, perfil, cambio de contraseña.
- Catálogo con filtros por categoría, plataforma y género.
- Carrito con HTMX (agregar, actualizar cantidades, eliminar).
- Checkout y pago simulado (aprobado/rechazado).
- Historial de pedidos, cancelación de pedidos pendientes.
- Reportes para staff: dashboard, ventas, inventario, videojuegos.
- Soporte: contacto, mayor información, ayuda.
- Admin personalizado con django-unfold.

### 5.4. Acuerdos y compromisos

| N.º | Acuerdo |
|---|---|
| 1 | El repositorio de GitHub será la fuente principal del código. |
| 2 | Se usará GitHub Projects para la gestión de issues y tablero. |
| 3 | Se trabajará con una rama por issue y Pull Requests revisados por otro integrante. |
| 4 | Cada Sprint se planificará y documentará con actas formales. |
| 5 | El equipo receptor analizará el código y propondrá el backlog del Sprint 1. |

## 6. Evidencias y recursos

| Recurso | Ubicación |
|---|---|
| Repositorio | `https://github.com/miguel-lujan2032/arcakane-zone.git` |
| GitHub Projects | `https://github.com/users/Cristianco9/projects/2` |
| Documentación técnica existente | `README.md` del repositorio |

## 7. Aprobación

| Rol | Nombre completo | Asistencia |
|---|---|---|
| Project Owner | Miguel Ángel Herrera Luján | Presente |
| Scrum Master | Cristian Camilo Cortés Ortiz | Presente |
| Developer | Kathe005 | Presente |
| Developer | luisanorena25 | Presente |
| Developer | Juan José Pérez Arana | Ausente |