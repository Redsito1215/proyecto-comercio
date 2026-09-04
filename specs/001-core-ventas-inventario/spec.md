# Feature Specification: Núcleo de ventas e inventario

**Feature Branch**: `001-core-ventas-inventario`
**Created**: 2026-09-03
**Status**: Ready for planning
**Input**: Venta rápida, inventario digital, compras, lotes, caducidad, agotados y ventas perdidas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cobrar una venta rápidamente (Priority: P1)

Como cajero quiero localizar productos, preparar una venta y confirmarla con pocos pasos para
atender al cliente sin demoras y descontar la mercancía correcta.

**Why this priority**: La venta genera ingresos y alimenta los demás módulos.

**Independent Test**: Registrar una venta de dos productos y comprobar que queda identificada y
las existencias disminuyen exactamente una vez.

**Acceptance Scenarios**:

1. **Given** productos activos con existencias, **When** se buscan por nombre, código o barras,
   **Then** aparecen con precio y disponibilidad vigentes.
2. **Given** una venta preparada, **When** se confirma, **Then** recibe un número único, congela
   sus líneas y descuenta existencias atómicamente.
3. **Given** una confirmación reintentada, **When** llega la misma solicitud, **Then** no duplica
   la venta ni el descuento.
4. **Given** cantidad insuficiente, **When** se confirma, **Then** se rechaza antes del cobro.

---

### User Story 2 - Controlar inventario por lote (Priority: P1)

Como responsable de almacén quiero conocer existencias, lotes, caducidades y movimientos para
detectar faltantes y productos próximos a vencer.

**Why this priority**: Sin existencias confiables no se puede vender ni pronosticar.

**Independent Test**: Recibir dos lotes, vender unidades y verificar cantidades, trazabilidad y
salida priorizada por caducidad.

**Acceptance Scenarios**:

1. **Given** una recepción con lote, **When** se confirma, **Then** aumenta la existencia y se
   registra un movimiento enlazado con su origen.
2. **Given** varios lotes, **When** se vende un perecedero, **Then** se consume primero el lote
   utilizable con vencimiento más cercano.
3. **Given** un lote próximo a caducar, **When** alcanza el umbral, **Then** se alerta con unidades
   y valor económico expuesto.

---

### User Story 3 - Reponer sin inmovilizar dinero (Priority: P2)

Como comprador quiero crear órdenes basadas en necesidad, rotación y cobertura para evitar
agotamientos y compras excesivas motivadas solo por un precio barato.

**Why this priority**: La reposición equilibra disponibilidad y capital inmovilizado.

**Independent Test**: Crear, enviar y recibir parcialmente una orden y comprobar cantidades
recibidas, pendientes, lotes e inventario.

**Acceptance Scenarios**:

1. **Given** productos bajo reposición, **When** se prepara una orden, **Then** se muestran
   existencia, cobertura, costo y plazo del proveedor.
2. **Given** una recepción parcial, **When** se confirma, **Then** solo ingresa lo recibido y el
   saldo queda pendiente.
3. **Given** una oferta superior a la necesidad, **When** se evalúa, **Then** se advierte capital
   y días de inventario excedentes.

---

### User Story 4 - Cuadrar existencias y demanda no atendida (Priority: P2)

Como supervisor quiero contar inventario, ajustar diferencias justificadas y registrar productos
solicitados sin stock para mantener datos útiles y trazables.

**Why this priority**: El inventario incorrecto distorsiona finanzas y demanda.

**Independent Test**: Registrar un conteo con diferencia, aprobarlo y verificar el movimiento
compensatorio; registrar además una venta perdida.

**Acceptance Scenarios**:

1. **Given** un conteo abierto, **When** se registra cantidad física, **Then** conserva la teórica.
2. **Given** una diferencia, **When** se aprueba, **Then** crea un ajuste sin reescribir historial.
3. **Given** un producto agotado solicitado, **When** se registra, **Then** conserva producto,
   cantidad, fecha y contexto.

---

### User Story 5 - Gestionar devoluciones trazables (Priority: P3)

Como supervisor quiero registrar devoluciones parciales y clasificar la mercancía para reintegrar
solo lo apto y reconocer la merma dañada.

**Why this priority**: La devolución afecta venta, inventario, pago y caja.

**Independent Test**: Devolver parte de una venta, separar apto y dañado y verificar sus destinos.

**Acceptance Scenarios**:

1. **Given** una venta confirmada, **When** se devuelve, **Then** no supera la cantidad disponible
   para devolución.
2. **Given** mercancía apta y dañada, **When** se confirma, **Then** solo lo apto vuelve a stock.

### Edge Cases

- Dos cajeros intentan vender la última unidad simultáneamente.
- El precio cambia mientras la venta está abierta.
- Una recepción se reintenta tras perder conexión.
- Un lote está vencido, bloqueado o retirado.
- Un conteo permanece abierto mientras ocurren movimientos.
- Se intenta devolver una venta anulada o fuera de plazo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST administrar categorías, productos, unidades, códigos y estado.
- **FR-002**: El sistema MUST localizar productos por nombre, código o código de barras único.
- **FR-003**: El sistema MUST mostrar precio y disponibilidad vigentes antes de vender.
- **FR-004**: Cada venta MUST conservar número único, responsable, estado, líneas y totales.
- **FR-005**: Confirmar una venta MUST ser atómico e idempotente.
- **FR-006**: El sistema MUST impedir stock negativo salvo ajuste autorizado.
- **FR-007**: El sistema MUST mantener stock por producto y ubicación.
- **FR-008**: Cada cambio MUST generar un movimiento inmutable con origen y responsable.
- **FR-009**: Los perecederos MUST gestionarse por lote y caducidad.
- **FR-010**: La salida MUST priorizar el lote utilizable que venza primero.
- **FR-011**: El sistema MUST alertar stock bajo, agotamiento y caducidad próxima.
- **FR-012**: Las alertas MUST incluir cantidad, valor económico y acción sugerida.
- **FR-013**: El sistema MUST administrar proveedores y productos suministrados.
- **FR-014**: Las órdenes MUST admitir borrador, envío, recepción parcial, cierre y cancelación.
- **FR-015**: Cada recepción MUST actualizar orden, lotes, stock y movimientos atómicamente.
- **FR-016**: El sistema MUST mostrar cobertura y capital excedente al evaluar compras.
- **FR-017**: El sistema MUST permitir conteos totales y parciales.
- **FR-018**: Todo ajuste MUST exigir motivo, autorización y movimiento compensatorio.
- **FR-019**: El sistema MUST registrar ventas perdidas por falta de stock.
- **FR-020**: Las devoluciones MUST limitarse por venta y devoluciones anteriores.
- **FR-021**: Solo mercancía apta MUST reingresar al inventario.
- **FR-022**: Los maestros desactivados MUST conservar su historial consultable.
- **FR-023**: Las operaciones sensibles MUST registrarse en auditoría.
- **FR-024**: El acceso MUST depender del rol y autorización vigente.

### Key Entities *(include if feature involves data)*

- **Producto**: Artículo vendible con códigos, unidad, categoría y estado.
- **Ubicación y existencia**: Cantidades disponibles y reservadas por producto.
- **Lote**: Unidades con origen, costo y posible caducidad.
- **Movimiento de inventario**: Evidencia inmutable de entradas, salidas y ajustes.
- **Venta y detalle**: Documento comercial y artículos con valores congelados.
- **Proveedor, orden y recepción**: Abastecimiento, compromiso y entregas.
- **Conteo**: Comparación entre existencia teórica y física.
- **Venta perdida**: Demanda observada que no pudo atenderse.
- **Devolución**: Reversión con inspección y destino de mercancía.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un cajero completa una venta de cinco productos en menos de 60 segundos.
- **SC-002**: El 100 % de ventas produce exactamente un descuento conciliable de inventario.
- **SC-003**: Ningún reintento crea ventas, recepciones o movimientos duplicados.
- **SC-004**: Cada ajuste conserva responsable, motivo y movimiento compensatorio.
- **SC-005**: Un responsable identifica agotados y caducidades en menos de 30 segundos.
- **SC-006**: Todas las recepciones parciales mantienen cantidades pendientes conciliadas.
- **SC-007**: Todas las ventas perdidas quedan disponibles para analizar demanda.

## Assumptions

- El comercio inicia con una ubicación, pero admite varias.
- Pagos y caja pertenecen a las especificaciones 007 y 006.
- Precios y márgenes se gobiernan en 003; la venta guarda su copia histórica.
- Los umbrales de stock y caducidad son configurables.
- Ninguna recomendación confirma compras o ajustes sin autorización humana.
