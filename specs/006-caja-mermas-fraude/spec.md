# Especificación funcional: Caja, mermas y señales de fraude

**Rama funcional**: `006-caja-mermas-fraude`
**Creada**: 2026-09-03
**Estado**: Completada y verificada

## Historias de usuario

### US1 - Cuadrar caja durante el turno (P1)
Como supervisor quiero conocer saldo esperado y contado por sesión, realizar arqueos horarios y explicar diferencias.

**Prueba independiente**: abrir caja, registrar entradas y retiros, realizar un arqueo y cerrar verificando la diferencia calculada.

**Escenarios de aceptación**:

1. **Dada** una caja sin sesión abierta, **cuando** se abre con fondo inicial, **entonces** el saldo esperado comienza con ese importe.
2. **Dada** una sesión abierta, **cuando** se cierra, **entonces** se conservan esperado, contado, diferencia, motivo y responsable.

### US2 - Controlar mermas (P1)
Como gerente quiero registrar unidades, costo, causa y evidencia para medir cuánto margen se pierde.

**Prueba independiente**: registrar una merma con inventario suficiente y comprobar la reducción de existencias y su costo.

**Escenarios de aceptación**:

1. **Dada** una cantidad disponible, **cuando** se confirma la merma, **entonces** disminuye inventario y se crea el movimiento correspondiente.
2. **Dada** una cantidad superior al disponible, **entonces** la operación se rechaza sin cambios parciales.

### US3 - Revisar anomalías sin acusar (P2)
Como auditor quiero recibir señales por diferencias de caja repetidas con evidencia y estado de revisión.

**Prueba independiente**: producir una diferencia relevante, revisar la alerta y resolverla con una conclusión conservando la evidencia.

**Escenarios de aceptación**:

1. **Dada** una diferencia que supera el umbral, **cuando** se registra el conteo, **entonces** se crea una señal de revisión sin afirmar fraude.
2. **Dada** una alerta abierta, **cuando** se guarda una conclusión, **entonces** queda resuelta sin eliminar el historial.

### Casos límite

- Apertura duplicada de una misma caja.
- Pago en efectivo cuando no existe caja abierta en la ubicación.
- Reintento del mismo movimiento o pago.
- Merma superior al inventario disponible o lote insuficiente.
- Diferencia de caja exactamente igual al umbral configurado.

## Requisitos funcionales
- **FR-001**: MUST abrir una única sesión activa por caja con fondo inicial.
- **FR-002**: MUST registrar entradas/salidas con tipo, referencia, actor, importe y fecha.
- **FR-003**: MUST impedir duplicar movimientos asociados a la misma venta.
- **FR-004**: MUST calcular saldo esperado de forma reproducible.
- **FR-005**: MUST permitir arqueos parciales y cierre con efectivo contado.
- **FR-006**: MUST registrar diferencia monetaria y justificación.
- **FR-007**: MUST crear señales por importe y recurrencia de diferencias de caja, sin declarar fraude.
- **FR-008**: MUST registrar merma por producto, lote, cantidad, causa, costo y evidencia.
- **FR-009**: MUST descontar inventario de una merma manual confirmada.
- **FR-010**: MUST mostrar unidades y costo económico acumulado de las mermas.
- **FR-011**: MUST conservar auditoría y permitir resolver señales con comentario.
- **FR-012**: MUST separar permisos de cajero, supervisor y auditor.
- **FR-013**: MUST exigir una sesión de caja abierta para aprobar un pago en efectivo.
- **FR-014**: MUST registrar automáticamente y una sola vez el movimiento de caja de cada pago en efectivo aprobado.

## Criterios de éxito
- **SC-001**: El saldo esperado coincide exactamente con los movimientos auditados.
- **SC-002**: Todo cierre conserva conteo, diferencia y responsable.
- **SC-003**: El 100 % de alertas contiene evidencia y puede resolverse sin borrar historial.
- **SC-004**: Las mermas muestran unidades y costo económico por causa.
- **SC-005**: Un reintento del mismo pago en efectivo no duplica ni el pago ni su movimiento de caja.

## Supuestos
- En 007 se conectarán medios de pago y seguridad reforzada.
- Una alerta representa una condición para revisar, no culpabilidad.

## Fuera de alcance

- Acusar automáticamente a una persona de fraude.
- Modificar o borrar movimientos históricos para cuadrar una caja.
- Descontar inventario cuando la operación transaccional de merma falla.
