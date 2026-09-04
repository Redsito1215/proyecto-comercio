# Feature Specification: Promociones inteligentes

**Feature Branch**: `005-promociones-inteligentes`  
**Created**: 2026-09-03  
**Status**: Ready for implementation

## User Stories

### US1 - Crear promoción rentable (P1)
Como gerente quiero definir audiencia, productos, vigencia y descuento validando el margen mínimo antes de activarla.

### US2 - Elegir clientes con explicación (P1)
Como responsable comercial quiero seleccionar clientes por afinidad, recurrencia y riesgo, respetando consentimiento y mostrando la razón.

### US3 - Medir efecto incremental (P2)
Como analista quiero separar tratamiento y control de forma estable para saber si la promoción causó compras adicionales.

## Functional Requirements
- **FR-001**: MUST administrar borrador, aprobación, activación, pausa y cierre.
- **FR-002**: MUST definir descuento, productos, audiencia, vigencia y límite de usos.
- **FR-003**: MUST simular margen posterior y rechazar campañas que crucen el piso.
- **FR-004**: MUST exigir consentimiento vigente para comunicaciones.
- **FR-005**: MUST explicar la elegibilidad de cada cliente.
- **FR-006**: MUST asignar tratamiento/control de forma determinista antes del envío.
- **FR-007**: MUST impedir más de una redención por cliente cuando así se configure.
- **FR-008**: MUST registrar notificación pendiente; el MVP no simula un envío real.
- **FR-009**: MUST auditar actor, estado, reglas, exclusiones y redenciones.
- **FR-010**: MUST medir conversión, ingresos, margen e incremento frente al control.
- **FR-011**: MUST evitar ofrecer recuperación cuando el cliente probablemente regresaría sin descuento mediante grupo control.

## Success Criteria
- Ninguna comunicación se programa sin consentimiento.
- Ninguna promoción ordinaria reduce el margen bajo el mínimo.
- Toda selección muestra explicación y grupo experimental.
- Toda redención respeta vigencia, estado y límite de uso.

## Assumptions
- Clientes y señales provienen de 002; márgenes de 003; ventas de 001.
- El envío externo de email/SMS queda reemplazado por una cola auditable.
