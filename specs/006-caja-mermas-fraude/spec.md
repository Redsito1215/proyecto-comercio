# Feature Specification: Caja, mermas y señales de fraude

**Feature Branch**: `006-caja-mermas-fraude`  
**Created**: 2026-09-03  
**Status**: Ready for implementation

## User Stories

### US1 - Cuadrar caja durante el turno (P1)
Como supervisor quiero conocer saldo esperado y contado por sesión, realizar arqueos horarios y explicar diferencias.

### US2 - Controlar mermas (P1)
Como gerente quiero registrar unidades, costo, causa y evidencia para medir cuánto margen se pierde.

### US3 - Revisar anomalías sin acusar (P2)
Como auditor quiero recibir señales por diferencias repetidas, anulaciones o ajustes inusuales con evidencia y estado de revisión.

## Functional Requirements
- **FR-001**: MUST abrir una única sesión activa por caja con fondo inicial.
- **FR-002**: MUST registrar entradas/salidas con tipo, referencia, actor, importe y fecha.
- **FR-003**: MUST impedir duplicar movimientos asociados a la misma venta.
- **FR-004**: MUST calcular saldo esperado de forma reproducible.
- **FR-005**: MUST permitir arqueos parciales y cierre con efectivo contado.
- **FR-006**: MUST registrar diferencia monetaria y justificación.
- **FR-007**: MUST crear señales por umbral y recurrencia, sin declarar fraude.
- **FR-008**: MUST registrar merma por producto, lote, cantidad, causa, costo y evidencia.
- **FR-009**: MUST descontar inventario de una merma manual confirmada.
- **FR-010**: MUST mostrar impacto de mermas sobre el margen.
- **FR-011**: MUST conservar auditoría y permitir resolver señales con comentario.
- **FR-012**: MUST separar permisos de cajero, supervisor y auditor.

## Success Criteria
- El saldo esperado coincide exactamente con los movimientos auditados.
- Todo cierre conserva conteo, diferencia y responsable.
- El 100 % de alertas contiene evidencia y puede resolverse sin borrar historial.
- Las mermas muestran unidades y costo económico por causa.

## Assumptions
- En 007 se conectarán medios de pago y seguridad reforzada.
- Una alerta representa una condición para revisar, no culpabilidad.
