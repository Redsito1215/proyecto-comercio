# Especificación funcional: Promociones inteligentes

**Rama funcional**: `005-promociones-inteligentes`
**Creada**: 2026-09-03
**Estado**: Completada y verificada

## Historias de usuario

### US1 - Crear promoción rentable (P1)
Como gerente quiero definir audiencia, productos, vigencia y descuento validando el margen mínimo antes de activarla.

**Prueba independiente**: crear una promoción válida y otra que reduzca un producto por debajo de su margen mínimo.

**Escenarios de aceptación**:

1. **Dado** un descuento rentable, **cuando** se crea la promoción, **entonces** queda en borrador con productos y vigencia registrados.
2. **Dado** un descuento no rentable, **cuando** se intenta crear, **entonces** se rechaza antes de preparar la audiencia.

### US2 - Elegir clientes con explicación (P1)
Como responsable comercial quiero seleccionar clientes por afinidad, recurrencia y riesgo, respetando consentimiento y mostrando la razón.

**Prueba independiente**: preparar una audiencia con clientes elegibles, sin consentimiento y pertenecientes al grupo control.

**Escenarios de aceptación**:

1. **Dado** un cliente elegible con consentimiento, **cuando** se prepara la audiencia, **entonces** recibe grupo y explicación.
2. **Dado** un cliente sin consentimiento, **entonces** queda excluido y no recibe cupón ni notificación.

### US3 - Medir efecto incremental (P2)
Como analista quiero separar tratamiento y control de forma estable para saber si la promoción causó compras adicionales.

**Prueba independiente**: activar una campaña, registrar compras de ambos grupos y consultar conversión e ingreso comparables.

**Escenarios de aceptación**:

1. **Cuando** se repite la preparación, **entonces** un mismo cliente conserva su grupo experimental.
2. **Cuando** se consultan métricas, **entonces** tratamiento y control aparecen separados y se calcula la diferencia de conversión.

### Casos límite

- Promoción fuera de vigencia al activarse.
- Cliente que revoca consentimiento antes de preparar la audiencia.
- Cupón vencido, agotado o aplicado a una venta de otro cliente.
- Venta sin productos pertenecientes a la promoción.
- Reintento de una redención ya registrada.

## Requisitos funcionales
- **FR-001**: MUST administrar los estados borrador, audiencia preparada y promoción activa.
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

## Criterios de éxito
- **SC-001**: Ninguna comunicación se programa sin consentimiento.
- **SC-002**: Ninguna promoción ordinaria reduce el margen bajo el mínimo.
- **SC-003**: Toda selección muestra explicación y grupo experimental.
- **SC-004**: Toda redención respeta vigencia, estado y límite de uso.

## Supuestos
- Clientes y señales provienen de 002; márgenes de 003; ventas de 001.
- El envío externo de email/SMS queda reemplazado por una cola auditable.

## Fuera de alcance

- Enviar correos o SMS mediante proveedores externos.
- Elegir manualmente quién pertenece al grupo control después de asignarlo.
- Aplicar promociones que ignoren el margen mínimo del producto.
