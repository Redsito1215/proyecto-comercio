# Feature Specification: Clientes y fidelización

**Feature Branch**: `002-clientes-fidelizacion`  
**Created**: 2026-09-03  
**Status**: Ready for planning

## User Scenarios & Testing

### User Story 1 - Conocer al cliente (Priority: P1)
Como vendedor quiero registrar identidad, contacto, cumpleaños y consentimiento para reconocer al cliente y consultar su historial.

**Independent Test**: Crear un cliente, asociarlo a ventas y consultar su perfil consolidado.

**Acceptance Scenarios**:
1. **Given** datos válidos, **When** se registra, **Then** se evita duplicar email o documento.
2. **Given** ventas asociadas, **When** se abre el perfil, **Then** muestra frecuencia, última compra, gasto, margen y productos habituales.

### User Story 2 - Valorar recurrencia y rentabilidad (Priority: P1)
Como gerente quiero segmentar clientes por recurrencia, frecuencia, margen y valor para no confundir una compra grande aislada con fidelidad sostenible.

**Independent Test**: Comparar un comprador frecuente de alto margen con uno ocasional de mayor gasto y verificar la explicación del segmento.

**Acceptance Scenarios**:
1. **Given** historial suficiente, **When** se calcula valor, **Then** considera frecuencia, margen, gasto y estabilidad.
2. **Given** un segmento asignado, **When** se consulta, **Then** muestra datos, fecha y explicación.

### User Story 3 - Detectar abandono individual (Priority: P2)
Como responsable comercial quiero detectar clientes retrasados respecto de su intervalo habitual para intervenir sin asumir que 30 días significa abandono para todos.

**Independent Test**: Calcular intervalos de dos clientes con ritmos distintos y verificar alertas individualizadas.

**Acceptance Scenarios**:
1. **Given** compras repetidas, **When** supera su intervalo esperado, **Then** genera una señal con confianza y días de retraso.
2. **Given** historial insuficiente, **When** se evalúa, **Then** informa incertidumbre y no etiqueta abandono definitivo.

### User Story 4 - Fidelizar con consentimiento (Priority: P2)
Como encargado quiero emitir cupones de cumpleaños o recuperación solo a clientes con consentimiento y límites de margen.

**Independent Test**: Generar un cupón elegible, canjearlo una vez y verificar vigencia, consentimiento y trazabilidad.

**Acceptance Scenarios**:
1. **Given** cumpleaños próximo y consentimiento, **When** se ejecuta la regla, **Then** crea un cupón único y limitado.
2. **Given** un cliente sin consentimiento, **When** se evalúa, **Then** no se programa comunicación.

### Edge Cases
- Emails con mayúsculas o espacios; clientes sin email; identidades duplicadas.
- Compras devueltas o anuladas no deben inflar valor.
- Clientes nuevos sin intervalos suficientes.
- Consentimiento retirado después de crear un cupón.
- El descuento destruiría el margen mínimo.

## Requirements

### Functional Requirements
- **FR-001**: El sistema MUST administrar clientes, contactos, cumpleaños y estado.
- **FR-002**: El sistema MUST normalizar y evitar duplicados de email o documento.
- **FR-003**: El sistema MUST registrar consentimiento, canal, propósito, fecha y revocación.
- **FR-004**: Las ventas MUST poder asociarse a un cliente sin hacerlo obligatorio.
- **FR-005**: El perfil MUST mostrar historial, frecuencia, recencia, gasto, margen y productos habituales.
- **FR-006**: El valor MUST considerar recurrencia, frecuencia, gasto, margen y estabilidad.
- **FR-007**: Todo segmento MUST conservar fecha, entradas y explicación.
- **FR-008**: El abandono MUST compararse con el intervalo individual esperado.
- **FR-009**: Una señal MUST mostrar días de retraso, confianza y razón.
- **FR-010**: Historial insuficiente MUST producir incertidumbre explícita.
- **FR-011**: Los cupones MUST exigir elegibilidad, vigencia, límite de uso y margen autorizado.
- **FR-012**: Las comunicaciones MUST respetar consentimiento vigente.
- **FR-013**: La revocación MUST impedir nuevas comunicaciones.
- **FR-014**: El sistema MUST auditar cambios, segmentaciones y canjes.

### Key Entities
- Cliente, consentimiento, evento de fidelidad, segmento, señal de abandono y cupón.

## Success Criteria
- **SC-001**: Un usuario encuentra el perfil completo de un cliente en menos de 15 segundos.
- **SC-002**: El 100 % de segmentos muestra explicación y fecha de cálculo.
- **SC-003**: Ninguna comunicación se crea sin consentimiento válido.
- **SC-004**: Un cupón no puede canjearse más veces que su límite.
- **SC-005**: Las alertas usan el intervalo individual cuando existen tres o más compras.

## Assumptions
- Las ventas confirmadas de 001 son la fuente comercial.
- Márgenes y límites provienen de 003; promociones completas se amplían en 005.
- No se envía email o SMS real en la primera entrega; se registra la notificación pendiente.
