# Feature Specification: Pronóstico de demanda

**Feature Branch**: `004-pronostico-demanda`  
**Created**: 2026-09-03  
**Status**: Completed and verified

## User Stories

### US1 - Estimar demanda explicable (P1)
Como comprador quiero un pronóstico que distinga ventas observadas de demanda no atendida y explique los factores empleados.

### US2 - Evitar sobrecompra temporal (P1)
Como gerente quiero reconocer picos provocados por promociones, variación de precio o ausencia de sustitutos para no perpetuarlos.

### US3 - Detectar demanda oculta (P2)
Como encargado quiero sumar ventas perdidas durante agotados y mostrar incertidumbre cuando faltan datos.

## Functional Requirements
- **FR-001**: MUST agregar ventas confirmadas por producto, ubicación y día.
- **FR-002**: MUST incorporar ventas perdidas y períodos sin stock como demanda censurada.
- **FR-003**: MUST conservar precio, promoción, disponibilidad y sustitutos como variables explicativas.
- **FR-004**: MUST excluir anulaciones y ajustar devoluciones.
- **FR-005**: MUST producir horizonte, valor central, intervalo y confianza.
- **FR-006**: MUST explicar los factores que elevaron o redujeron el resultado.
- **FR-007**: MUST diferenciar tendencia temporal de señal persistente.
- **FR-008**: MUST registrar versión del método, fecha y datos de corte.
- **FR-009**: MUST permitir revisión humana antes de convertir pronóstico en compra.
- **FR-010**: MUST medir error contra demanda posterior cuando esté disponible.

## Success Criteria
- **SC-001**: Cada pronóstico incluye intervalo, confianza y al menos una explicación.
- **SC-002**: Los agotados con ventas perdidas no aparecen como demanda cero.
- **SC-003**: Ningún pronóstico crea órdenes automáticamente.
- **SC-004**: El tablero permite detectar riesgo de agotado y sobrestock en menos de 15 segundos.

## Assumptions
- Los datos operativos proceden de 001, precios de 003 y promociones de 005.
- La primera versión usa un modelo determinista explicable y deja preparado el reemplazo por modelos posteriores.
