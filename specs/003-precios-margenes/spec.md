# Feature Specification: Precios y márgenes

**Feature Branch**: `003-precios-margenes`  
**Created**: 2026-09-03  
**Status**: Ready for implementation

## User Scenarios & Testing

### User Story 1 - Conocer el margen real (P1)
Como responsable comercial quiero ver costo, precio, margen monetario y porcentual por producto para decidir con evidencia.

**Independent Test**: Consultar productos con distintos costos y verificar cálculos y clasificación visual.

### User Story 2 - Cambiar precios con control (P1)
Como gerente quiero simular y aplicar un precio sin cruzar el margen mínimo autorizado.

**Independent Test**: Rechazar un precio bajo el piso, aceptar uno válido y conservar el historial.

### User Story 3 - Comparar mercado (P2)
Como analista quiero registrar precios de competidores con fuente y fecha para medir la brecha sin convertirlos automáticamente en precio propio.

**Independent Test**: Registrar observaciones y obtener mínimo, mediana y posición relativa.

## Requirements
- **FR-001**: El sistema MUST calcular margen como precio menos costo y porcentaje sobre precio.
- **FR-002**: El sistema MUST mostrar explícitamente productos sin costo confiable.
- **FR-003**: Cada producto MUST admitir un porcentaje mínimo de margen.
- **FR-004**: La simulación MUST devolver resultado, piso y advertencias sin modificar datos.
- **FR-005**: La aplicación MUST rechazar precios bajo el piso salvo flujo de autorización posterior.
- **FR-006**: Todo cambio MUST conservar precio anterior, nuevo, motivo, actor y vigencia.
- **FR-007**: El sistema MUST registrar observaciones externas con competidor, canal, fuente y fecha.
- **FR-008**: Las comparaciones MUST indicar antigüedad y no sobrescribir precios automáticamente.
- **FR-009**: Las ventas MUST conservar el precio y costo históricos de cada línea.
- **FR-010**: La interfaz MUST distinguir margen saludable, ajustado, crítico y desconocido.

## Success Criteria
- **SC-001**: Un usuario identifica productos con margen crítico en menos de 15 segundos.
- **SC-002**: El 100 % de cambios de precio conserva trazabilidad.
- **SC-003**: Ningún cambio ordinario deja el margen bajo el mínimo configurado.
- **SC-004**: Todos los cálculos monetarios usan Decimal128 y redondeo explícito.

## Assumptions
- El costo medio y precio actual provienen del núcleo 001.
- La captura competitiva inicial es manual; no se realiza scraping.
- Las promociones excepcionales se implementan en 005.
