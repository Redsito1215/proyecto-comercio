# Modelo de datos: Núcleo de ventas e inventario

MongoDB implementa cada entrada como colección, pero el proyecto la denomina **tabla lógica**.
Todos los documentos incluyen `_id`, `created_at`, `updated_at` y `version` cuando admiten edición.

## Tablas lógicas

### categories

`code` único, `name`, `description`, `active`.

### products

`sku` único, `name`, `category_id`, `unit`, `barcodes[]`, `perishable`, `active`,
`name_normalized` y metadatos de versión.

### locations

`code` único, `name`, `address`, `active`.

### inventory

Clave única (`product_id`, `location_id`), `on_hand`, `reserved`, `available`, `average_cost`.
Regla: cantidades no negativas y `available = on_hand - reserved`.

### lots

`product_id`, `location_id`, `lot_number`, `received_at`, `expires_at`, `unit_cost`, `quantity`,
`available_quantity`, `status`. Único por producto, ubicación y lote.

### inventory_movements

`sequence`, `product_id`, `location_id`, `lot_id`, `type`, `quantity`, `unit_cost`,
`source_type`, `source_id`, `reason`, `actor_id`, `occurred_at`. Inmutable.

### suppliers

`code` único, `name`, `email`, `phone`, `active`.

### purchase_orders / purchase_order_items

Cabecera: `number`, `supplier_name`, `location_id`, `status`, fechas e `idempotency_key`.
Detalle: producto, cantidad pedida/recibida y costo unitario congelado.
Estados: `draft → sent → partially_received → received`. Cada recepción se materializa de
forma transaccional en lotes, inventario, movimientos y cantidades recibidas de la orden.

### sales / sale_items

Cabecera: `number`, `customer_id?`, `location_id`, `status`, importes, `actor_id`,
`idempotency_key`, fechas. Detalle: producto, cantidad, precio, descuentos, impuestos, costo
congelado y asignaciones de lote.
Estados implementados: `draft → confirmed → partially_returned`. Las devoluciones generan
documentos y movimientos compensatorios sin reescribir la venta original.

### stock_counts / stock_count_items

Cabecera con ubicación, alcance, estado y responsables. Detalle con producto/lote, cantidad
teórica, física, diferencia, motivo y aprobación.

### lost_sales

`product_id`, `requested_quantity`, `customer_id?`, `reason`, `occurred_at`, `actor_id`, contexto.

### returns / return_items

Cabecera enlazada a venta. Detalle con cantidad, condición `fit|damaged|not_received`, motivo,
reintegro y destino. La suma no supera lo vendible restante.

## Índices obligatorios

- Unicidad: códigos, SKU, barras, números de documentos e idempotencia por operación.
- Búsqueda: nombre normalizado, SKU y barras.
- Inventario: producto+ubicación; lote por caducidad y estado.
- Movimientos: producto+fecha, origen, secuencia y actor.
- Compras/ventas: estado+fecha y tercero+fecha.
- Ventas perdidas: producto+fecha.

## Retención

Movimientos y documentos confirmados no se eliminan. Los maestros se desactivan. Correcciones
financieras o de existencias producen documentos y movimientos compensatorios.
