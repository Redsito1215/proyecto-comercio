"""Diagnóstico del almacén analítico que alimenta los informes compuestos."""
from backend.config import get_settings
from backend.modules.reports.warehouse import WarehouseUnavailable, get_client


def analytics_status():
    settings = get_settings()
    try:
        client = get_client()
        tables = client.query("SHOW TABLES").result_rows
        counts = {name: client.query(f"SELECT count() FROM {name}").first_row[0] for (name,) in tables}
        return {"status": "ok", "engine": "ClickHouse", "database": settings.clickhouse_database, "tables": counts}
    except WarehouseUnavailable as error:
        return {"status": "unavailable", "engine": "ClickHouse", "database": settings.clickhouse_database,
                "message": str(error)}
