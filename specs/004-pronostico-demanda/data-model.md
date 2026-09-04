# Data Model: Pronóstico de demanda

## Tablas lógicas MongoDB
- `demand_daily`: product_id, location_id, date, sold, returned, lost, available_ratio, average_price, promotion_ids.
- `forecast_runs`: cutoff_at, horizon_days, method_version, status, actor_id, created_at.
- `forecasts`: run_id, product_id, location_id, expected_units, lower_bound, upper_bound, confidence, factors, recommended_quantity.
- `forecast_accuracy`: forecast_id, actual_units, absolute_error, evaluated_at.

## Índices
- `demand_daily(product_id, location_id, date)` único.
- `forecasts(run_id, product_id, location_id)` único.
