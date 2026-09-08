"""Acceso de solo lectura a ClickHouse para los informes compuestos.

Los informes compuestos no consultan MongoDB: leen las tablas de hechos que el DAG
de Airflow deja preparadas. Si el almacén no responde se levanta ``WarehouseUnavailable``
para que la ruta devuelva 503 y el usuario sepa que debe correr el ETL, en lugar de
mostrar un informe vacío que parecería un negocio sin actividad.
"""
from datetime import date, datetime
from decimal import Decimal

from backend.config import get_settings


class WarehouseUnavailable(Exception):
    pass


def get_client():
    settings = get_settings()
    try:
        import clickhouse_connect
        return clickhouse_connect.get_client(host=settings.clickhouse_host, port=settings.clickhouse_port,
                                             database=settings.clickhouse_database, connect_timeout=3,
                                             send_receive_timeout=15)
    except ImportError as error:
        raise WarehouseUnavailable("El conector de ClickHouse no está instalado en el servidor") from error
    except Exception as error:
        raise WarehouseUnavailable(f"ClickHouse no responde: {str(error)[:120]}") from error


def query_rows(sql, parameters=None):
    """Ejecuta la consulta y devuelve filas como listas, en el orden del SELECT."""
    client = get_client()
    try:
        result = client.query(sql, parameters=parameters or {})
    except Exception as error:
        raise WarehouseUnavailable(f"Consulta analítica rechazada: {str(error)[:120]}") from error
    return [[normalize(value) for value in row] for row in result.result_rows]


def normalize(value):
    if isinstance(value, (datetime, date)): return value.isoformat()[:19].replace("T", " ")
    if isinstance(value, Decimal): return str(value)
    return value
