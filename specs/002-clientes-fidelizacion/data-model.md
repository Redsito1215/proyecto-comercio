# Data Model: Clientes y fidelización

## customers
`code`, `document`, `name`, `email_normalized`, `phone`, `birthday`, `status`, fechas. Índices únicos parciales para documento y email.

## customer_consents
`customer_id`, `purpose`, `channel`, `status`, `granted_at`, `revoked_at`, `source`, `actor_id`. Único vigente por cliente, propósito y canal.

## customer_metrics
`customer_id`, `purchase_count`, `last_purchase_at`, `average_interval_days`, `spend`, `gross_margin`, `stability`, `calculated_at`, `inputs_until`.

## customer_segments
`customer_id`, `segment`, `score_components`, `explanation`, `confidence`, `calculated_at`, `model_version`.

## churn_signals
`customer_id`, `expected_interval_days`, `days_since_purchase`, `delay_days`, `confidence`, `reason`, `status`, `calculated_at`.

## loyalty_events
`customer_id`, `type`, `points_delta?`, `source_type`, `source_id`, `occurred_at`, `actor_id`.

## coupons
`code`, `customer_id`, `purpose`, `discount`, `margin_floor`, `valid_from`, `valid_until`, `usage_limit`, `usage_count`, `status`.
