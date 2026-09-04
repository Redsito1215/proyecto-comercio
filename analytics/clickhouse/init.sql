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
