# Especificación funcional: Clientes y fidelización

**Rama funcional**: `002-clientes-fidelizacion`
**Creada**: 2026-09-03
**Estado**: Completada y verificada

## Escenarios de usuario y pruebas

### Historia de usuario 1 - Conocer al cliente (Prioridad: P1)
Como vendedor quiero registrar identidad, contacto, cumpleaños y consentimiento para reconocer al cliente y consultar su historial.

**Prueba independiente**: Crear un cliente, asociarlo a ventas y consultar su perfil consolidado.

**Escenarios de aceptación**:
1. **Given** datos válidos, **When** se registra, **Then** se evita duplicar email o documento.
2. **Given** ventas asociadas, **When** se abre el perfil, **Then** muestra segmento, frecuencia, margen, riesgo y explicación.

### Historia de usuario 2 - Valorar recurrencia y rentabilidad (Prioridad: P1)
Como gerente quiero segmentar clientes por recurrencia, frecuencia, margen y valor para no confundir una compra grande aislada con fidelidad sostenible.

**Prueba independiente**: Comparar un comprador frecuente de alto margen con uno ocasional de mayor gasto y verificar la explicación del segmento.

**Escenarios de aceptación**:
1. **Given** historial suficiente, **When** se calcula valor, **Then** considera frecuencia, margen y gasto.
2. **Given** un segmento asignado, **When** se consulta, **Then** muestra datos, fecha y explicación.

### Historia de usuario 3 - Detectar abandono individual (Prioridad: P2)
Como responsable comercial quiero detectar clientes retrasados respecto de su intervalo habitual para intervenir sin asumir que 30 días significa abandono para todos.

**Prueba independiente**: Calcular intervalos de dos clientes con ritmos distintos y verificar alertas individualizadas.

**Escenarios de aceptación**:
1. **Given** compras repetidas, **When** supera su intervalo esperado, **Then** genera una señal con confianza y días de retraso.
2. **Given** historial insuficiente, **When** se evalúa, **Then** informa incertidumbre y no etiqueta abandono definitivo.

### Historia de usuario 4 - Fidelizar con consentimiento (Prioridad: P2)
Como encargado quiero emitir cupones de cumpleaños o recuperación solo a clientes con consentimiento y límites de margen.

**Prueba independiente**: Generar un cupón elegible y verificar vigencia, consentimiento y unicidad del código.

**Escenarios de aceptación**:
1. **Given** cumpleaños próximo y consentimiento, **When** se ejecuta la regla, **Then** crea un cupón único y limitado.
2. **Given** un cliente sin consentimiento, **When** se evalúa, **Then** no se programa comunicación.

### Casos límite
- Emails con mayúsculas o espacios; clientes sin email; identidades duplicadas.
- Compras devueltas o anuladas no deben inflar valor.
- Clientes nuevos sin intervalos suficientes.
- Consentimiento retirado después de crear un cupón.
- El descuento destruiría el margen mínimo.

## Requisitos

### Requisitos funcionales
- **FR-001**: El sistema MUST administrar clientes, contactos, cumpleaños y estado.
- **FR-002**: El sistema MUST normalizar y evitar duplicados de email o documento.
- **FR-003**: El sistema MUST registrar consentimiento, canal, propósito, fecha y revocación.
- **FR-004**: Las ventas MUST poder asociarse a un cliente sin hacerlo obligatorio.
- **FR-005**: El perfil MUST mostrar segmento, frecuencia, margen acumulado, riesgo y una explicación comprensible.
- **FR-006**: El valor MUST considerar frecuencia, gasto y margen, evitando clasificar únicamente por importe comprado.
- **FR-007**: Todo segmento MUST conservar fecha de cálculo, puntuación y explicación.
- **FR-008**: El abandono MUST compararse con el intervalo individual esperado.
- **FR-009**: Una señal MUST mostrar días de retraso, confianza y razón.
- **FR-010**: Historial insuficiente MUST producir incertidumbre explícita.
- **FR-011**: Los cupones de cumpleaños MUST exigir cliente existente, consentimiento vigente, período de validez y límite de uso.
- **FR-012**: Las comunicaciones MUST respetar consentimiento vigente.
- **FR-013**: La revocación MUST impedir nuevas comunicaciones.
- **FR-014**: El sistema MUST conservar la fecha y procedencia de consentimientos, segmentos, señales y cupones emitidos.

### Entidades principales
- Cliente, consentimiento, evento de fidelidad, segmento, señal de abandono y cupón.

## Criterios de éxito
- **SC-001**: Un usuario encuentra el perfil completo de un cliente en menos de 15 segundos.
- **SC-002**: El 100 % de segmentos muestra explicación y fecha de cálculo.
- **SC-003**: Ninguna comunicación se crea sin consentimiento válido.
- **SC-004**: Un cupón no puede canjearse más veces que su límite.
- **SC-005**: Las alertas usan el intervalo individual cuando existen tres o más compras.

## Supuestos
- Las ventas confirmadas de 001 son la fuente comercial.
- Márgenes y límites provienen de 003; promociones completas se amplían en 005.
- No se envía email o SMS real en la primera entrega; se registra la notificación pendiente.

## Fuera de alcance

- El envío real mediante proveedores externos de correo electrónico, SMS o mensajería.
- La creación automática de descuentos sin consentimiento vigente ni revisión comercial.
- La captura de información personal ajena a los datos que el cliente proporcionó y autorizó.
