# Data Model: Promociones inteligentes

## Tablas lógicas MongoDB
- `promotions`: name, status, discount_percent, product_ids, segment, valid_from/until, control_percent, usage_limit, actor_id.
- `promotion_audience`: promotion_id, customer_id, eligible, reason, group, consent_snapshot, assigned_at.
- `promotion_coupons`: promotion_id, customer_id, code, status, usage_limit, usage_count, valid_until.
- `promotion_redemptions`: promotion_id, coupon_id, customer_id, sale_id, discount_amount, margin_after, redeemed_at.
- `notification_outbox`: promotion_id, customer_id, channel, status, payload, created_at.

## Índices
- Audiencia única por promoción/cliente.
- Código de cupón único.
- Redención única por cupón/venta.
