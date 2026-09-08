"""El catálogo declara columnas y los ejecutores producen filas: si ambos se
desalinean el PDF sale con celdas corridas, así que se comprueba aquí."""
import inspect

import pytest

from backend.modules.reports.catalog import SIMPLE_BY_ID, SIMPLE_REPORTS, check_width
from backend.modules.reports.compuestos import COMPLEX_BY_ID, COMPLEX_REPORTS
from backend.modules.reports import compuestos, simple

METADATA = {"id", "name", "spec", "para_que", "quien", "permission", "columns"}


def test_every_simple_report_has_a_runner():
    assert set(SIMPLE_BY_ID) == set(simple.RUNNERS)


def test_every_complex_report_has_a_runner():
    assert set(COMPLEX_BY_ID) == set(compuestos.RUNNERS)


def test_identifiers_are_unique():
    ids = [report["id"] for report in SIMPLE_REPORTS + COMPLEX_REPORTS]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("report", SIMPLE_REPORTS + COMPLEX_REPORTS, ids=lambda r: r["id"])
def test_report_metadata_is_complete(report):
    assert METADATA <= set(report)
    assert report["columns"], "un informe sin columnas no puede renderizarse"


@pytest.mark.parametrize("report", COMPLEX_REPORTS, ids=lambda r: r["id"])
def test_complex_reports_declare_chart_and_sources(report):
    """Todo compuesto se dibuja: el frontend no renderiza gráfico si algún
    nombre del `chart` no coincide con una columna, y falla en silencio."""
    chart = report.get("chart")
    assert chart, f'{report["id"]} no declara gráfico'
    assert chart["x"] in report["columns"], f'{report["id"]}: eje x "{chart["x"]}" no es una columna'
    assert chart["series"], f'{report["id"]} no declara series'
    for series in chart["series"]:
        assert series in report["columns"], f'{report["id"]}: serie "{series}" no es una columna'
    if "group" in chart:
        assert chart["group"] in report["columns"], f'{report["id"]}: grupo "{chart["group"]}" no es una columna'
    assert len(report["source_tables"]) >= 2, "un compuesto debe cruzar al menos dos tablas"


def test_all_complex_reports_are_chartable():
    assert len([r for r in COMPLEX_REPORTS if r.get("chart")]) == len(COMPLEX_REPORTS)


@pytest.mark.parametrize("report", COMPLEX_REPORTS, ids=lambda r: r["id"])
def test_complex_query_reads_the_tables_it_declares(report):
    source = inspect.getsource(compuestos.RUNNERS[report["id"]])
    referenced = source + compuestos.SALES + compuestos.ITEMS + compuestos.DIM + compuestos.STOCK
    for table in report["source_tables"]:
        assert table in referenced, f'{report["id"]} declara {table} pero no la consulta'


def test_row_width_guard_rejects_misaligned_rows():
    report = {"id": "RC-00", "name": "x", "columns": ["a", "b"], "tipo": "compuesto", "data_layer": "clickhouse"}
    with pytest.raises(ValueError, match="RC-00"):
        check_width(report, [["solo-una-celda"]])
    assert check_width(report, [["a", "b"]]) == [["a", "b"]]
