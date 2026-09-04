# Data Model: Caja, mermas y señales

## Tablas lógicas MongoDB
- `cash_sessions`: register_id, location_id, status, opening_amount, opened_by/at, expected_balance, counted_balance, difference, closed_by/at.
- `cash_movements`: session_id, type, direction, amount, source_type/id, idempotency_key, actor_id, occurred_at.
- `cash_counts`: session_id, expected, counted, difference, reason, actor_id, counted_at.
- `loss_events`: product_id, location_id, lot_id, type, quantity, unit_cost, total_cost, reason, evidence, actor_id, occurred_at.
- `risk_alerts`: type, severity, entity_type/id, evidence, status, assigned_to, resolution, created_at/resolved_at.

## Índices
- Una sesión abierta por caja mediante índice único parcial.
- Idempotencia única para movimientos.
- Alertas por estado, severidad y fecha.
