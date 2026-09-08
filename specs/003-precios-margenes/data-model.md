# Modelo de datos: Precios y márgenes

## Tablas lógicas MongoDB

### products (extendida)
`current_price Decimal128`, `average_cost Decimal128`, `minimum_margin_percent Decimal128`, `pricing_updated_at Date`.

### price_changes
`product_id ObjectId`, `old_price Decimal128`, `new_price Decimal128`, `cost_snapshot Decimal128`, `margin_percent Decimal128`, `reason String`, `actor_id String`, `effective_at Date`, `created_at Date`.

### competitor_prices
`product_id ObjectId`, `competitor String`, `channel String`, `observed_price Decimal128`, `source String`, `observed_at Date`, `actor_id String`, `created_at Date`.

## Índices
- `price_changes(product_id, effective_at desc)`.
- `competitor_prices(product_id, observed_at desc)`.

## Relaciones y reglas

- `price_changes.product_id` y `competitor_prices.product_id` referencian un producto existente.
- Precio y costo se almacenan como Decimal128; no se aceptan valores monetarios binarios.
- El margen se calcula como `(precio - costo) / precio * 100` y se redondea explícitamente.
- Una simulación no genera documentos; un cambio confirmado actualiza el producto y anexa su historial.
- La observación competitiva conserva fuente y fecha y nunca modifica el precio vigente por sí sola.

## Trazabilidad

El producto representa el estado vigente. `price_changes` constituye la bitácora comercial de solo anexado y permite conocer qué cambió, por qué, cuándo y quién lo autorizó.
