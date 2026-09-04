# Implementation Plan: Caja, mermas y señales de fraude

Flask, MongoDB y transacciones implementarán sesiones, movimientos, arqueos, cierres, mermas y alertas auditables. La UI conservará el diseño Altavia.

## Constitution Check
- PASS: trazabilidad, mínimo privilegio, lenguaje no acusatorio, precisión decimal, transacciones y pruebas.

## Structure
`backend/modules/controls/{schemas,risk,services,routes,indexes}.py`, `frontend/js/modules/controls/`, `tests/{unit,contract,integration}/`.
