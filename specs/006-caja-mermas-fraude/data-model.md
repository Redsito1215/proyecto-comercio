# Modelo de datos: Caja, mermas y señales

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

## Relaciones y reglas

- Cada movimiento y arqueo pertenece a una sesión existente.
- El saldo esperado se deriva del fondo y movimientos; no es un valor libremente editable.
- Un cierre exige sesión abierta y conserva contado, diferencia, fecha y responsable.
- Una merma referencia producto, ubicación y opcionalmente lote, y reduce inventario en la misma transacción.
- Una alerta conserva evidencia y puede resolverse, pero no se elimina ni constituye una acusación.

## Ciclo de vida

La sesión pasa de abierta a cerrada. Las alertas pasan de abiertas a resueltas con conclusión y actor. Las correcciones contables se representan mediante nuevos movimientos compensatorios.
