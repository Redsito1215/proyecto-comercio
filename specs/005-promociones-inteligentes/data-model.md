# Modelo de datos: Promociones inteligentes

## Tablas lógicas MongoDB
- `promotions`: name, status, discount_percent, product_ids, segment, valid_from/until, control_percent, usage_limit, actor_id.
- `promotion_audience`: promotion_id, customer_id, eligible, reason, group, consent_snapshot, assigned_at.
- `promotion_coupons`: promotion_id, customer_id, code, status, usage_limit, usage_count, valid_until.
- `promotion_redemptions`: promotion_id, coupon_id, customer_id, sale_id, discount_amount, actor_id, redeemed_at.
- `notification_outbox`: promotion_id, customer_id, channel, status, payload, created_at.

## Índices
- Audiencia única por promoción/cliente.
- Código de cupón único.
- Redención única por cupón/venta.

## Relaciones y reglas

- Una promoción contiene productos y genera audiencia antes de activarse.
- Solo clientes elegibles y asignados a tratamiento reciben cupón y elemento de outbox.
- El consentimiento se captura como evidencia de elegibilidad, sin reemplazar su registro original.
- El cupón respeta vigencia y límite; la redención referencia una venta y es idempotente.
- Los descuentos se validan por producto contra costo y margen mínimo.

## Ciclo de vida

La promoción avanza de `draft` a `audience_ready` y luego a `active`. La preparación de audiencia es reproducible; el grupo de control se conserva para medir resultados sin recibir comunicación ni cupón.
