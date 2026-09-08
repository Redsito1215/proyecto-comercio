CREATE DATABASE IF NOT EXISTS comercio_analytics;

CREATE TABLE IF NOT EXISTS comercio_analytics.sales_facts
(
    sale_id String,
    sale_number String,
    occurred_at DateTime64(3, 'UTC'),
    location_id LowCardinality(String),
    customer_id Nullable(String),
    status LowCardinality(String),
    total Decimal(18, 2),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (occurred_at, sale_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.sale_item_facts
(
    sale_id String,
    product_id String,
    sku String,
    product_name String,
    quantity UInt32,
    unit_price Decimal(18, 2),
    unit_cost Decimal(18, 2),
    line_total Decimal(18, 2),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (sale_id, product_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.inventory_snapshots
(
    captured_at DateTime64(3, 'UTC'),
    product_id String,
    location_id LowCardinality(String),
    on_hand Int64,
    available Int64,
    average_cost Decimal(18, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(captured_at)
ORDER BY (captured_at, location_id, product_id);

-- Dimensión de producto: permite agrupar los hechos por categoría y proveedor,
-- atributos que no viajan en las líneas de venta.
CREATE TABLE IF NOT EXISTS comercio_analytics.product_dim
(
    product_id String,
    sku String,
    name String,
    category LowCardinality(String),
    supplier LowCardinality(String),
    current_price Decimal(18, 2),
    average_cost Decimal(18, 2),
    minimum_margin_percent Decimal(18, 2),
    active UInt8,
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY product_id;

CREATE TABLE IF NOT EXISTS comercio_analytics.payment_facts
(
    payment_id String,
    sale_id String,
    method LowCardinality(String),
    status LowCardinality(String),
    provider LowCardinality(String),
    amount Decimal(18, 2),
    occurred_at DateTime64(3, 'UTC'),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (occurred_at, payment_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.loss_facts
(
    loss_id String,
    product_id String,
    location_id LowCardinality(String),
    loss_type LowCardinality(String),
    quantity UInt32,
    unit_cost Decimal(18, 2),
    total_cost Decimal(18, 2),
    reason String,
    occurred_at DateTime64(3, 'UTC'),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (occurred_at, loss_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.cash_session_facts
(
    session_id String,
    register_id LowCardinality(String),
    location_id LowCardinality(String),
    status LowCardinality(String),
    opening_amount Decimal(18, 2),
    expected_balance Decimal(18, 2),
    counted_balance Decimal(18, 2),
    difference Decimal(18, 2),
    opened_by String,
    closed_by String,
    opened_at DateTime64(3, 'UTC'),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (opened_at, session_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.customer_facts
(
    customer_id String,
    name String,
    segment LowCardinality(String),
    frequency UInt32,
    spend Decimal(18, 2),
    margin Decimal(18, 2),
    score Decimal(18, 2),
    churn_status LowCardinality(String),
    delay_days Int32,
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY customer_id;

CREATE TABLE IF NOT EXISTS comercio_analytics.promotion_audience_facts
(
    promotion_id String,
    promotion_name String,
    customer_id String,
    experimental_group LowCardinality(String),
    eligible UInt8,
    discount_percent Decimal(18, 2),
    valid_from DateTime64(3, 'UTC'),
    valid_until DateTime64(3, 'UTC'),
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (promotion_id, customer_id);

CREATE TABLE IF NOT EXISTS comercio_analytics.forecast_facts
(
    run_id String,
    cutoff_at DateTime64(3, 'UTC'),
    product_id String,
    sku String,
    product_name String,
    location_id LowCardinality(String),
    expected_units Int64,
    lower_bound Int64,
    upper_bound Int64,
    confidence LowCardinality(String),
    available Int64,
    recommended_quantity Int64,
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (cutoff_at, product_id, location_id);
