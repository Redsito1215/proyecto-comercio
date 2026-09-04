<!--
Sync Impact Report
- Version change: plantilla sin versión → 1.0.0
- Modified principles: placeholders iniciales → cinco principios obligatorios del proyecto
- Added sections: Restricciones Técnicas y Funcionales; Flujo Spec Kit y Puertas de Calidad
- Removed sections: ninguna
- Follow-up TODOs: ninguno
-->
# Constitución de Comercio Inteligente

## Core Principles

### I. Desarrollo dirigido por especificaciones
Toda funcionalidad MUST comenzar y conservar trazabilidad en una de las siete carpetas
`specs/001` a `specs/007`. Cada requisito MUST vincularse con escenarios de aceptación,
modelo de datos, contrato, tareas y pruebas. El código que no responda a un requisito
aprobado MUST NOT incorporarse. Spec Kit de GitHub es el flujo normativo del proyecto.

### II. Integridad comercial y trazabilidad
Ventas, pagos, inventario, compras, caja, devoluciones, mermas y cambios de precios MUST
conservar autor, fecha, estado anterior, estado resultante y referencia de negocio. Las
operaciones que afecten dinero o existencias MUST ser atómicas, idempotentes cuando puedan
reintentarse y auditables. Los registros históricos MUST NOT eliminarse para ocultar una
corrección; se usarán anulaciones, ajustes o movimientos compensatorios.

### III. Inteligencia explicable y responsable
Todo pronóstico, segmento, promoción, alerta de fraude o recomendación MUST mostrar los
datos considerados, la razón, la fecha de cálculo, el nivel de confianza y el impacto
económico estimado. Una alerta MUST NOT declarar culpabilidad ni ejecutar automáticamente
una sanción. La demanda MUST considerar promociones, precios, agotamientos, sustitutos y
estacionalidad; el valor del cliente MUST considerar frecuencia, recurrencia y margen,
además del gasto.

### IV. Seguridad y privacidad desde el diseño
Cada acción protegida MUST validar autenticación y autorización en el servidor. Las
contraseñas MUST almacenarse mediante hash seguro; secretos MUST entrar por variables de
entorno. El sistema MUST NOT almacenar PAN completo, CVV ni credenciales bancarias. La
información personal MUST limitarse al propósito aprobado y conservar evidencia de
consentimiento para comunicaciones y promociones.

### V. Calidad verificable y despliegue reproducible
Los cálculos monetarios, márgenes, existencias, caja y reglas promocionales MUST tener
pruebas automatizadas. Cada historia MUST disponer de una validación independiente. El
sistema completo MUST levantarse con Docker Compose, persistir datos mediante volúmenes y
publicar comprobaciones de salud. Ninguna tarea se considera completa si la documentación,
las pruebas o el arranque reproducible quedan pendientes.

## Restricciones Técnicas y Funcionales

- La estructura mínima del repositorio MUST conservar `.specify/`, las siete carpetas de
  `specs/`, `backend/`, `frontend/` y `tests/`.
- La base operativa MUST ser MongoDB y se modelará documentalmente como tablas lógicas para
  facilitar diagramas, contratos, índices y validación académica.
- MongoDB MUST ejecutarse como replica set cuando una operación requiera transacciones.
- ClickHouse MUST almacenar la publicación analítica de informes compuestos y Airflow MUST
  orquestar el ETL reproducible e idempotente.
- El frontend MUST reutilizar el lenguaje visual y los patrones de interacción de
  `C:\proyect6softwa`, adaptados a la identidad y alcance de Comercio Inteligente.
- Los siete dominios obligatorios son: ventas e inventario; clientes y fidelización; precios
  y márgenes; pronóstico de demanda; promociones inteligentes; caja, mermas y fraude; pagos
  y seguridad.
- El alcance MUST incluir informes operativos y gerenciales, previsualización, PDF,
  exportaciones y trazabilidad de sus fuentes.
- La interfaz, mensajes, documentación y evidencia académica MUST estar en español.

## Flujo Spec Kit y Puertas de Calidad

1. Constitución: aprobar principios y restricciones transversales.
2. Especificación: redactar historias, requisitos, casos límite y resultados medibles sin
   introducir decisiones técnicas.
3. Lista de calidad: cerrar ambigüedades antes de planificar.
4. Plan e investigación: justificar arquitectura, alternativas y dependencias.
5. Diseño: definir tablas lógicas de MongoDB, relaciones, estados, índices y contratos.
6. Tareas: descomponer por historia con identificadores, dependencias, rutas y pruebas.
7. Implementación: ejecutar por incrementos verificables; el MVP no invalida el alcance
   completo.
8. Validación: ejecutar pruebas unitarias, de contrato, integración, seguridad, ETL y
   recorridos visuales antes de cerrar cada especificación.

Los documentos MUST usar fechas ISO `YYYY-MM-DD`, criterios medibles y lenguaje obligatorio
MUST/MUST NOT cuando corresponda. Ninguna decisión técnica MAY contradecir esta constitución
sin una enmienda versionada.

## Governance

Esta constitución prevalece sobre planes, tareas, código y preferencias de implementación.
Toda enmienda MUST explicar el motivo, impacto, migración requerida y artefactos afectados.
La versión sigue SemVer: MAJOR para cambios incompatibles de gobierno, MINOR para principios
o secciones nuevas y PATCH para aclaraciones sin cambio normativo. Cada revisión de una
especificación MUST comprobar estructura, trazabilidad, seguridad, pruebas, explicabilidad y
despliegue Docker. Las excepciones MUST quedar justificadas en el plan y aprobadas antes de
la implementación.

**Version**: 1.0.0 | **Ratified**: 2026-09-03 | **Last Amended**: 2026-09-03
