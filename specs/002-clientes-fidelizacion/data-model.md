# Modelo de datos: Clientes y fidelización

## customers
`code`, `document`, `name`, `email_normalized`, `phone`, `birthday`, `status`, fechas. Índices únicos parciales para documento y email.

## customer_consents
`customer_id`, `purpose`, `channel`, `status`, `granted_at`, `revoked_at`, `source`, `actor_id`. Único vigente por cliente, propósito y canal.

## customer_segments
`customer_id`, `segment`, `spend`, `margin`, `frequency`, `score`, `explanation`, `calculated_at`. Consolida el valor calculado a partir de compras confirmadas sin depender únicamente del gasto.

## churn_signals
`customer_id`, `expected_interval_days`, `days_since_purchase`, `delay_days`, `confidence`, `reason`, `status`, `calculated_at`.

## coupons
`code`, `customer_id`, `purpose`, `discount_percent`, `valid_from`, `valid_until`, `usage_limit`, `usage_count`, `status`, `created_by`.

## Relaciones y reglas

- Un cliente puede tener varios consentimientos históricos, segmentos y señales, pero solo un consentimiento vigente por propósito y canal.
- Las ventas referencian opcionalmente `customer_id`; eliminar o desactivar al cliente no reescribe ventas históricas.
- Email y documento se normalizan antes de aplicar unicidad parcial.
- Un cupón exige cliente existente, vigencia coherente y `usage_count <= usage_limit`.
- Segmentos y señales conservan fecha y explicación para reproducir la decisión mostrada.

## Ciclo de vida

El cliente puede estar activo o inactivo. El consentimiento pasa de otorgado a revocado sin borrar el registro previo; las señales se revisan mediante su estado y los cupones pasan de disponibles a agotados o vencidos según uso y fecha.
