# Implementation Plan: Promociones inteligentes

Flask y MongoDB implementarán ciclo de vida, elegibilidad, asignación determinista, cupones y medición. La interfaz reutilizará el shell Altavia.

## Constitution Check
- PASS: consentimiento, margen, explicación, experimento, auditoría y pruebas aisladas.

## Structure
`backend/modules/promotions/{schemas,eligibility,services,routes,indexes}.py`, `frontend/js/modules/promotions/`, `tests/{unit,contract,integration}/`.
