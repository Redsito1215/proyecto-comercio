# Modelo de datos: Pronóstico de demanda

## Tablas lógicas MongoDB
- `forecast_runs`: `cutoff_at`, `horizon_days`, `lookback_days`, `location_id`, `method_version`, `status`, `actor_id`, `created_at`.
- `forecasts`: `run_id`, `product_id`, `location_id`, `product_name`, `sku`, `expected_units`, `lower_bound`, `upper_bound`, `confidence`, `factors`, `available`, `recommended_quantity`, `created_at`.

La serie diaria de demanda se deriva al ejecutar cada corrida a partir de `sales`,
`sale_items`, `return_items` y `lost_sales`. No se duplica como una colección operativa:
la fecha de corte, el período observado y la versión del método permiten reproducir el cálculo.

## Índices
- `forecasts(run_id, product_id, location_id)` único.
- `forecast_runs(created_at desc)` para consultar ejecuciones recientes.

## Relaciones y reglas

- Una corrida contiene muchos resultados; cada combinación corrida/producto/ubicación es única.
- Horizonte y período histórico deben ser positivos y estar dentro de los límites del esquema.
- `lower_bound <= expected_units <= upper_bound` y la cantidad recomendada nunca es negativa.
- `factors` conserva las señales contextuales utilizadas; `confidence` comunica incertidumbre.
- Los resultados anteriores no se actualizan cuando se ejecuta una nueva versión del método.

## Procedencia

Ventas, devoluciones y ventas perdidas aportan la demanda neta; inventario aporta disponibilidad, mientras precio y promociones aportan contexto. La fecha de corte impide utilizar información posterior en una corrida histórica.
