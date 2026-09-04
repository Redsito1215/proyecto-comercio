# Data Model: Núcleo de ventas e inventario

MongoDB implementa cada entrada como colección, pero el proyecto la denomina **tabla lógica**.
Todos los documentos incluyen `_id`, `created_at`, `updated_at` y `version` cuando admiten edición.

## Tablas lógicas

### categories

`code` único, `name`, `description`, `active`.

### products

`sku` único, `name`, `category_id`, `unit`, `barcodes[]` únicos, `perishable`,
`reorder_point`, `expiry_alert_days`, `active`.

### locations

`code` único, `name`, `type`, `active`.

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

`tax_id` único, `name`, `contacts`, `lead_time_days`, `active`.

### product_suppliers

Clave única (`product_id`, `supplier_id`), `supplier_sku`, `last_cost`, `minimum_order`,
`pack_size`, `preferred`, `active`.

### purchase_orders / purchase_order_items

Cabecera: `number`, `supplier_id`, `status`, fechas, moneda, totales, `idempotency_key`.
Detalle: producto, cantidad pedida/recibida, costo y descuentos congelados.
Estados: `draft → sent → partially_received → received`; `draft|sent → cancelled`.

### purchase_receipts

`number`, `purchase_order_id`, `items[]` con producto, lote, caducidad, cantidad y costo,
`received_by`, `received_at`, `idempotency_key`.

### sales / sale_items

Cabecera: `number`, `customer_id?`, `location_id`, `status`, importes, `actor_id`,
`idempotency_key`, fechas. Detalle: producto, cantidad, precio, descuentos, impuestos, costo
congelado y asignaciones de lote.
Estados: `draft → confirmed → partially_returned → returned`; `draft|confirmed → cancelled`
según autorización y efectos compensatorios.

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
