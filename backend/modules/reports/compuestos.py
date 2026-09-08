"""Catálogo y ejecución de los informes compuestos RC-01…RC-12.

Un informe compuesto agrega y cruza al menos dos tablas de hechos de ClickHouse
que el DAG de Airflow deja preparadas. Se diferencia de un informe simple en tres
cosas: agrupa (no lista), cruza fuentes, y declara un ``chart`` para que el
frontend sepa representarlo.

Las tablas de hechos son ``ReplacingMergeTree``, así que toda lectura pasa por un
CTE con ``FINAL`` para no contar dos veces una fila recargada por el ETL.
"""
from backend.modules.reports.catalog import check_width
from backend.modules.reports.warehouse import query_rows

COMPLEX_REPORTS = [
    {
        "id": "RC-01",
        "name": "Ventas por mes y ubicación",
        "spec": "001-core-ventas-inventario",
        "para_que": "Ver la evolución del ingreso y del ticket promedio en cada punto de venta.",
        "quien": "Gerencia, analista",
        "permission": "sales.read",
        "source_tables": ["sales_facts", "sale_item_facts"],
        "columns": ["Mes", "Ubicación", "Ventas", "Unidades", "Ingresos", "Ticket promedio"],
        "chart": {"type": "line", "x": "Mes", "series": ["Ingresos"], "group": "Ubicación"},
    },
    {
        "id": "RC-02",
        "name": "Productos líderes y rezagados frente a existencias",
        "spec": "001-core-ventas-inventario",
        "para_que": "Detectar qué se vende y qué no, contrastándolo con el stock inmovilizado.",
        "quien": "Gerencia comercial, comprador",
        "permission": "sales.read",
        "source_tables": ["sale_item_facts", "sales_facts", "inventory_snapshots", "product_dim"],
        "columns": ["Grupo", "SKU", "Producto", "Categoría", "Unidades", "Ingresos", "Existencias"],
        "chart": {"type": "bar", "x": "Producto", "series": ["Ingresos"], "group": "Grupo"},
    },
    {
        "id": "RC-03",
        "name": "Margen por categoría en el tiempo",
        "spec": "003-precios-margenes",
        "para_que": "Comparar ingreso, costo y margen por categoría mes a mes.",
        "quien": "Gerencia, analista",
        "permission": "products.read",
        "source_tables": ["sale_item_facts", "sales_facts", "product_dim"],
        "columns": ["Mes", "Categoría", "Ingresos", "Costos", "Utilidad", "Margen %"],
        "chart": {"type": "line", "x": "Mes", "series": ["Margen %"], "group": "Categoría"},
    },
    {
        "id": "RC-04",
        "name": "Rotación y cobertura de inventario por categoría",
        "spec": "001-core-ventas-inventario",
        "para_que": "Relacionar lo vendido con lo disponible para anticipar quiebres y sobrestock.",
        "quien": "Responsable de almacén, comprador",
        "permission": "inventory.read",
        "source_tables": ["sale_item_facts", "sales_facts", "inventory_snapshots", "product_dim"],
        "columns": ["Categoría", "Unidades vendidas", "Existencias", "Rotación", "Días de cobertura", "Valor inventario"],
        "chart": {"type": "bar", "x": "Categoría", "series": ["Unidades vendidas", "Existencias"]},
    },
    {
        "id": "RC-05",
        "name": "Composición del ticket por ubicación",
        "spec": "001-core-ventas-inventario",
        "para_que": "Comparar cuántos artículos y cuánto dinero entra por venta en cada local.",
        "quien": "Gerencia comercial",
        "permission": "sales.read",
        "source_tables": ["sales_facts", "sale_item_facts"],
        "columns": ["Ubicación", "Ventas", "Unidades", "Ingresos", "Ticket promedio", "Ítems por venta", "Referencias"],
        "chart": {"type": "bar", "x": "Ubicación", "series": ["Ticket promedio"]},
    },
    {
        "id": "RC-06",
        "name": "Estado de la carga analítica",
        "spec": "001-core-ventas-inventario",
        "para_que": "Comprobar que el ETL llenó cada tabla antes de confiar en los demás compuestos.",
        "quien": "Administrador, analista",
        "permission": "reports.read",
        "source_tables": ["sales_facts", "sale_item_facts", "inventory_snapshots", "product_dim",
                          "payment_facts", "loss_facts", "cash_session_facts", "customer_facts",
                          "promotion_audience_facts", "forecast_facts"],
        "columns": ["Tabla", "Filas", "Última carga", "Estado"],
        "chart": {"type": "status", "x": "Tabla", "series": ["Filas"]},
    },
    {
        "id": "RC-07",
        "name": "Mix y aprobación por medio de pago",
        "spec": "007-pagos-seguridad",
        "para_que": "Ver qué medios concentran el cobro y cuáles fallan más al autorizar.",
        "quien": "Gerencia comercial, cajero",
        "permission": "payments.read",
        "source_tables": ["payment_facts", "sales_facts"],
        "columns": ["Medio", "Proveedor", "Intentos", "Aprobados", "Tasa aprobación %", "Importe aprobado", "Ticket promedio"],
        "chart": {"type": "bar", "x": "Medio", "series": ["Importe aprobado"]},
    },
    {
        "id": "RC-08",
        "name": "Mermas frente a ventas por categoría",
        "spec": "006-caja-mermas-fraude",
        "para_que": "Medir cuánto margen se pierde en cada categoría respecto de lo que factura.",
        "quien": "Gerencia, responsable de almacén",
        "permission": "inventory.read",
        "source_tables": ["loss_facts", "sale_item_facts", "sales_facts", "product_dim"],
        "columns": ["Categoría", "Unidades vendidas", "Ingresos", "Unidades perdidas", "Costo mermas", "Merma sobre ingresos %"],
        "chart": {"type": "bar", "x": "Categoría", "series": ["Costo mermas"]},
    },
    {
        "id": "RC-09",
        "name": "Descuadres de caja por turno y responsable",
        "spec": "006-caja-mermas-fraude",
        "para_que": "Comparar el descuadre acumulado de cada responsable con el ingreso de su local.",
        "quien": "Supervisor de caja, auditor",
        "permission": "payments.read",
        "source_tables": ["cash_session_facts", "sales_facts"],
        "columns": ["Caja", "Responsable", "Ubicación", "Sesiones", "Cerradas", "Descuadre absoluto",
                    "Diferencia promedio", "Ingresos de la ubicación"],
        "chart": {"type": "bar", "x": "Responsable", "series": ["Descuadre absoluto"]},
    },
    {
        "id": "RC-10",
        "name": "Valor y recurrencia por segmento de cliente",
        "spec": "002-clientes-fidelizacion",
        "para_que": "Saber qué segmentos sostienen el ingreso y cuántos clientes están en riesgo.",
        "quien": "Gerencia comercial, analista",
        "permission": "customers.read",
        "source_tables": ["customer_facts", "sales_facts"],
        "columns": ["Segmento", "Clientes", "Frecuencia media", "Ingresos del periodo",
                    "Ingreso por cliente", "En riesgo", "Score medio"],
        "chart": {"type": "bar", "x": "Segmento", "series": ["Ingresos del periodo"]},
    },
    {
        "id": "RC-11",
        "name": "Efecto incremental de promociones",
        "spec": "005-promociones-inteligentes",
        "para_que": "Comparar conversión e ingreso entre tratamiento y control para saber si la campaña causó compras.",
        "quien": "Analista, gerencia comercial",
        "permission": "products.read",
        "source_tables": ["promotion_audience_facts", "sales_facts"],
        "columns": ["Promoción", "Grupo", "Clientes", "Compradores", "Conversión %", "Ingresos", "Ticket promedio"],
        "chart": {"type": "bar", "x": "Promoción", "series": ["Conversión %"], "group": "Grupo"},
    },
    {
        "id": "RC-12",
        "name": "Pronóstico frente a venta real",
        "spec": "004-pronostico-demanda",
        "para_que": "Verificar si la demanda observada cayó dentro del intervalo que se pronosticó.",
        "quien": "Comprador, analista",
        "permission": "inventory.read",
        "source_tables": ["forecast_facts", "sale_item_facts", "sales_facts"],
        "columns": ["SKU", "Producto", "Esperado", "Intervalo", "Confianza", "Vendido real", "Desviación", "Resultado"],
        "chart": {"type": "bar", "x": "Producto", "series": ["Esperado", "Vendido real"]},
    },
]

COMPLEX_BY_ID = {report["id"]: report for report in COMPLEX_REPORTS}

# CTEs reutilizados: consolidan las tablas ReplacingMergeTree antes de cruzarlas.
SALES = "ventas AS (SELECT * FROM sales_facts FINAL)"
ITEMS = "lineas AS (SELECT * FROM sale_item_facts FINAL)"
DIM = "dim AS (SELECT * FROM product_dim FINAL)"
STOCK = ("stock AS (SELECT product_id, argMax(available, captured_at) available, "
         "argMax(average_cost, captured_at) average_cost FROM inventory_snapshots GROUP BY product_id)")

# Un LEFT JOIN contra product_dim rellena con cadena vacía los productos que la
# dimensión todavía no tiene cargados. Etiquetarlos evita una fila en blanco que
# parece un error de la tabla en vez de un hueco del ETL.
CATEGORY = "if(empty(d.category), 'sin catálogo', d.category)"


def period(column, params):
    """Cláusula de rango sobre una columna de fecha, lista para concatenar tras un WHERE."""
    clauses, values = [], {}
    if params.date_from:
        clauses.append(f"AND toDate({column}) >= {{date_from:Date}}")
        values["date_from"] = params.date_from
    if params.date_to:
        clauses.append(f"AND toDate({column}) <= {{date_to:Date}}")
        values["date_to"] = params.date_to
    return " ".join(clauses), values


def rc01(params):
    where, values = period("v.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, {ITEMS}
        SELECT formatDateTime(toStartOfMonth(v.occurred_at), '%Y-%m') mes,
               v.location_id ubicacion,
               uniqExact(v.sale_id) ventas,
               sum(l.quantity) unidades,
               round(sum(l.line_total), 2) ingresos,
               round(sum(l.line_total) / uniqExact(v.sale_id), 2) ticket_promedio
        FROM ventas v INNER JOIN lineas l ON l.sale_id = v.sale_id
        WHERE 1 {where}
        GROUP BY mes, ubicacion ORDER BY mes, ingresos DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc02(params):
    where, values = period("v.occurred_at", params)
    half = max(params.limit // 2, 5)
    return query_rows(f"""
        WITH {SALES}, {ITEMS}, {DIM}, {STOCK},
        totales AS (
            SELECT l.product_id product_id, any(l.sku) sku, any(l.product_name) nombre,
                   sum(l.quantity) unidades, round(sum(l.line_total), 2) ingresos
            FROM lineas l INNER JOIN ventas v ON v.sale_id = l.sale_id
            WHERE 1 {where} GROUP BY l.product_id
        ),
        ordenados AS (
            SELECT *, row_number() OVER (ORDER BY ingresos DESC) rk_top,
                      row_number() OVER (ORDER BY ingresos ASC) rk_bottom
            FROM totales
        )
        SELECT if(o.rk_top <= {{half:UInt32}}, 'líder', 'rezagado') grupo,
               o.sku, o.nombre, {CATEGORY} categoria, o.unidades, o.ingresos, s.available existencias
        FROM ordenados o
        LEFT JOIN dim d ON d.product_id = o.product_id
        LEFT JOIN stock s ON s.product_id = o.product_id
        WHERE o.rk_top <= {{half:UInt32}} OR o.rk_bottom <= {{half:UInt32}}
        ORDER BY o.ingresos DESC LIMIT {{limit:UInt32}}
    """, {**values, "half": half, "limit": params.limit})


def rc03(params):
    where, values = period("v.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, {ITEMS}, {DIM}
        SELECT formatDateTime(toStartOfMonth(v.occurred_at), '%Y-%m') mes,
               {CATEGORY} categoria,
               round(sum(l.line_total), 2) ingresos,
               round(sum(l.unit_cost * l.quantity), 2) costos,
               round(sum(l.line_total) - sum(l.unit_cost * l.quantity), 2) utilidad,
               round((sum(l.line_total) - sum(l.unit_cost * l.quantity)) / nullIf(sum(l.line_total), 0) * 100, 2) margen_pct
        FROM lineas l
        INNER JOIN ventas v ON v.sale_id = l.sale_id
        LEFT JOIN dim d ON d.product_id = l.product_id
        WHERE 1 {where}
        GROUP BY mes, categoria ORDER BY mes, utilidad DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc04(params):
    where, values = period("v.occurred_at", params)
    # La cobertura divide las existencias entre la venta diaria, así que la ventana
    # debe coincidir con el periodo realmente consultado. Sin filtro de fechas se
    # suma todo el historial: usar 30 días fijos inflaría la tasa diaria y haría
    # parecer que el stock se agota en horas.
    explicit = bool(params.date_from and params.date_to)
    span = "{ventana:UInt32}" if explicit else \
        "(SELECT greatest(dateDiff('day', min(occurred_at), max(occurred_at)) + 1, 1) FROM ventas)"
    if explicit: values["ventana"] = params.window_days
    return query_rows(f"""
        WITH {SALES}, {ITEMS}, {DIM}, {STOCK},
        vendido AS (
            SELECT l.product_id product_id, sum(l.quantity) unidades
            FROM lineas l INNER JOIN ventas v ON v.sale_id = l.sale_id
            WHERE 1 {where} GROUP BY l.product_id
        )
        SELECT {CATEGORY} categoria,
               sum(w.unidades) unidades_vendidas,
               sum(s.available) existencias,
               round(sum(w.unidades) / nullIf(sum(s.available), 0), 2) rotacion,
               round(sum(s.available) / nullIf(sum(w.unidades) / {span}, 0), 1) dias_cobertura,
               round(sum(s.available * s.average_cost), 2) valor_inventario
        FROM stock s
        LEFT JOIN vendido w ON w.product_id = s.product_id
        LEFT JOIN dim d ON d.product_id = s.product_id
        GROUP BY categoria ORDER BY unidades_vendidas DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc05(params):
    where, values = period("v.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, {ITEMS}
        SELECT v.location_id ubicacion,
               uniqExact(v.sale_id) ventas,
               sum(l.quantity) unidades,
               round(sum(l.line_total), 2) ingresos,
               round(sum(l.line_total) / uniqExact(v.sale_id), 2) ticket_promedio,
               round(sum(l.quantity) / uniqExact(v.sale_id), 2) items_por_venta,
               uniqExact(l.product_id) referencias
        FROM lineas l INNER JOIN ventas v ON v.sale_id = l.sale_id
        WHERE 1 {where}
        GROUP BY ubicacion ORDER BY ingresos DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc06(_params):
    tables = ["sales_facts", "sale_item_facts", "inventory_snapshots", "product_dim", "payment_facts",
              "loss_facts", "cash_session_facts", "customer_facts", "promotion_audience_facts", "forecast_facts"]
    # inventory_snapshots es MergeTree y su marca temporal es captured_at, no loaded_at.
    stamp = {"inventory_snapshots": "captured_at"}
    parts = [f"SELECT {index} orden, '{table}' tabla, count() filas, "
             f"toString(max({stamp.get(table, 'loaded_at')})) ultima_carga, "
             f"if(count() > 0, 'cargada', 'vacía') estado FROM {table}"
             for index, table in enumerate(tables)]
    return query_rows(f"SELECT tabla, filas, ultima_carga, estado FROM ({' UNION ALL '.join(parts)}) ORDER BY orden")


def rc07(params):
    where, values = period("p.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, pagos AS (SELECT * FROM payment_facts FINAL)
        SELECT p.method medio,
               any(p.provider) proveedor,
               count() intentos,
               countIf(p.status = 'approved') aprobados,
               round(countIf(p.status = 'approved') / count() * 100, 2) tasa_aprobacion_pct,
               round(sumIf(p.amount, p.status = 'approved'), 2) importe_aprobado,
               round(sumIf(p.amount, p.status = 'approved') / nullIf(uniqExactIf(p.sale_id, p.status = 'approved'), 0), 2) ticket_promedio
        FROM pagos p INNER JOIN ventas v ON v.sale_id = p.sale_id
        WHERE 1 {where}
        GROUP BY medio ORDER BY importe_aprobado DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc08(params):
    sales_where, values = period("v.occurred_at", params)
    loss_where, _ = period("m.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, {ITEMS}, {DIM}, mermas AS (SELECT * FROM loss_facts FINAL),
        vendido AS (
            SELECT l.product_id product_id, sum(l.quantity) unidades, sum(l.line_total) ingresos
            FROM lineas l INNER JOIN ventas v ON v.sale_id = l.sale_id
            WHERE 1 {sales_where} GROUP BY l.product_id
        ),
        perdido AS (
            SELECT m.product_id product_id, sum(m.quantity) unidades, sum(m.total_cost) costo
            FROM mermas m WHERE 1 {loss_where} GROUP BY m.product_id
        )
        SELECT {CATEGORY} categoria,
               sum(w.unidades) unidades_vendidas,
               round(sum(w.ingresos), 2) ingresos,
               sum(p.unidades) unidades_perdidas,
               round(sum(p.costo), 2) costo_mermas,
               round(sum(p.costo) / nullIf(sum(w.ingresos), 0) * 100, 2) merma_sobre_ingresos_pct
        FROM dim d
        LEFT JOIN vendido w ON w.product_id = d.product_id
        LEFT JOIN perdido p ON p.product_id = d.product_id
        GROUP BY categoria
        HAVING unidades_vendidas > 0 OR unidades_perdidas > 0
        ORDER BY costo_mermas DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc09(params):
    session_where, values = period("c.opened_at", params)
    sales_where, _ = period("v.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, cajas AS (SELECT * FROM cash_session_facts FINAL),
        ingresos_ubicacion AS (
            SELECT v.location_id location_id, round(sum(v.total), 2) ingresos
            FROM ventas v WHERE 1 {sales_where} GROUP BY v.location_id
        )
        SELECT c.register_id caja,
               c.opened_by responsable,
               c.location_id ubicacion,
               count() sesiones,
               countIf(c.status = 'closed') cerradas,
               round(sum(abs(c.difference)), 2) descuadre_absoluto,
               round(avg(c.difference), 2) diferencia_promedio,
               any(i.ingresos) ingresos_ubicacion
        FROM cajas c LEFT JOIN ingresos_ubicacion i ON i.location_id = c.location_id
        WHERE 1 {session_where}
        GROUP BY caja, responsable, ubicacion
        ORDER BY descuadre_absoluto DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc10(params):
    where, values = period("v.occurred_at", params)
    return query_rows(f"""
        WITH {SALES}, clientes AS (SELECT * FROM customer_facts FINAL),
        compras AS (
            -- sales_facts.customer_id es Nullable(String) y customer_facts lo tiene
            -- como String: se normaliza antes de cruzar para evitar el choque de tipos.
            SELECT assumeNotNull(v.customer_id) customer_id, round(sum(v.total), 2) ingresos
            FROM ventas v WHERE v.customer_id IS NOT NULL {where} GROUP BY v.customer_id
        )
        SELECT c.segment segmento,
               count() clientes,
               round(avg(c.frequency), 2) frecuencia_media,
               round(sum(p.ingresos), 2) ingresos_periodo,
               round(sum(p.ingresos) / nullIf(count(), 0), 2) ingreso_por_cliente,
               countIf(c.churn_status = 'at_risk') en_riesgo,
               round(avg(c.score), 2) score_medio
        FROM clientes c LEFT JOIN compras p ON p.customer_id = c.customer_id
        GROUP BY segmento ORDER BY ingresos_periodo DESC LIMIT {{limit:UInt32}}
    """, {**values, "limit": params.limit})


def rc11(params):
    return query_rows(f"""
        WITH audiencia AS (SELECT * FROM promotion_audience_facts FINAL WHERE eligible = 1),
        ventas AS (SELECT assumeNotNull(customer_id) customer_id, sale_id, occurred_at, total
                   FROM sales_facts FINAL WHERE customer_id IS NOT NULL),
        por_cliente AS (
            SELECT a.promotion_name promocion, a.experimental_group grupo, a.customer_id customer_id,
                   uniqExactIf(v.sale_id, v.occurred_at BETWEEN a.valid_from AND a.valid_until) ventas,
                   sumIf(v.total, v.occurred_at BETWEEN a.valid_from AND a.valid_until) ingresos
            FROM audiencia a LEFT JOIN ventas v ON v.customer_id = a.customer_id
            GROUP BY promocion, grupo, customer_id
        )
        SELECT promocion, grupo,
               count() clientes,
               countIf(ventas > 0) compradores,
               round(countIf(ventas > 0) / count() * 100, 2) conversion_pct,
               round(sum(ingresos), 2) ingresos,
               round(sum(ingresos) / nullIf(countIf(ventas > 0), 0), 2) ticket_promedio
        FROM por_cliente
        GROUP BY promocion, grupo ORDER BY promocion, grupo LIMIT {{limit:UInt32}}
    """, {"limit": params.limit})


def rc12(params):
    return query_rows(f"""
        WITH {SALES}, {ITEMS}, pronostico AS (SELECT * FROM forecast_facts FINAL),
        corte AS (SELECT max(cutoff_at) cutoff FROM pronostico),
        plan AS (
            SELECT f.product_id product_id, any(f.sku) sku, any(f.product_name) nombre,
                   sum(f.expected_units) esperado, sum(f.lower_bound) minimo, sum(f.upper_bound) maximo,
                   any(f.confidence) confianza
            FROM pronostico f WHERE f.cutoff_at = (SELECT cutoff FROM corte) GROUP BY f.product_id
        ),
        observado AS (
            SELECT l.product_id product_id, sum(l.quantity) vendido
            FROM lineas l INNER JOIN ventas v ON v.sale_id = l.sale_id
            WHERE v.occurred_at >= (SELECT cutoff FROM corte) GROUP BY l.product_id
        )
        SELECT p.sku, p.nombre, p.esperado,
               concat(toString(p.minimo), ' - ', toString(p.maximo)) intervalo,
               p.confianza, o.vendido vendido_real,
               o.vendido - p.esperado desviacion,
               if(o.vendido BETWEEN p.minimo AND p.maximo, 'dentro del intervalo', 'fuera del intervalo') resultado
        FROM plan p LEFT JOIN observado o ON o.product_id = p.product_id
        ORDER BY abs(desviacion) DESC LIMIT {{limit:UInt32}}
    """, {"limit": params.limit})


RUNNERS = {"RC-01": rc01, "RC-02": rc02, "RC-03": rc03, "RC-04": rc04, "RC-05": rc05, "RC-06": rc06,
           "RC-07": rc07, "RC-08": rc08, "RC-09": rc09, "RC-10": rc10, "RC-11": rc11, "RC-12": rc12}


def describe(report):
    return {**report, "tipo": "compuesto", "data_layer": "clickhouse"}


def run_complex(report_id, params):
    report = describe(COMPLEX_BY_ID[report_id])
    rows = check_width(report, RUNNERS[report_id](params))
    return {"report": report, "rows": rows, "total": len(rows)}
